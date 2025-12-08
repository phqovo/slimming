from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.models.user import User
from app.models.user_settings import UserSettings
from app.models.weight import WeightRecord
from app.api.deps import get_current_user
from datetime import date

router = APIRouter()


@router.get("/leaderboard", summary="获取减肥榜")
async def get_leaderboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取减肥榜数据
    - 显示所有有减重记录的用户
    - 按减重斤数从高到低排序
    - 减重 = 首次体重 - 当前体重
    - 耗时 = 今天 - 首次记录日期
    - data_public字段用于控制能否查看用户详情页
    """
    try:
        # 查询所有用户，连表查询user_settings
        from sqlalchemy.orm import joinedload
        
        all_users = db.query(User).all()
        
        rankings = []
        today = date.today()
        
        for user in all_users:
            # 获取该用户的首次体重记录
            first_record = db.query(WeightRecord).filter(
                WeightRecord.user_id == user.id
            ).order_by(WeightRecord.record_date.asc()).first()
            
            if not first_record:
                continue
            
            # 获取当前体重（今天有记录就用今天的，否则用用户表的）
            today_record = db.query(WeightRecord).filter(
                WeightRecord.user_id == user.id,
                WeightRecord.record_date == today
            ).first()
            
            current_weight = today_record.weight if today_record else user.current_weight
            
            # 如果当前体重为0，跳过
            if current_weight <= 0:
                continue
            
            # 计算减重（单位：公斤）
            weight_lost_kg = first_record.weight - current_weight
            
            # 转换为斤（1公斤 = 2斤）
            weight_lost_jin = round(weight_lost_kg * 2, 1)
            
            # 只统计减重成功的（减重大于0）
            if weight_lost_jin <= 0:
                continue
            
            # 计算耗时天数
            days = (today - first_record.record_date).days
            
            # 获取用户设置，判断是否公开数据
            user_setting = db.query(UserSettings).filter(
                UserSettings.user_id == user.id
            ).first()
            
            data_public = user_setting.data_public if user_setting else False
            
            rankings.append({
                "user_id": user.id,
                "nickname": user.nickname,
                "username": user.phone[-4:] if user.phone else "",  # 手机号后4位作为用户名
                "avatar": user.avatar,
                "weight_lost": weight_lost_jin,
                "days": days,
                "is_current_user": user.id == current_user.id,
                "data_public": data_public  # 是否允许查看详情
            })
        
        # 按减重斤数降序排序
        rankings.sort(key=lambda x: x["weight_lost"], reverse=True)
        
        return {
            "code": 200,
            "data": rankings
        }
        
    except Exception as e:
        print(f"获取减肥榜失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "code": 500,
            "message": f"获取失败: {str(e)}",
            "data": []
        }
