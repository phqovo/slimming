from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.user import User
from app.models.food import FoodNutrition
from app.schemas.food import FoodNutritionResponse, FoodNutritionCreate, FoodNutritionUpdate
from app.api.deps import get_current_user
from app.utils.storage import upload_file
import httpx
import requests
from bs4 import BeautifulSoup
import re
from decimal import Decimal
import urllib3

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

router = APIRouter()


# 在线搜索喵喵食物网
@router.get("/search", summary="搜索食物(喵喵食物网)")
async def search_food_online(
    keyword: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    搜索食物热量信息(使用execjs执行Nuxt的__NUXT__数据)
    """
    try:
        import urllib.parse
        import re
        import execjs
        
        encoded_keyword = urllib.parse.quote(keyword)
        search_url = f"https://www.miaofoods.com/search/{encoded_keyword}.html"
        
        # 请求头
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
            "Accept-Encoding": "gzip, deflate",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        }
        
        # 发送请求
        resp = requests.get(search_url, headers=headers, timeout=10, verify=False)
        resp.raise_for_status()
        resp.encoding = "utf-8"
        html = resp.text
        
        # 提取包含 window.__NUXT__ 的 script 标签
        script_pattern = re.search(r'<script>window\.__NUXT__\s*=\s*(.*?)</script>', html, re.S)
        
        if not script_pattern:
            raise HTTPException(status_code=500, detail="未能找到食物数据")
        
        # 提取 JavaScript 表达式
        js_expression = script_pattern.group(1).strip()
        
        # 移除末尾的分号(execjs.eval需要纯表达式)
        if js_expression.endswith(';'):
            js_expression = js_expression[:-1]
        
        # 执行 JavaScript 获取数据
        nuxt_data = execjs.eval(js_expression)
        
        # 从解析好的数据中提取食物列表
        data_list = nuxt_data.get('data', [{}])[0].get('curSearchFoodList', [])
        
        foods = []
        for item in data_list:  # 返回所有结果
            try:
                # 处理图片URL中的unicode编码
                image_url = item.get('foodIcon', '')
                if image_url:
                    image_url = image_url.replace('\\u002F', '/')
                
                food_item = {
                    "external_id": str(item.get('foodId', hash(item.get('foodName')))),
                    "name": item.get('foodName', ''),
                    "calories": Decimal(str(item.get('foodCaloriesVal', 0))),
                    "protein": Decimal(str(item.get('foodProteinVal', 0))),
                    "carbs": Decimal(str(item.get('foodCarbohydrateVal', 0))),
                    "fat": Decimal(str(item.get('foodFatVal', 0))),
                    "image_url": image_url,
                    "category": item.get('cateName'),
                    "source": "miaofoods",
                    "unit": "100克"
                }
                
                foods.append(food_item)
                
            except Exception as e:
                print(f"解析食物项失败: {str(e)}")
                import traceback
                traceback.print_exc()
                continue
        
        # 批量保存到数据库(后台任务)
        if foods:
            background_tasks.add_task(batch_save_foods_to_db, foods, db)
        
        return {
            "source": "online",
            "data": foods
        }
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"搜索食物失败: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")


# 获取食物详情（并异步保存到本地）
@router.get("/detail/{external_id}", summary="获取食物详情")
def get_food_detail(
    external_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取食物详细营养信息
    """
    try:
        # 先查本地
        local_food = db.query(FoodNutrition).filter(
            FoodNutrition.external_id == external_id
        ).first()
        
        if local_food:
            return FoodNutritionResponse.from_orm(local_food).dict()
        
        # TODO: 爬虫功能待实现
        raise HTTPException(status_code=404, detail="食物不存在")
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"获取食物详情失败: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"获取详情失败: {str(e)}")


def save_food_to_db(food_data: dict, db: Session):
    """
    保存食物到本地数据库(同步,后台任务调用)
    """
    try:
        # 检查是否已存在
        existing = db.query(FoodNutrition).filter(
            FoodNutrition.external_id == food_data['external_id']
        ).first()
        
        if existing:
            print(f"食物 {food_data['name']} 已存在,跳过保存")
            return
        
        # 保存到数据库(图片URL暂时保持原始链接)
        food = FoodNutrition(
            external_id=food_data['external_id'],
            name=food_data['name'],
            calories=food_data['calories'],
            protein=food_data.get('protein', 0),
            carbs=food_data.get('carbs', 0),
            fat=food_data.get('fat', 0),
            image_url=food_data.get('image_url'),
            unit=food_data.get('unit', '100g'),
            source='miaofoods',
            is_custom=False,
            category=food_data.get('category')
        )
        db.add(food)
        db.commit()
        print(f"食物 {food_data['name']} 已保存到本地")
        
    except Exception as e:
        print(f"保存食物到本地失败: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()


def batch_save_foods_to_db(foods_data: list, db: Session):
    """
    批量保存食物到本地数据库(同步,后台任务调用)
    同时下载图片并上传到七牛云
    """
    try:
        if not foods_data:
            return
        
        # 获取所有external_id
        external_ids = [food['external_id'] for food in foods_data]
        
        # 一次查询所有已存在的食物
        existing_foods = db.query(FoodNutrition.external_id).filter(
            FoodNutrition.external_id.in_(external_ids)
        ).all()
        existing_ids = set(row[0] for row in existing_foods)
        
        # 过滤出需要新增的食物
        new_foods = []
        for food_data in foods_data:
            if food_data['external_id'] not in existing_ids:
                # 处理图片上传
                qiniu_image_url = None
                original_image_url = food_data.get('image_url')
                
                if original_image_url:
                    try:
                        # 下载原始图片
                        import asyncio
                        image_response = requests.get(original_image_url, timeout=10)
                        if image_response.status_code == 200:
                            image_content = image_response.content
                            
                            # 获取文件扩展名
                            file_ext = '.jpg'  # 默认jpg
                            if '.' in original_image_url:
                                file_ext = '.' + original_image_url.split('.')[-1].split('?')[0]
                            
                            # 上传到七牛云(同步调用异步函数)
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            upload_result = loop.run_until_complete(
                                upload_file(image_content, file_ext, folder="foods/")
                            )
                            loop.close()
                            
                            if upload_result.get('success'):
                                qiniu_image_url = upload_result.get('url')
                                print(f"图片上传成功: {food_data['name']} -> {qiniu_image_url}")
                            else:
                                print(f"图片上传失败: {food_data['name']}")
                    except Exception as img_error:
                        print(f"处理图片失败 {food_data['name']}: {str(img_error)}")
                
                new_foods.append(FoodNutrition(
                    external_id=food_data['external_id'],
                    name=food_data['name'],
                    calories=food_data['calories'],
                    protein=food_data.get('protein', 0),
                    carbs=food_data.get('carbs', 0),
                    fat=food_data.get('fat', 0),
                    image_url=qiniu_image_url or original_image_url,  # 优先使用七牛云URL
                    unit=food_data.get('unit', '100g'),
                    source='miaofoods',
                    is_custom=False,
                    category=food_data.get('category')
                ))
        
        # 批量插入
        if new_foods:
            db.bulk_save_objects(new_foods)
            db.commit()
            print(f"批量保存了 {len(new_foods)} 个食物到本地")
        else:
            print("所有食物已存在,跳过保存")
        
    except Exception as e:
        print(f"批量保存食物失败: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()


# 本地食物库 - 列表查询
@router.get("/local", summary="本地食物库列表")
def get_local_foods(
    keyword: Optional[str] = None,
    category: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    random: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取本地食物库列表
    random=True 时随机返回数据
    """
    try:
        query = db.query(FoodNutrition)
        
        if keyword:
            query = query.filter(FoodNutrition.name.like(f"%{keyword}%"))
        
        if category:
            query = query.filter(FoodNutrition.category == category)
        
        total = query.count()
        
        if random:
            # 随机获取
            from sqlalchemy.sql.expression import func
            foods = query.order_by(func.rand()).limit(page_size).all()
        else:
            # 按更新时间倒序排列
            skip = (page - 1) * page_size
            foods = query.order_by(FoodNutrition.updated_at.desc()).offset(skip).limit(page_size).all()
        
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "items": [FoodNutritionResponse.from_orm(food).dict() for food in foods]
        }
        
    except Exception as e:
        print(f"获取本地食物库失败: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


# 新增/编辑本地食物
@router.post("/local", summary="新增食物到本地库")
def create_local_food(
    food: FoodNutritionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    新增食物到本地库
    """
    try:
        new_food = FoodNutrition(**food.dict())
        new_food.is_custom = True
        db.add(new_food)
        db.commit()
        db.refresh(new_food)
        
        return FoodNutritionResponse.from_orm(new_food).dict()
        
    except Exception as e:
        db.rollback()
        print(f"新增食物失败: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"新增失败: {str(e)}")


@router.put("/local/{food_id}", summary="编辑本地食物")
def update_local_food(
    food_id: int,
    food: FoodNutritionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    编辑本地食物
    """
    try:
        db_food = db.query(FoodNutrition).filter(FoodNutrition.id == food_id).first()
        if not db_food:
            raise HTTPException(status_code=404, detail="食物不存在")
        
        for key, value in food.dict(exclude_unset=True).items():
            setattr(db_food, key, value)
        
        db.commit()
        db.refresh(db_food)
        
        return FoodNutritionResponse.from_orm(db_food).dict()
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"编辑食物失败: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"编辑失败: {str(e)}")


@router.delete("/local/{food_id}", summary="删除本地食物")
def delete_local_food(
    food_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    删除本地食物
    """
    try:
        db_food = db.query(FoodNutrition).filter(FoodNutrition.id == food_id).first()
        if not db_food:
            raise HTTPException(status_code=404, detail="食物不存在")
        
        db.delete(db_food)
        db.commit()
        
        return {"message": "删除成功"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"删除食物失败: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")


# 上传食物图片
@router.post("/upload-image", summary="上传食物图片")
async def upload_food_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    上传食物图片到七牛云
    """
    try:
        contents = await file.read()
        
        # 获取文件扩展名
        import os
        file_ext = os.path.splitext(file.filename)[1]
        
        # 上传到七牛云
        result = await upload_file(contents, file_ext, folder="foods/")
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=f"上传失败: {result.get('error', '未知错误')}")
        
        return {"image_url": result["url"]}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"上传图片失败: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")
