from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.core.database import get_db
from app.models.user import User
from app.models.weight import WeightRecord
from app.models.diet import DietRecord
from app.models.exercise import ExerciseRecord
from app.api.deps import get_current_user
from datetime import date, timedelta

router = APIRouter()


@router.get("/dashboard", summary="获取首页概览数据")
async def get_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取今日概览数据
    - 最新体重
    - 今日摄入热量
    - 今日消耗热量
    - 今日饮食记录
    - 今日运动记录
    """
    try:
        today = date.today()
        
        # 获取最新体重记录
        latest_weight = db.query(WeightRecord).filter(
            WeightRecord.user_id == current_user.id
        ).order_by(desc(WeightRecord.record_date)).first()
        
        # 获取今日饮食记录
        today_diet = db.query(DietRecord).filter(
            DietRecord.user_id == current_user.id,
            DietRecord.record_date == today
        ).all()
        
        # 计算今日摄入热量
        today_calories = sum(float(d.calories or 0) for d in today_diet)
        
        # 获取今日运动记录
        today_exercise = db.query(ExerciseRecord).filter(
            ExerciseRecord.user_id == current_user.id,
            ExerciseRecord.record_date == today
        ).all()
        
        # 计算今日消耗热量
        today_exercise_calories = sum(float(e.calories or 0) for e in today_exercise)
        
        # 格式化饮食记录
        diet_records = [{
            "id": d.id,
            "meal_type": d.meal_type,
            "food_name": d.food_name,
            "calories": float(d.calories or 0),
            "portion": d.portion or "",
            "record_date": d.record_date.strftime("%Y-%m-%d")
        } for d in today_diet]
        
        # 格式化运动记录
        exercise_records = [{
            "id": e.id,
            "exercise_type": e.exercise_type,
            "duration": e.duration,
            "calories": float(e.calories or 0),
            "distance": float(e.distance or 0),
            "record_date": e.record_date.strftime("%Y-%m-%d")
        } for e in today_exercise]
        
        return {
            "latest_weight": {
                "weight": float(latest_weight.weight) if latest_weight else None,
                "record_date": latest_weight.record_date.strftime("%Y-%m-%d") if latest_weight else None
            } if latest_weight else None,
            "today_calories": round(today_calories, 1),
            "today_exercise_calories": round(today_exercise_calories, 1),
            "today_diet_records": diet_records,
            "today_exercise_records": exercise_records
        }
        
    except Exception as e:
        print(f"获取首页数据失败: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"获取失败: {str(e)}")


@router.get("/calories-trend", summary="获取热量趋势")
async def get_calories_trend(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取热量趋势数据
    - 摄入热量趋势
    - 消耗热量趋势
    """
    try:
        start_date = date.today() - timedelta(days=days)
        
        # 获取饮食记录
        diet_records = db.query(
            DietRecord.record_date,
            func.sum(DietRecord.calories).label('total_calories')
        ).filter(
            DietRecord.user_id == current_user.id,
            DietRecord.record_date >= start_date
        ).group_by(DietRecord.record_date).all()
        
        # 获取运动记录
        exercise_records = db.query(
            ExerciseRecord.record_date,
            func.sum(ExerciseRecord.calories).label('total_calories')
        ).filter(
            ExerciseRecord.user_id == current_user.id,
            ExerciseRecord.record_date >= start_date
        ).group_by(ExerciseRecord.record_date).all()
        
        # 创建日期到热量的映射
        diet_map = {str(r.record_date): float(r.total_calories or 0) for r in diet_records}
        exercise_map = {str(r.record_date): float(r.total_calories or 0) for r in exercise_records}
        
        # 生成完整的日期序列
        data = []
        for i in range(days):
            current_date = start_date + timedelta(days=i)
            date_str = str(current_date)
            data.append({
                "date": date_str,
                "intake": round(diet_map.get(date_str, 0), 1),
                "consume": round(exercise_map.get(date_str, 0), 1)
            })
        
        return {
            "data": data
        }
        
    except Exception as e:
        print(f"获取热量趋势失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取失败: {str(e)}")
