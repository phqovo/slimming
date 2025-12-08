from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, date
from typing import List, Dict, Optional
from app.core.database import get_db
from app.models.user import User
from app.models.diet import DietRecord
from app.models.exercise import ExerciseRecord
from app.api.deps import get_current_user

router = APIRouter()


@router.get("/nutrition-analysis", summary="获取营养成分分析")
async def get_nutrition_analysis(
    analysis_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取指定日期的营养成分分析
    - 计算总热量、蛋白质、碳水、脂肪摄入
    - 对比推荐摄入量
    - 计算热量缺口
    - 生成营养建议
    """
    try:
        # 解析日期，默认今天
        if analysis_date:
            target_date = datetime.strptime(analysis_date, "%Y-%m-%d").date()
        else:
            target_date = date.today()
        
        # 获取用户基础数据
        user_bmr = current_user.bmr or 0  # 基础代谢
        user_height = current_user.height or 0
        user_age = current_user.age or 0
        user_gender = current_user.gender or 'male'
        
        # 查询当天饮食记录
        diet_records = db.query(DietRecord).filter(
            DietRecord.user_id == current_user.id,
            DietRecord.record_date == target_date
        ).all()
        
        # 查询当天运动记录
        exercise_records = db.query(ExerciseRecord).filter(
            ExerciseRecord.user_id == current_user.id,
            ExerciseRecord.record_date == target_date
        ).all()
        
        # 计算摄入营养成分
        total_calories = sum(float(d.calories or 0) for d in diet_records)
        total_protein = sum(float(d.protein or 0) for d in diet_records)
        total_carbs = sum(float(d.carbs or 0) for d in diet_records)
        total_fat = sum(float(d.fat or 0) for d in diet_records)
        
        # 计算运动消耗
        exercise_calories = sum(float(e.calories or 0) for e in exercise_records)
        
        # 计算总能量消耗（TDEE）= 基础代谢 + 实际运动消耗
        # 不使用固定活动系数，而是使用真实的运动数据
        tdee = user_bmr + exercise_calories if user_bmr > 0 else 2000 + exercise_calories
        
        # 减肥热量缺口（建议每天减少500千卡）
        calorie_deficit = 500
        
        # 推荐摄入量 = TDEE - 热量缺口
        recommended_intake = tdee - calorie_deficit
        
        # 推荐营养素比例（蛋白质20%、碳水50%、脂肪30%）
        recommended_protein = (recommended_intake * 0.20) / 4  # 1g蛋白质 = 4千卡
        recommended_carbs = (recommended_intake * 0.50) / 4    # 1g碳水 = 4千卡
        recommended_fat = (recommended_intake * 0.30) / 9      # 1g脂肪 = 9千卡
        
        # 计算营养素占比
        total_macro_calories = (total_protein * 4) + (total_carbs * 4) + (total_fat * 9)
        protein_ratio = round((total_protein * 4 / total_macro_calories * 100), 1) if total_macro_calories > 0 else 0
        carbs_ratio = round((total_carbs * 4 / total_macro_calories * 100), 1) if total_macro_calories > 0 else 0
        fat_ratio = round((total_fat * 9 / total_macro_calories * 100), 1) if total_macro_calories > 0 else 0
        
        # 计算热量缺口
        calories_remaining = recommended_intake - total_calories  # 还能摄入的热量
        
        # 准备营养摄入数据（只包含蛋白质、碳水、脂肪）
        nutrition_data = [
            {
                "name": "蛋白质",
                "current": round(total_protein, 1),
                "target": round(recommended_protein, 1),
                "unit": "g"
            },
            {
                "name": "碳水化合物",
                "current": round(total_carbs, 1),
                "target": round(recommended_carbs, 1),
                "unit": "g"
            },
            {
                "name": "脂肪",
                "current": round(total_fat, 1),
                "target": round(recommended_fat, 1),
                "unit": "g"
            }
        ]
        
        # 生成营养建议
        recommendations = []
        
        # 热量建议
        if total_calories < user_bmr * 0.8:
            recommendations.append({
                "title": "热量摄入不足",
                "content": f"您今天的饮食摄入({round(total_calories)}千卡)低于基础代谢的80%，建议适当增加饮食，以免影响基础代谢和健康。",
                "type": "warning"
            })
        elif total_calories > recommended_intake * 1.2:
            recommendations.append({
                "title": "热量摄入过高",
                "content": f"您今天的饮食摄入({round(total_calories)}千卡)超过推荐量的20%，建议适当控制饮食或增加运动。",
                "type": "warning"
            })
        else:
            recommendations.append({
                "title": "热量摄入合理",
                "content": f"您今天的饮食摄入({round(total_calories)}千卡)在推荐范围内，保持每天{calorie_deficit}千卡热量缺口有助于减重。",
                "type": "good"
            })
        
        # 蛋白质建议
        protein_percentage = (total_protein / recommended_protein * 100) if recommended_protein > 0 else 0
        if protein_percentage < 70:
            recommendations.append({
                "title": "增加蛋白质摄入",
                "content": f"您的蛋白质摄入({round(total_protein, 1)}g)较低，建议增加鸡胸肉、鱼类、豆制品等优质蛋白来源。",
                "type": "warning"
            })
        elif protein_percentage >= 80:
            recommendations.append({
                "title": "蛋白质摄入充足",
                "content": f"您的蛋白质摄入({round(total_protein, 1)}g)达到推荐量，有助于肌肉恢复和维护。",
                "type": "good"
            })
        
        # 碳水化合物建议
        carbs_percentage = (total_carbs / recommended_carbs * 100) if recommended_carbs > 0 else 0
        if carbs_percentage > 120:
            recommendations.append({
                "title": "控制碳水化合物",
                "content": f"您的碳水化合物摄入({round(total_carbs, 1)}g)偏高，建议减少精制碳水，多选择全谷物和蔬菜。",
                "type": "warning"
            })
        
        # 脂肪建议
        fat_percentage = (total_fat / recommended_fat * 100) if recommended_fat > 0 else 0
        if fat_percentage > 120:
            recommendations.append({
                "title": "注意脂肪摄入",
                "content": f"您的脂肪摄入({round(total_fat, 1)}g)偏高，建议减少油炸食品，选择健康脂肪来源如坚果、橄榄油。",
                "type": "warning"
            })
        
        # 运动建议
        if exercise_calories == 0:
            recommendations.append({
                "title": "增加运动量",
                "content": "您今天还没有运动记录，建议每天至少进行30分钟中等强度运动，如快走、慢跑或游泳。",
                "type": "warning"
            })
        else:
            recommendations.append({
                "title": "运动表现良好",
                "content": f"您今天消耗了{round(exercise_calories)}千卡，坚持运动有助于保持健康体重。",
                "type": "good"
            })
        
        return {
            "date": target_date.isoformat(),
            "summary": {
                "total_calories": round(total_calories, 1),
                "exercise_calories": round(exercise_calories, 1),
                "calories_remaining": round(calories_remaining, 1),
                "bmr": round(user_bmr, 1),
                "tdee": round(tdee, 1),
                "recommended_intake": round(recommended_intake, 1),
                "calorie_deficit": calorie_deficit,
                "protein_ratio": protein_ratio,
                "carbs_ratio": carbs_ratio,
                "fat_ratio": fat_ratio,
                "total_protein": round(total_protein, 1),
                "total_carbs": round(total_carbs, 1),
                "total_fat": round(total_fat, 1)
            },
            "nutrition_data": nutrition_data,
            "recommendations": recommendations
        }
        
    except Exception as e:
        print(f"获取营养分析失败: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取营养分析失败: {str(e)}"
        )
