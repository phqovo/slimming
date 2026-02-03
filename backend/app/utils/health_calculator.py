"""
用户健康数据计算工具
"""
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.weight import WeightRecord


def calculate_bmi(weight: float, height: float) -> float:
    """
    计算BMI指数
    
    Args:
        weight: 体重(kg)
        height: 身高(cm)
        
    Returns:
        BMI值
    """
    if weight is None or height is None:
        return 0.0
    if height <= 0 or weight <= 0:
        return 0.0
    
    height_m = height / 100  # 转换为米
    bmi = weight / (height_m * height_m)
    return round(bmi, 2)


def calculate_bmr(weight: float, height: float, age: int, gender: str) -> float:
    """
    计算基础代谢率（使用Harris-Benedict公式）
    
    Args:
        weight: 体重(kg)
        height: 身高(cm)
        age: 年龄
        gender: 性别 (male/female)
        
    Returns:
        基础代谢率(kcal/天)
    """
    if weight is None or height is None or age is None:
        return 0.0
    if weight <= 0 or height <= 0 or age <= 0:
        return 0.0
    
    if gender == "male":
        # 男性：BMR = 88.362 + (13.397 × 体重kg) + (4.799 × 身高cm) - (5.677 × 年龄)
        bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
    elif gender == "female":
        # 女性：BMR = 447.593 + (9.247 × 体重kg) + (3.098 × 身高cm) - (4.330 × 年龄)
        bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)
    else:
        # 未设置性别，使用平均值
        male_bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
        female_bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)
        bmr = (male_bmr + female_bmr) / 2
    
    return round(bmr, 2)


def update_user_health_stats(db: Session, user_id: int) -> bool:
    """
    更新用户的健康数据（当前体重、BMI、基础代谢）
    从最新的体重记录中获取数据并计算
    
    Args:
        db: 数据库会话
        user_id: 用户ID
        
    Returns:
        是否更新成功
    """
    try:
        # 获取用户信息
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        
        # 获取最新的体重记录
        latest_weight_record = db.query(WeightRecord).filter(
            WeightRecord.user_id == user_id
        ).order_by(
            WeightRecord.record_date.desc(),
            WeightRecord.updated_at.desc(),
            WeightRecord.id.desc()
        ).first()
        
        if not latest_weight_record:
            # 没有体重记录，清空数据
            user.current_weight = 0.0
            user.bmi = 0.0
            user.bmr = 0.0
        else:
            # 更新当前体重
            user.current_weight = latest_weight_record.weight
            
            # 计算BMI
            user.bmi = calculate_bmi(latest_weight_record.weight, user.height)
            
            # 计算基础代谢率
            user.bmr = calculate_bmr(
                latest_weight_record.weight,
                user.height,
                user.age,
                user.gender
            )
        
        db.commit()
        return True
        
    except Exception as e:
        print(f"更新用户健康数据失败: {str(e)}")
        db.rollback()
        return False
