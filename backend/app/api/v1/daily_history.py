from fastapi import APIRouter, Depends, HTTPException, status
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, date, timedelta
from typing import List, Optional
from app.core.database import get_db
from app.models.user import User
from app.models.daily_history import DailyHistory
from app.models.weight import WeightRecord
from app.models.diet import DietRecord
from app.models.exercise import ExerciseRecord
from app.models.water import WaterRecord
from app.api.deps import get_current_user
from pydantic import BaseModel, validator
from app.schemas.common import PaginationResponse
from app.models.sleep import SleepRecord
import math

router = APIRouter()


class DailyHistoryResponse(BaseModel):
    id: int
    record_date: str
    breakfast: str
    lunch: str
    dinner: str
    exercise: str
    morning_weight: Optional[float]
    evening_weight: Optional[float]
    water: str
    note: str
    
    @validator('record_date', pre=True)
    @classmethod
    def convert_date(cls, v):
        if isinstance(v, date):
            return v.isoformat()
        return v
    
    class Config:
        from_attributes = True


class DietRecordDetail(BaseModel):
    id: int
    meal_type: str
    food_name: str
    calories: float
    protein: float
    carbs: float
    fat: float
    portion: str
    note: str
    
    class Config:
        from_attributes = True


class ExerciseRecordDetail(BaseModel):
    id: int
    exercise_type: str
    duration: int
    calories: float
    distance: float
    note: str
    
    class Config:
        from_attributes = True


class WeightRecordDetail(BaseModel):
    id: Optional[int] = None
    weight: Optional[float] = None
    morning_weight: Optional[float] = None
    evening_weight: Optional[float] = None
    body_fat: Optional[float] = None
    note: str = ""
    
    class Config:
        from_attributes = True


class SleepRecordDetail(BaseModel):
    id: int
    duration: float
    quality: str
    sleep_time: Optional[str] = None
    wake_time: Optional[str] = None
    
    @validator('sleep_time', 'wake_time', pre=True)
    @classmethod
    def convert_datetime(cls, v):
        if v and hasattr(v, 'isoformat'):
            return v.isoformat()
        return v
    
    class Config:
        from_attributes = True


class WaterRecordDetail(BaseModel):
    id: int
    amount: int
    
    class Config:
        from_attributes = True


class DailyHistoryDetail(BaseModel):
    id: int
    record_date: str
    diet_records: List[DietRecordDetail]
    exercise_records: List[ExerciseRecordDetail]
    weight_record: Optional[WeightRecordDetail]
    sleep_records: List[SleepRecordDetail]
    water_records: List[WaterRecordDetail]
    note: str
    
    @validator('record_date', pre=True)
    @classmethod
    def convert_date(cls, v):
        if isinstance(v, date):
            return v.isoformat()
        return v
    
    class Config:
        from_attributes = True


class CreateDailyHistoryRequest(BaseModel):
    record_date: str
    diet_records: List[dict]
    exercise_records: List[dict]
    weight_record: Optional[dict]
    sleep_records: List[dict]
    water_records: List[dict]
    note: str = ""


@router.get("/daily-history", summary="获取历史数据")
async def get_daily_history(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取用户的历史记录数据（仅包含前一天及更早的数据）
    """
    try:
        # 确保最多只查询到前一天
        today = date.today()
        yesterday = today - timedelta(days=1)
        
        query = db.query(DailyHistory).filter(
            DailyHistory.user_id == current_user.id,
            DailyHistory.record_date <= yesterday
        )
        
        if start_date:
            query = query.filter(DailyHistory.record_date >= start_date)
        
        if end_date:
            query = query.filter(DailyHistory.record_date <= end_date)
        
        # 获取总数
        total = query.count()
        
        # 计算总页数
        total_pages = math.ceil(total / page_size) if total > 0 else 0
        
        # 按日期倒序
        query = query.order_by(DailyHistory.record_date.desc())
        
        # 分页查询
        skip = (page - 1) * page_size
        records = query.offset(skip).limit(page_size).all()
        
        # 转换为响应模型
        items = [DailyHistoryResponse.from_orm(record).dict() for record in records]
        
        # 返回分页响应
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "items": items
        }
        
    except Exception as e:
        print(f"获取历史数据失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取数据失败: {str(e)}"
        )


@router.post("/daily-history/recalculate", summary="重算指定日期的历史数据")
async def recalculate_daily_history(
    record_date: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    根据当日的饮食、运动、体重、饮水数据，重新计算并更新历史数据
    """
    try:
        target_date = datetime.strptime(record_date, "%Y-%m-%d").date()
        
        # 查询该日期的所有记录
        diet_records = db.query(DietRecord).filter(
            DietRecord.user_id == current_user.id,
            DietRecord.record_date == target_date
        ).all()
        
        exercise_records = db.query(ExerciseRecord).filter(
            ExerciseRecord.user_id == current_user.id,
            ExerciseRecord.record_date == target_date
        ).all()
        
        weight_records = db.query(WeightRecord).filter(
            WeightRecord.user_id == current_user.id,
            WeightRecord.record_date == target_date
        ).all()
        
        water_records = db.query(WaterRecord).filter(
            WaterRecord.user_id == current_user.id,
            WaterRecord.record_date == target_date
        ).all()
        
        # 组织数据
        breakfast_list = [f"{d.food_name} {d.portion if d.portion else ''} {int(d.calories)}大卡".strip() for d in diet_records if d.meal_type == 'breakfast']
        lunch_list = [f"{d.food_name} {d.portion if d.portion else ''} {int(d.calories)}大卡".strip() for d in diet_records if d.meal_type == 'lunch']
        dinner_list = [f"{d.food_name} {d.portion if d.portion else ''} {int(d.calories)}大卡".strip() for d in diet_records if d.meal_type == 'dinner']
        
        breakfast = ' + '.join(breakfast_list) if breakfast_list else "无"
        lunch = ' + '.join(lunch_list) if lunch_list else "无"
        dinner = ' + '.join(dinner_list) if dinner_list else "无"
        
        exercise_list = [f"{e.exercise_type} {e.duration}分钟 {int(e.calories)}大卡" for e in exercise_records]
        exercise = ' + '.join(exercise_list) if exercise_list else "无"
        
        # 获取体重数据（优先使用morning_weight和evening_weight字段）
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
        
        # 计算饮水总量
        total_water = sum(w.amount for w in water_records)
        water = f"{total_water / 1000:.1f}L" if total_water > 0 else "0L"
        
        # 查找或创建历史数据
        history = db.query(DailyHistory).filter(
            DailyHistory.user_id == current_user.id,
            DailyHistory.record_date == target_date
        ).first()
        
        if not history:
            history = DailyHistory(
                user_id=current_user.id,
                record_date=target_date
            )
            db.add(history)
        
        # 更新数据
        history.breakfast = breakfast
        history.lunch = lunch
        history.dinner = dinner
        history.exercise = exercise
        history.morning_weight = morning_weight
        history.evening_weight = evening_weight
        history.water = water
        history.note = note
        
        db.commit()
        db.refresh(history)
        
        return {
            "message": "重算成功",
            "data": DailyHistoryResponse.from_orm(history).dict()
        }
        
    except Exception as e:
        print(f"重算历史数据失败: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"重算失败: {str(e)}"
        )


@router.get("/daily-history/{history_id}", summary="获取历史记录详情")
async def get_daily_history_detail(
    history_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取指定历史记录的详细信息，包括各个子表的数据
    """
    try:
        # 获取历史记录
        history = db.query(DailyHistory).filter(
            DailyHistory.id == history_id,
            DailyHistory.user_id == current_user.id
        ).first()
        
        if not history:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="历史记录不存在"
            )
        
        # 获取该日期的所有子表数据
        diet_records = db.query(DietRecord).filter(
            DietRecord.user_id == current_user.id,
            DietRecord.record_date == history.record_date
        ).all()
        
        exercise_records = db.query(ExerciseRecord).filter(
            ExerciseRecord.user_id == current_user.id,
            ExerciseRecord.record_date == history.record_date
        ).all()
        
        weight_record = db.query(WeightRecord).filter(
            WeightRecord.user_id == current_user.id,
            WeightRecord.record_date == history.record_date
        ).first()
        
        sleep_records = db.query(SleepRecord).filter(
            SleepRecord.user_id == current_user.id,
            SleepRecord.record_date == history.record_date
        ).all()
        
        water_records = db.query(WaterRecord).filter(
            WaterRecord.user_id == current_user.id,
            WaterRecord.record_date == history.record_date
        ).all()
        
        return {
            "id": history.id,
            "record_date": history.record_date.isoformat(),
            "diet_records": [DietRecordDetail.from_orm(d).dict() for d in diet_records],
            "exercise_records": [ExerciseRecordDetail.from_orm(e).dict() for e in exercise_records],
            "weight_record": WeightRecordDetail.from_orm(weight_record).dict() if weight_record else None,
            "sleep_records": [SleepRecordDetail.from_orm(s).dict() for s in sleep_records],
            "water_records": [WaterRecordDetail.from_orm(w).dict() for w in water_records],
            "note": history.note
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"获取历史详情失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取详情失败: {str(e)}"
        )


@router.post("/daily-history", summary="新增历史记录")
async def create_daily_history(
    request: CreateDailyHistoryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    新增历史记录，只能添加今天之前的数据
    """
    try:
        target_date = datetime.strptime(request.record_date, "%Y-%m-%d").date()
        today = date.today()
        
        # 验证日期必须是今天之前
        if target_date >= today:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="只能记录今天之前的数据"
            )
        
        # 检查该日期是否已存在记录
        existing = db.query(DailyHistory).filter(
            DailyHistory.user_id == current_user.id,
            DailyHistory.record_date == target_date
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该日期已有记录，请使用编辑功能"
            )
        
        # 保存饮食记录
        for diet in request.diet_records:
            diet_record = DietRecord(
                user_id=current_user.id,
                record_date=target_date,
                meal_type=diet.get('meal_type'),
                food_name=diet.get('food_name'),
                calories=diet.get('calories', 0),
                protein=diet.get('protein', 0),
                carbs=diet.get('carbs', 0),
                fat=diet.get('fat', 0),
                portion=diet.get('portion', ''),
                note=diet.get('note', '')
            )
            db.add(diet_record)
        
        # 保存运动记录
        for exercise in request.exercise_records:
            exercise_record = ExerciseRecord(
                user_id=current_user.id,
                record_date=target_date,
                exercise_type=exercise.get('exercise_type'),
                duration=exercise.get('duration'),
                calories=exercise.get('calories', 0),
                distance=exercise.get('distance', 0),
                note=exercise.get('note', '')
            )
            db.add(exercise_record)
        
        # 保存体重记录
        if request.weight_record:
            # 智能取值：如果没有填写当前体重，使用早晨体重或睡前体重
            weight = request.weight_record.get('weight')
            if not weight:
                weight = request.weight_record.get('morning_weight') or request.weight_record.get('evening_weight')
            
            # 如果有任何体重数据，才创建记录
            if weight or request.weight_record.get('morning_weight') or request.weight_record.get('evening_weight'):
                weight_record = WeightRecord(
                    user_id=current_user.id,
                    record_date=target_date,
                    weight=weight,
                    morning_weight=request.weight_record.get('morning_weight'),
                    evening_weight=request.weight_record.get('evening_weight'),
                    body_fat=request.weight_record.get('body_fat') or None,
                    bmi=0.0,  # 后续可以计算
                    note=request.weight_record.get('note', '')
                )
                db.add(weight_record)
        
        # 保存睡眠记录
        for sleep in request.sleep_records:
            sleep_record = SleepRecord(
                user_id=current_user.id,
                record_date=target_date,
                duration=sleep.get('duration'),
                quality=sleep.get('quality', ''),
                sleep_time=datetime.fromisoformat(sleep['sleep_time']) if sleep.get('sleep_time') else None,
                wake_time=datetime.fromisoformat(sleep['wake_time']) if sleep.get('wake_time') else None
            )
            db.add(sleep_record)
        
        # 保存饮水记录
        for water in request.water_records:
            water_record = WaterRecord(
                user_id=current_user.id,
                record_date=target_date,
                amount=water.get('amount')
            )
            db.add(water_record)
        
        # 创建历史汇总记录
        # 汇总饮食数据
        breakfast_list = [f"{d.get('food_name')} {d.get('portion', '')} {int(d.get('calories', 0))}大卡".strip() for d in request.diet_records if d.get('meal_type') == 'breakfast']
        lunch_list = [f"{d.get('food_name')} {d.get('portion', '')} {int(d.get('calories', 0))}大卡".strip() for d in request.diet_records if d.get('meal_type') == 'lunch']
        dinner_list = [f"{d.get('food_name')} {d.get('portion', '')} {int(d.get('calories', 0))}大卡".strip() for d in request.diet_records if d.get('meal_type') == 'dinner']
        
        breakfast = ' + '.join(breakfast_list) if breakfast_list else "无"
        lunch = ' + '.join(lunch_list) if lunch_list else "无"
        dinner = ' + '.join(dinner_list) if dinner_list else "无"
        
        # 汇总运动数据
        exercise_list = [f"{e.get('exercise_type')} {e.get('duration', 0)}分钟 {int(e.get('calories', 0))}大卡" for e in request.exercise_records]
        exercise = ' + '.join(exercise_list) if exercise_list else "无"
        
        # 获取体重数据
        morning_weight = request.weight_record.get('morning_weight') if request.weight_record else None
        evening_weight = request.weight_record.get('evening_weight') if request.weight_record else None
        
        # 计算饮水总量
        total_water = sum(w.get('amount', 0) for w in request.water_records)
        water = f"{total_water / 1000:.1f}L" if total_water > 0 else "0L"
        
        history = DailyHistory(
            user_id=current_user.id,
            record_date=target_date,
            breakfast=breakfast,
            lunch=lunch,
            dinner=dinner,
            exercise=exercise,
            morning_weight=morning_weight,
            evening_weight=evening_weight,
            water=water,
            note=request.note
        )
        db.add(history)
        
        db.commit()
        db.refresh(history)
        
        return {
            "message": "创建成功",
            "data": DailyHistoryResponse.from_orm(history).dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"创建历史记录失败: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建失败: {str(e)}"
        )


@router.put("/daily-history/{history_id}", summary="更新历史记录")
async def update_daily_history(
    history_id: int,
    request: CreateDailyHistoryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新历史记录，删除原子表数据并插入新数据
    """
    try:
        # 获取历史记录
        history = db.query(DailyHistory).filter(
            DailyHistory.id == history_id,
            DailyHistory.user_id == current_user.id
        ).first()
        
        if not history:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="历史记录不存在"
            )
        
        target_date = datetime.strptime(request.record_date, "%Y-%m-%d").date()
        today = date.today()
        
        # 验证日期必须是今天之前
        if target_date >= today:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="只能记录今天之前的数据"
            )
        
        # 如果修改了日期，检查新日期是否已存在记录
        if target_date != history.record_date:
            existing = db.query(DailyHistory).filter(
                DailyHistory.user_id == current_user.id,
                DailyHistory.record_date == target_date
            ).first()
            
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="目标日期已有记录，无法修改为该日期"
                )
        
        # 删除原日期的所有子表记录（仅删除用户手动数据，不删除同步数据）
        old_date = history.record_date
        db.query(DietRecord).filter(
            DietRecord.user_id == current_user.id,
            DietRecord.record_date == old_date
        ).delete()
        
        db.query(ExerciseRecord).filter(
            ExerciseRecord.user_id == current_user.id,
            ExerciseRecord.record_date == old_date
            # 删除所有运动记录，包括外部同步的，以用户编辑的数据为准
        ).delete()
        
        db.query(WeightRecord).filter(
            WeightRecord.user_id == current_user.id,
            WeightRecord.record_date == old_date
            # 删除所有体重记录，包括外部同步的，以用户编辑的数据为准
        ).delete()
        
        db.query(SleepRecord).filter(
            SleepRecord.user_id == current_user.id,
            SleepRecord.record_date == old_date
            # 删除所有睡眠记录，包括外部同步的，以用户编辑的数据为准
        ).delete()
        
        db.query(WaterRecord).filter(
            WaterRecord.user_id == current_user.id,
            WaterRecord.record_date == old_date
        ).delete()
        
        # 插入新数据（与创建逻辑相同）
        # 保存饮食记录
        for diet in request.diet_records:
            diet_record = DietRecord(
                user_id=current_user.id,
                record_date=target_date,
                meal_type=diet.get('meal_type'),
                food_name=diet.get('food_name'),
                calories=diet.get('calories', 0),
                protein=diet.get('protein', 0),
                carbs=diet.get('carbs', 0),
                fat=diet.get('fat', 0),
                portion=diet.get('portion', ''),
                note=diet.get('note', '')
            )
            db.add(diet_record)
        
        # 保存运动记录
        for exercise in request.exercise_records:
            exercise_record = ExerciseRecord(
                user_id=current_user.id,
                record_date=target_date,
                exercise_type=exercise.get('exercise_type'),
                duration=exercise.get('duration'),
                calories=exercise.get('calories', 0),
                distance=exercise.get('distance', 0),
                note=exercise.get('note', '')
            )
            db.add(exercise_record)
        
        # 保存体重记录
        if request.weight_record:
            # 智能取值：如果没有填写当前体重，使用早晨体重或睡前体重
            weight = request.weight_record.get('weight')
            if not weight:
                weight = request.weight_record.get('morning_weight') or request.weight_record.get('evening_weight')
            
            # 如果有任何体重数据，才创建记录
            if weight or request.weight_record.get('morning_weight') or request.weight_record.get('evening_weight'):
                weight_record = WeightRecord(
                    user_id=current_user.id,
                    record_date=target_date,
                    weight=weight,
                    morning_weight=request.weight_record.get('morning_weight'),
                    evening_weight=request.weight_record.get('evening_weight'),
                    body_fat=request.weight_record.get('body_fat') or None,
                    bmi=0.0,  # 后续可以计算
                    note=request.weight_record.get('note', '')
                )
                db.add(weight_record)
        
        # 保存睡眠记录
        for sleep in request.sleep_records:
            sleep_record = SleepRecord(
                user_id=current_user.id,
                record_date=target_date,
                duration=sleep.get('duration'),
                quality=sleep.get('quality', ''),
                sleep_time=datetime.fromisoformat(sleep['sleep_time']) if sleep.get('sleep_time') else None,
                wake_time=datetime.fromisoformat(sleep['wake_time']) if sleep.get('wake_time') else None
            )
            db.add(sleep_record)
        
        # 保存饮水记录
        for water in request.water_records:
            water_record = WaterRecord(
                user_id=current_user.id,
                record_date=target_date,
                amount=water.get('amount')
            )
            db.add(water_record)
        
        # 更新历史汇总记录
        breakfast_list = [f"{d.get('food_name')} {d.get('portion', '')} {int(d.get('calories', 0))}大卡".strip() for d in request.diet_records if d.get('meal_type') == 'breakfast']
        lunch_list = [f"{d.get('food_name')} {d.get('portion', '')} {int(d.get('calories', 0))}大卡".strip() for d in request.diet_records if d.get('meal_type') == 'lunch']
        dinner_list = [f"{d.get('food_name')} {d.get('portion', '')} {int(d.get('calories', 0))}大卡".strip() for d in request.diet_records if d.get('meal_type') == 'dinner']
        
        breakfast = ' + '.join(breakfast_list) if breakfast_list else "无"
        lunch = ' + '.join(lunch_list) if lunch_list else "无"
        dinner = ' + '.join(dinner_list) if dinner_list else "无"
        
        exercise_list = [f"{e.get('exercise_type')} {e.get('duration', 0)}分钟 {int(e.get('calories', 0))}大卡" for e in request.exercise_records]
        exercise = ' + '.join(exercise_list) if exercise_list else "无"
        lunch = '+'.join(lunch_list) if lunch_list else "无"
        dinner = '+'.join(dinner_list) if dinner_list else "无"
        
        exercise_list = [f"{e.get('exercise_type')} {e.get('calories', 0)}大卡" for e in request.exercise_records]
        exercise = '+'.join(exercise_list) if exercise_list else "无"
        
        morning_weight = request.weight_record.get('morning_weight') if request.weight_record else None
        evening_weight = request.weight_record.get('evening_weight') if request.weight_record else None
        
        total_water = sum(w.get('amount', 0) for w in request.water_records)
        water = f"{total_water / 1000:.1f}L" if total_water > 0 else "0L"
        
        history.record_date = target_date
        history.breakfast = breakfast
        history.lunch = lunch
        history.dinner = dinner
        history.exercise = exercise
        history.morning_weight = morning_weight
        history.evening_weight = evening_weight
        history.water = water
        history.note = request.note
        
        db.commit()
        db.refresh(history)
        
        return {
            "message": "更新成功",
            "data": DailyHistoryResponse.from_orm(history).dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"更新历史记录失败: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新失败: {str(e)}"
        )


@router.delete("/daily-history/{history_id}", summary="删除历史记录")
async def delete_daily_history(
    history_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    删除历史记录及对应日期的所有子表数据
    """
    try:
        # 获取历史记录
        history = db.query(DailyHistory).filter(
            DailyHistory.id == history_id,
            DailyHistory.user_id == current_user.id
        ).first()
        
        if not history:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="历史记录不存在"
            )
        
        record_date = history.record_date
        
        # 删除所有子表记录（仅删除用户手动数据，不删除同步数据）
        db.query(DietRecord).filter(
            DietRecord.user_id == current_user.id,
            DietRecord.record_date == record_date
        ).delete()
        
        db.query(ExerciseRecord).filter(
            ExerciseRecord.user_id == current_user.id,
            ExerciseRecord.record_date == record_date,
            ExerciseRecord.external_id.is_(None)  # 只删除用户手动数据
        ).delete()
        
        db.query(WeightRecord).filter(
            WeightRecord.user_id == current_user.id,
            WeightRecord.record_date == record_date,
            WeightRecord.external_id.is_(None)  # 只删除用户手动数据
        ).delete()
        
        db.query(SleepRecord).filter(
            SleepRecord.user_id == current_user.id,
            SleepRecord.record_date == record_date,
            SleepRecord.external_id.is_(None)  # 只删除用户手动数据
        ).delete()
        
        db.query(WaterRecord).filter(
            WaterRecord.user_id == current_user.id,
            WaterRecord.record_date == record_date
        ).delete()
        
        # 删除历史记录
        db.delete(history)
        
        db.commit()
        
        return {"message": "删除成功"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"删除历史记录失败: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除失败: {str(e)}"
        )
