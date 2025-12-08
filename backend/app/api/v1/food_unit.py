import json
import uuid
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.redis import get_redis
from app.schemas.food_unit import (
    FoodUnitCreate,
    FoodUnitUpdate,
    FoodUnitResponse,
    FoodUnitRecordCreate,
    FoodUnitRecordResponse,
)
from app.api.deps import get_current_user

router = APIRouter(prefix="/api/v1/food-units", tags=["food-units"])

# Redis key 前缀
UNIT_KEY_PREFIX = "food_unit:"  # food_unit:{user_id}:{source_type}:{food_id}:units
RECORD_KEY_PREFIX = "food_unit_record:"  # food_unit_record:{user_id}:{source_type}:{food_id}


@router.post("/units", response_model=FoodUnitResponse)
async def create_food_unit(
    unit_data: FoodUnitCreate,
    current_user = Depends(get_current_user),
    redis_client = Depends(get_redis),
):
    """\u521b建食物单位（保存到 Redis）"""
    user_id = current_user.id
    food_id = unit_data.food_id
    source_type = unit_data.source_type or "local"  # 默认为本地
    
    # 生成单位ID
    unit_id = str(uuid.uuid4())
    
    # Redis key - 带上文物源类型
    key = f"{UNIT_KEY_PREFIX}{user_id}:{source_type}:{food_id}:units"
    
    # 构建单位数据
    unit_info = {
        "unit_id": unit_id,
        "unit_name": unit_data.unit_name,
        "unit_weight": unit_data.unit_weight,
        "food_id": food_id,
        "source_type": source_type,
        "created_at": datetime.utcnow().isoformat(),
    }
    
    # 存储到 Redis（以 unit_id 为 hash field）
    redis_client.hset(
        key,
        unit_id,
        json.dumps(unit_info),
    )
    
    # 设置过期时间（30天）
    redis_client.expire(key, 30 * 24 * 60 * 60)
    
    return FoodUnitResponse(**unit_info)


@router.get("/units/{food_id}", response_model=List[FoodUnitResponse])
async def get_food_units(
    food_id: int,
    source_type: str = "local",
    current_user = Depends(get_current_user),
    redis_client = Depends(get_redis),
):
    """获取某个食物的所有自定义单位"""
    user_id = current_user.id
    key = f"{UNIT_KEY_PREFIX}{user_id}:{source_type}:{food_id}:units"
    
    units_data = redis_client.hgetall(key)
    
    if not units_data:
        return []
    
    # 反序列化
    units = []
    for unit_json in units_data.values():
        unit = json.loads(unit_json)
        units.append(FoodUnitResponse(**unit))
    
    return units


@router.put("/units/{food_id}/{unit_id}", response_model=FoodUnitResponse)
async def update_food_unit(
    food_id: int,
    unit_id: str,
    unit_data: FoodUnitUpdate,
    source_type: str = "local",
    current_user = Depends(get_current_user),
    redis_client = Depends(get_redis),
):
    """更新食物单位"""
    user_id = current_user.id
    key = f"{UNIT_KEY_PREFIX}{user_id}:{source_type}:{food_id}:units"
    
    # 获取现有单位数据
    unit_json = redis_client.hget(key, unit_id)
    if not unit_json:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="单位不存在",
        )
    
    unit_info = json.loads(unit_json)
    
    # 更新字段
    if unit_data.unit_name is not None:
        unit_info["unit_name"] = unit_data.unit_name
    if unit_data.unit_weight is not None:
        unit_info["unit_weight"] = unit_data.unit_weight
    
    unit_info["updated_at"] = datetime.utcnow().isoformat()
    
    # 保存回 Redis
    redis_client.hset(key, unit_id, json.dumps(unit_info))
    redis_client.expire(key, 30 * 24 * 60 * 60)
    
    return FoodUnitResponse(**unit_info)


@router.delete("/units/{food_id}/{unit_id}")
async def delete_food_unit(
    food_id: int,
    unit_id: str,
    source_type: str = "local",
    current_user = Depends(get_current_user),
    redis_client = Depends(get_redis),
):
    """删除食物单位"""
    user_id = current_user.id
    key = f"{UNIT_KEY_PREFIX}{user_id}:{source_type}:{food_id}:units"
    
    # 检查单位是否存在
    unit_json = redis_client.hget(key, unit_id)
    if not unit_json:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="单位不存在",
        )
    
    # 删除
    redis_client.hdel(key, unit_id)
    
    return {"message": "单位已删除"}


@router.post("/records", response_model=FoodUnitRecordResponse)
async def save_food_unit_record(
    record_data: FoodUnitRecordCreate,
    current_user = Depends(get_current_user),
    redis_client = Depends(get_redis),
):
    """保存食物单位转换记录"""
    user_id = current_user.id
    food_id = record_data.food_id
    source_type = record_data.source_type or "local"
    
    # 生成记录ID
    record_id = str(uuid.uuid4())
    
    # Redis key - 带上文物源类型
    key = f"{RECORD_KEY_PREFIX}{user_id}:{source_type}:{food_id}"
    
    # 构建记录数据
    record_info = {
        "record_id": record_id,
        "food_id": food_id,
        "unit_id": record_data.unit_id,
        "quantity": record_data.quantity,
        "total_weight": record_data.total_weight,
        "calories": record_data.calories,
        "protein": record_data.protein,
        "carbs": record_data.carbs,
        "fat": record_data.fat,
        "source_type": source_type,
        "created_at": datetime.utcnow().isoformat(),
    }
    
    # 存储到 Redis（以 record_id 为 hash field）
    redis_client.hset(
        key,
        record_id,
        json.dumps(record_info),
    )
    
    # 设置过期时间（30天）
    redis_client.expire(key, 30 * 24 * 60 * 60)
    
    return FoodUnitRecordResponse(**record_info)


@router.get("/records/{food_id}", response_model=List[FoodUnitRecordResponse])
async def get_food_unit_records(
    food_id: int,
    source_type: str = "local",
    current_user = Depends(get_current_user),
    redis_client = Depends(get_redis),
):
    """获取某个食物的所有单位转换记录"""
    user_id = current_user.id
    key = f"{RECORD_KEY_PREFIX}{user_id}:{source_type}:{food_id}"
    
    records_data = redis_client.hgetall(key)
    
    if not records_data:
        return []
    
    # 反序列化并排序（按创建时间倒序）
    records = []
    for record_json in records_data.values():
        record = json.loads(record_json)
        records.append(FoodUnitRecordResponse(**record))
    
    # 按创建时间倒序排列
    records.sort(key=lambda x: x.created_at if hasattr(x, 'created_at') else '', reverse=True)
    
    return records


@router.delete("/records/{food_id}/{record_id}")
async def delete_food_unit_record(
    food_id: int,
    record_id: str,
    source_type: str = "local",
    current_user = Depends(get_current_user),
    redis_client = Depends(get_redis),
):
    """删除食物单位转换记录"""
    user_id = current_user.id
    key = f"{RECORD_KEY_PREFIX}{user_id}:{source_type}:{food_id}"
    
    # 检查记录是否存在
    record_json = redis_client.hget(key, record_id)
    if not record_json:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="记录不存在",
        )
    
    # 删除
    redis_client.hdel(key, record_id)
    
    return {"message": "记录已删除"}
