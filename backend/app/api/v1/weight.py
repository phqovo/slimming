from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime, timedelta
from app.core.database import get_db
from app.models.user import User
from app.models.weight import WeightRecord
from app.models.daily_history import DailyHistory
from app.schemas.weight import (
    WeightRecordCreate, WeightRecordUpdate, WeightRecordResponse,
    WeightTrendRequest, WeightPrediction
)
from app.api.deps import get_current_user
from app.utils.health_calculator import update_user_health_stats

router = APIRouter()


def trigger_daily_history_recalculate(db: Session, user_id: int, record_date: date):
    """触发历史数据重算，今天的数据也会保存到历史记录表"""
    # 移除日期限制，今天的数据也会触发历史记录更新
    from app.models.diet import DietRecord
    from app.models.exercise import ExerciseRecord
    from app.models.water import WaterRecord
    
    # 查询该日期的所有记录
    diet_records = db.query(DietRecord).filter(
        DietRecord.user_id == user_id,
        DietRecord.record_date == record_date
    ).all()
    
    exercise_records = db.query(ExerciseRecord).filter(
        ExerciseRecord.user_id == user_id,
        ExerciseRecord.record_date == record_date
    ).all()
    
    weight_records = db.query(WeightRecord).filter(
        WeightRecord.user_id == user_id,
        WeightRecord.record_date == record_date
    ).all()
    
    water_records = db.query(WaterRecord).filter(
        WaterRecord.user_id == user_id,
        WaterRecord.record_date == record_date
    ).all()
    
    # 汇总数据
    breakfast_list = [f"{d.food_name} {d.portion if d.portion else ''} {int(d.calories)}大卡".strip() for d in diet_records if d.meal_type == 'breakfast']
    lunch_list = [f"{d.food_name} {d.portion if d.portion else ''} {int(d.calories)}大卡".strip() for d in diet_records if d.meal_type == 'lunch']
    dinner_list = [f"{d.food_name} {d.portion if d.portion else ''} {int(d.calories)}大卡".strip() for d in diet_records if d.meal_type == 'dinner']
    
    breakfast = ' + '.join(breakfast_list) if breakfast_list else "无"
    lunch = ' + '.join(lunch_list) if lunch_list else "无"
    dinner = ' + '.join(dinner_list) if dinner_list else "无"
    
    exercise_list = [f"{e.exercise_type} {e.duration}分钟 {int(e.calories)}大卡" for e in exercise_records]
    exercise = ' + '.join(exercise_list) if exercise_list else "无"
    
    # 体重数据
    morning_weight = None
    evening_weight = None
    note = ""
    
    for weight in weight_records:
        if weight.morning_weight:
            morning_weight = weight.morning_weight
        if weight.evening_weight:
            evening_weight = weight.evening_weight
        if weight.note:
            note = weight.note
    
    # 计算饮水
    total_water = sum(w.amount for w in water_records)
    water = f"{total_water / 1000:.1f}L" if total_water > 0 else "0L"
    
    # 查找或创建历史记录
    history = db.query(DailyHistory).filter(
        DailyHistory.user_id == user_id,
        DailyHistory.record_date == record_date
    ).first()
    
    if not history:
        history = DailyHistory(
            user_id=user_id,
            record_date=record_date
        )
        db.add(history)
    
    history.breakfast = breakfast
    history.lunch = lunch
    history.dinner = dinner
    history.exercise = exercise
    history.morning_weight = morning_weight
    history.evening_weight = evening_weight
    history.water = water
    history.note = note
    
    db.commit()


@router.post("/", response_model=WeightRecordResponse, summary="创建或更新体重记录")
async def create_weight_record(
    record: WeightRecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建或更新体重记录（saveOrUpdate逻辑）"""
    # 如果没有填写当前体重，使用早晨体重或睡前体重作为默认值
    weight = record.weight
    if not weight:
        weight = record.morning_weight or record.evening_weight
    
    # 如果仍然没有体重数据，返回错误
    if not weight:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="请至少填写一项体重数据（当前体重、早晨体重或睡前体重）"
        )
    
    # 计算BMI
    bmi = 0.0
    if current_user.height > 0:
        height_m = current_user.height / 100
        bmi = weight / (height_m * height_m)
    
    # 检查当天是否已有记录
    existing = db.query(WeightRecord).filter(
        WeightRecord.user_id == current_user.id,
        WeightRecord.record_date == record.record_date
    ).first()
    
    if existing:
        # 更新现有记录
        existing.weight = weight
        existing.morning_weight = record.morning_weight
        existing.evening_weight = record.evening_weight
        existing.body_fat = record.body_fat
        existing.bmi = bmi
        existing.note = record.note
        
        db.commit()
        db.refresh(existing)
        db_record = existing
    else:
        # 创建新记录
        db_record = WeightRecord(
            user_id=current_user.id,
            weight=weight,
            morning_weight=record.morning_weight,
            evening_weight=record.evening_weight,
            body_fat=record.body_fat,
            bmi=bmi,
            record_date=record.record_date,
            note=record.note
        )
        
        db.add(db_record)
        db.commit()
        db.refresh(db_record)
    
    # 更新用户的健康数据（当前体重、BMI、基础代谢）
    update_user_health_stats(db, current_user.id)
    
    # 触发历史数据重算
    trigger_daily_history_recalculate(db, current_user.id, record.record_date)
    
    return WeightRecordResponse.from_orm(db_record).dict()


@router.get("/", response_model=List[WeightRecordResponse], summary="获取体重记录列表")
async def get_weight_records(
    skip: int = 0,
    limit: int = 100,
    all_records: bool = False,
    record_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取用户的体重记录列表
    
    Args:
        skip: 跳过的记录数
        limit: 限制的记录数
        all_records: 是否获取所有记录（忽略skip和limit）
        record_date: 指定日期（格式：YYYY-MM-DD）
    """
    query = db.query(WeightRecord).filter(
        WeightRecord.user_id == current_user.id
    )
    
    # 如果指定了日期，添加日期过滤
    if record_date:
        query = query.filter(WeightRecord.record_date == record_date)
    
    query = query.order_by(WeightRecord.record_date.desc())
    
    if all_records:
        records = query.all()
    else:
        records = query.offset(skip).limit(limit).all()
    
    return [WeightRecordResponse.from_orm(r).dict() for r in records]


@router.get("/trend", summary="获取体重趋势")
async def get_weight_trend(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取体重趋势数据"""
    try:
        # 支持返回全部记录：当 days <= 0 时不做日期限制
        query = db.query(WeightRecord).filter(WeightRecord.user_id == current_user.id)
        if days and days > 0:
            start_date = date.today() - timedelta(days=days)
            query = query.filter(WeightRecord.record_date >= start_date)
        records = query.order_by(WeightRecord.record_date.asc()).all()
        
        data = [{
            "record_date": r.record_date.strftime("%Y-%m-%d"),
            "weight": float(r.weight)
        } for r in records]
        
        return {
            "data": data,
            "current_weight": float(current_user.current_weight) if current_user.current_weight else None,
            "target_weight": float(current_user.target_weight) if current_user.target_weight else None
        }
        
    except Exception as e:
        print(f"获取体重趋势失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取失败: {str(e)}")


@router.get("/{record_id}", response_model=WeightRecordResponse, summary="获取单条体重记录")
async def get_weight_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取指定的体重记录"""
    record = db.query(WeightRecord).filter(
        WeightRecord.id == record_id,
        WeightRecord.user_id == current_user.id
    ).first()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="记录不存在"
        )
    
    return WeightRecordResponse.from_orm(record).dict()


@router.put("/{record_id}", response_model=WeightRecordResponse, summary="更新体重记录")
async def update_weight_record(
    record_id: int,
    record_update: WeightRecordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新体重记录"""
    record = db.query(WeightRecord).filter(
        WeightRecord.id == record_id,
        WeightRecord.user_id == current_user.id
    ).first()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="记录不存在"
        )
    
    # 更新字段
    for field, value in record_update.dict(exclude_unset=True).items():
        setattr(record, field, value)
    
    # 重新计算BMI
    if record_update.weight and current_user.height > 0:
        height_m = current_user.height / 100
        record.bmi = record.weight / (height_m * height_m)
    
    db.commit()
    db.refresh(record)
    
    # 更新用户的健康数据
    update_user_health_stats(db, current_user.id)
    
    # 触发历史数据重算
    record_date = record_update.record_date if record_update.record_date else record.record_date
    trigger_daily_history_recalculate(db, current_user.id, record_date)
    
    return WeightRecordResponse.from_orm(record).dict()


@router.delete("/{record_id}", summary="删除体重记录")
async def delete_weight_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除体重记录"""
    record = db.query(WeightRecord).filter(
        WeightRecord.id == record_id,
        WeightRecord.user_id == current_user.id
    ).first()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="记录不存在"
        )
    
    db.delete(record)
    db.commit()
    
    # 删除后重新计算用户健康数据
    update_user_health_stats(db, current_user.id)
    
    # 触发历史数据重算
    trigger_daily_history_recalculate(db, current_user.id, record.record_date)
    
    return {"code": 200, "message": "删除成功"}


@router.post("/predict", summary="预测体重趋势")
async def predict_weight_trend(
    request: WeightTrendRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """基于历史数据预测未来体重趋势"""
    from app.services.ml_service import predict_weight_trend
    
    predictions = await predict_weight_trend(db, current_user.id, request.days)
    
    return {
        "code": 200,
        "data": predictions
    }
