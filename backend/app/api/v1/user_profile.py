from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.core.database import get_db
from app.models.user import User
from app.models.user_settings import UserSettings
from app.models.weight import WeightRecord
from app.models.diet import DietRecord
from app.models.exercise import ExerciseRecord
from app.api.deps import get_current_user
from datetime import date, timedelta
from collections import defaultdict

router = APIRouter()


@router.get("/profile/{user_id}", summary="获取用户详情")
async def get_user_profile(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取用户详情信息
    - 需要用户开启数据公开才能查看
    - 返回用户基本信息、体重趋势、饮食记录、锻炼记录
    """
    try:
        # 查询目标用户
        target_user = db.query(User).filter(User.id == user_id).first()
        if not target_user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        # 查询用户设置，判断是否公开数据
        user_setting = db.query(UserSettings).filter(
            UserSettings.user_id == user_id
        ).first()
        
        # 如果不是查看自己，且未公开数据，则拒绝访问
        if user_id != current_user.id:
            if not user_setting or not user_setting.data_public:
                raise HTTPException(status_code=403, detail="该用户未公开数据，无法查看详情")
        
        # 获取首次体重记录（初始体重）
        first_record = db.query(WeightRecord).filter(
            WeightRecord.user_id == user_id
        ).order_by(WeightRecord.record_date.asc()).first()
        
        initial_weight = first_record.weight if first_record else target_user.current_weight
        
        # 获取用户基本信息
        user_info = {
            "id": target_user.id,
            "nickname": target_user.nickname,
            "avatar": target_user.avatar,
            "age": target_user.age,
            "gender": target_user.gender,
            "height": target_user.height,
            "initial_weight": initial_weight,  # 初始体重
            "target_weight": target_user.target_weight,
            "current_weight": target_user.current_weight,
            "bmi": target_user.bmi,
            "bmr": target_user.bmr
        }
        
        # 获取最近30天的体重记录
        thirty_days_ago = date.today() - timedelta(days=30)
        weight_records = db.query(WeightRecord).filter(
            WeightRecord.user_id == user_id,
            WeightRecord.record_date >= thirty_days_ago
        ).order_by(WeightRecord.record_date.asc()).all()
        
        weight_data = [{
            "date": record.record_date.strftime("%Y-%m-%d"),
            "weight": float(record.weight)
        } for record in weight_records]
        
        # 计算减重进度（first_record 已在上面获取）
        weight_lost = 0
        days_elapsed = 0
        if first_record:
            weight_lost = round((first_record.weight - target_user.current_weight) * 2, 1)  # 转换为斤
            days_elapsed = (date.today() - first_record.record_date).days
        
        # 获取最近10天的饮食记录，按天聚合
        ten_days_ago = date.today() - timedelta(days=9)  # 包含今天共10天
        diet_records = db.query(DietRecord).filter(
            DietRecord.user_id == user_id,
            DietRecord.record_date >= ten_days_ago
        ).order_by(desc(DietRecord.record_date)).all()
        
        # 按日期聚合饮食记录
        diet_by_date = defaultdict(lambda: {"total_calories": 0, "meals": {}})
        for record in diet_records:
            date_str = record.record_date.strftime("%Y-%m-%d")
            diet_by_date[date_str]["total_calories"] += float(record.calories) if record.calories else 0
            
            # 按餐次分组
            meal_type = record.meal_type
            if meal_type not in diet_by_date[date_str]["meals"]:
                diet_by_date[date_str]["meals"][meal_type] = []
            
            diet_by_date[date_str]["meals"][meal_type].append({
                "food_name": record.food_name,
                "portion": record.portion or "",
                "calories": float(record.calories) if record.calories else 0
            })
        
        # 定义餐次顺序
        meal_order = ["breakfast", "lunch", "dinner", "snack"]
        
        diet_data = []
        for date_str, data in sorted(diet_by_date.items(), reverse=True)[:10]:
            # 按顺序组织餐次数据
            ordered_meals = []
            for meal_type in meal_order:
                if meal_type in data["meals"]:
                    ordered_meals.append({
                        "meal_type": meal_type,
                        "foods": data["meals"][meal_type],
                        "meal_calories": sum(food["calories"] for food in data["meals"][meal_type])
                    })
            
            diet_data.append({
                "date": date_str,
                "total_calories": round(data["total_calories"], 1),
                "meal_count": len(ordered_meals),  # 统计不同餐次的数量
                "meals": ordered_meals
            })
        
        # 获取最近10天的锻炼记录，按天聚合
        exercise_records = db.query(ExerciseRecord).filter(
            ExerciseRecord.user_id == user_id,
            ExerciseRecord.record_date >= ten_days_ago
        ).order_by(desc(ExerciseRecord.record_date)).all()
        
        # 按日期聚合锻炼记录
        exercise_by_date = defaultdict(lambda: {"total_duration": 0, "total_calories": 0, "total_distance": 0, "exercises": []})
        for record in exercise_records:
            date_str = record.record_date.strftime("%Y-%m-%d")
            exercise_by_date[date_str]["total_duration"] += record.duration or 0
            exercise_by_date[date_str]["total_calories"] += float(record.calories) if record.calories else 0
            exercise_by_date[date_str]["total_distance"] += float(record.distance) if record.distance else 0
            exercise_by_date[date_str]["exercises"].append({
                "exercise_type": record.exercise_type,
                "duration": record.duration,
                "calories": float(record.calories) if record.calories else 0,
                "distance": float(record.distance) if record.distance else 0
            })
        
        exercise_data = [{
            "date": date_str,
            "total_duration": data["total_duration"],
            "total_calories": round(data["total_calories"], 1),
            "total_distance": round(data["total_distance"], 2),
            "exercise_count": len(data["exercises"]),
            "exercises": data["exercises"]
        } for date_str, data in sorted(exercise_by_date.items(), reverse=True)][:10]
        
        return {
            "code": 200,
            "data": {
                "user_info": user_info,
                "weight_progress": {
                    "weight_lost": weight_lost,
                    "days_elapsed": days_elapsed
                },
                "weight_data": weight_data,
                "diet_records": diet_data,
                "exercise_records": exercise_data
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"获取用户详情失败: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"获取失败: {str(e)}")
