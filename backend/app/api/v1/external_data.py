"""外部数据查询API"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.external_data import (
    ExternalSleepRecord,
    ExternalExerciseRecord,
    ExternalWeightRecord,
    ExternalStepRecord
)
from app.schemas.external_data import ExternalDataListResponse
from app.utils.exercise_types import get_exercise_type_cn
from typing import Optional
from datetime import datetime, date
import math

router = APIRouter()


@router.get("/latest-weight", summary="获取最新的体重成分数据")
async def get_latest_weight(
    data_source: Optional[str] = Query("xiaomi_sport", description="数据来源"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取最新的体重成分数据，用于人体成分报告
    """
    query = db.query(ExternalWeightRecord).filter(
        ExternalWeightRecord.user_id == current_user.id
    )
    
    if data_source:
        query = query.filter(ExternalWeightRecord.data_source == data_source)
    
    # 获取最新的一条记录
    latest_record = query.order_by(
        desc(ExternalWeightRecord.measure_date),
        desc(ExternalWeightRecord.measure_time)
    ).first()
    
    if not latest_record:
        return None
    
    # 返回完整的体重成分数据
    return {
        'id': latest_record.id,
        'user_id': latest_record.user_id,
        'data_source': latest_record.data_source,
        'measure_date': latest_record.measure_date,
        'measure_time': latest_record.measure_time,
        # 基础指标
        'weight': float(latest_record.weight) if latest_record.weight else None,
        'bmi': float(latest_record.bmi) if latest_record.bmi else None,
        'body_fat': float(latest_record.body_fat) if latest_record.body_fat else None,
        'muscle_mass': float(latest_record.muscle_mass) if latest_record.muscle_mass else None,
        'bone_mass': float(latest_record.bone_mass) if latest_record.bone_mass else None,
        'water': float(latest_record.water) if latest_record.water else None,
        'protein': float(latest_record.protein) if latest_record.protein else None,
        'bmr': latest_record.bmr,
        'visceral_fat': float(latest_record.visceral_fat) if latest_record.visceral_fat else None,
        'body_age': latest_record.body_age,
        'body_score': latest_record.body_score,
        'heart_rate': latest_record.heart_rate,
        'whr': float(latest_record.whr) if latest_record.whr else None,
        'body_shape': latest_record.body_shape,
        'fat_mass': float(latest_record.fat_mass) if latest_record.fat_mass else None,
        # 左下肢
        'left_lower_limb_fat_mass': float(latest_record.left_lower_limb_fat_mass) if latest_record.left_lower_limb_fat_mass else None,
        'left_lower_limb_fat_rank': latest_record.left_lower_limb_fat_rank,
        'left_lower_limb_muscle_mass': float(latest_record.left_lower_limb_muscle_mass) if latest_record.left_lower_limb_muscle_mass else None,
        'left_lower_limb_muscle_rank': latest_record.left_lower_limb_muscle_rank,
        # 左上肢
        'left_upper_limb_fat_mass': float(latest_record.left_upper_limb_fat_mass) if latest_record.left_upper_limb_fat_mass else None,
        'left_upper_limb_fat_rank': latest_record.left_upper_limb_fat_rank,
        'left_upper_limb_muscle_mass': float(latest_record.left_upper_limb_muscle_mass) if latest_record.left_upper_limb_muscle_mass else None,
        'left_upper_limb_muscle_rank': latest_record.left_upper_limb_muscle_rank,
        # 右下肢
        'right_lower_limb_fat_mass': float(latest_record.right_lower_limb_fat_mass) if latest_record.right_lower_limb_fat_mass else None,
        'right_lower_limb_fat_rank': latest_record.right_lower_limb_fat_rank,
        'right_lower_limb_muscle_mass': float(latest_record.right_lower_limb_muscle_mass) if latest_record.right_lower_limb_muscle_mass else None,
        'right_lower_limb_muscle_rank': latest_record.right_lower_limb_muscle_rank,
        # 右上肢
        'right_upper_limb_fat_mass': float(latest_record.right_upper_limb_fat_mass) if latest_record.right_upper_limb_fat_mass else None,
        'right_upper_limb_fat_rank': latest_record.right_upper_limb_fat_rank,
        'right_upper_limb_muscle_mass': float(latest_record.right_upper_limb_muscle_mass) if latest_record.right_upper_limb_muscle_mass else None,
        'right_upper_limb_muscle_rank': latest_record.right_upper_limb_muscle_rank,
        # 躯干
        'trunk_fat_mass': float(latest_record.trunk_fat_mass) if latest_record.trunk_fat_mass else None,
        'trunk_fat_rank': latest_record.trunk_fat_rank,
        'trunk_muscle_mass': float(latest_record.trunk_muscle_mass) if latest_record.trunk_muscle_mass else None,
        'trunk_muscle_rank': latest_record.trunk_muscle_rank,
        # 平衡指标
        'limbs_fat_balance': latest_record.limbs_fat_balance,
        'limbs_muscle_balance': latest_record.limbs_muscle_balance,
        'limbs_skeletal_muscle_index': float(latest_record.limbs_skeletal_muscle_index) if latest_record.limbs_skeletal_muscle_index else None,
        'lower_limb_fat_balance': latest_record.lower_limb_fat_balance,
        'lower_limb_muscle_balance': latest_record.lower_limb_muscle_balance,
        'upper_limb_fat_balance': latest_record.upper_limb_fat_balance,
        'upper_limb_muscle_balance': latest_record.upper_limb_muscle_balance,
        # 其他
        'recommended_calories_intake': latest_record.recommended_calories_intake,
        'created_at': latest_record.created_at
    }


@router.get("/", summary="获取外部数据列表")
async def get_external_data_list(
    data_type: str = Query(..., description="数据类型：sleep/exercise/weight/steps"),
    data_source: Optional[str] = Query("xiaomi_sport", description="数据来源"),
    start_date: Optional[date] = Query(None, description="开始日期"),
    end_date: Optional[date] = Query(None, description="结束日期"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取外部数据列表
    支持按数据类型、数据来源、时间范围筛选
    """
    # 根据数据类型选择对应的模型
    model_map = {
        'sleep': ExternalSleepRecord,
        'exercise': ExternalExerciseRecord,
        'weight': ExternalWeightRecord,
        'steps': ExternalStepRecord
    }
    
    if data_type not in model_map:
        return {
            "total": 0,
            "page": page,
            "page_size": page_size,
            "total_pages": 0,
            "items": []
        }
    
    model = model_map[data_type]
    
    # 构建查询
    query = db.query(model).filter(model.user_id == current_user.id)
    
    # 数据来源筛选
    if data_source:
        query = query.filter(model.data_source == data_source)
    
    # 时间范围筛选
    if start_date:
        if data_type == 'sleep':
            query = query.filter(model.sleep_date >= start_date)
        elif data_type == 'exercise':
            query = query.filter(model.exercise_date >= start_date)
        elif data_type == 'weight':
            query = query.filter(model.measure_date >= start_date)
        elif data_type == 'steps':
            query = query.filter(model.step_date >= start_date)
    
    if end_date:
        if data_type == 'sleep':
            query = query.filter(model.sleep_date <= end_date)
        elif data_type == 'exercise':
            query = query.filter(model.exercise_date <= end_date)
        elif data_type == 'weight':
            query = query.filter(model.measure_date <= end_date)
        elif data_type == 'steps':
            query = query.filter(model.step_date <= end_date)
    
    # 总数
    total = query.count()
    
    # 按时间倒序排序
    if data_type == 'sleep':
        query = query.order_by(desc(model.sleep_date), desc(model.start_time))
    elif data_type == 'exercise':
        query = query.order_by(desc(model.exercise_date), desc(model.start_time))
    elif data_type == 'weight':
        query = query.order_by(desc(model.measure_date), desc(model.measure_time))
    elif data_type == 'steps':
        query = query.order_by(desc(model.step_date))
    
    # 分页
    offset = (page - 1) * page_size
    items = query.offset(offset).limit(page_size).all()
    
    # 转换为字典列表
    items_data = []
    for item in items:
        item_dict = {
            'id': item.id,
            'user_id': item.user_id,
            'data_source': item.data_source,
            'created_at': item.created_at
        }
        
        # 根据类型添加特定字段
        if data_type == 'sleep':
            item_dict.update({
                'sleep_date': item.sleep_date,
                'start_time': item.start_time,
                'end_time': item.end_time,
                'total_duration': item.total_duration,
                'deep_sleep': item.deep_sleep,
                'light_sleep': item.light_sleep,
                'rem_sleep': item.rem_sleep,
                'awake_time': item.awake_time,
                'sleep_score': item.sleep_score
            })
        elif data_type == 'exercise':
            item_dict.update({
                'exercise_date': item.exercise_date,
                'start_time': item.start_time,
                'end_time': item.end_time,
                'exercise_type': item.exercise_type,
                'exercise_type_cn': get_exercise_type_cn(item.exercise_type),  # 添加中文类型
                'duration': item.duration,
                'distance': float(item.distance) if item.distance else None,
                'calories': item.calories,
                'steps': item.steps,
                'avg_heart_rate': item.avg_heart_rate,
                'max_heart_rate': item.max_heart_rate
            })
        elif data_type == 'weight':
            item_dict.update({
                'measure_date': item.measure_date,
                'measure_time': item.measure_time,
                'weight': float(item.weight),
                'bmi': float(item.bmi) if item.bmi else None,
                'body_fat': float(item.body_fat) if item.body_fat else None,
                'muscle_mass': float(item.muscle_mass) if item.muscle_mass else None,
                'bone_mass': float(item.bone_mass) if item.bone_mass else None,
                'water': float(item.water) if item.water else None,
                'protein': float(item.protein) if item.protein else None,
                'bmr': item.bmr,
                'visceral_fat': float(item.visceral_fat) if item.visceral_fat else None,
                'body_age': item.body_age,
                'body_score': item.body_score,
                'note': item.note
            })
        elif data_type == 'steps':
            item_dict.update({
                'step_date': item.step_date,
                'steps': item.steps,
                'distance': float(item.distance) if item.distance else None,
                'calories': item.calories,
                'active_time': item.active_time
            })
        
        items_data.append(item_dict)
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": math.ceil(total / page_size) if total > 0 else 0,
        "items": items_data
    }
