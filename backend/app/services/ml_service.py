from sqlalchemy.orm import Session
from datetime import date, timedelta
import numpy as np
from sklearn.linear_model import LinearRegression
from typing import List
from app.models.weight import WeightRecord
from app.schemas.weight import WeightPrediction


async def predict_weight_trend(db: Session, user_id: int, days: int) -> List[WeightPrediction]:
    """
    基于历史数据预测未来体重趋势
    使用线性回归模型进行简单预测
    """
    # 获取用户的历史体重记录（最近90天）
    records = db.query(WeightRecord).filter(
        WeightRecord.user_id == user_id
    ).order_by(WeightRecord.record_date).all()
    
    if len(records) < 3:
        # 数据不足，无法预测
        return []
    
    # 准备训练数据
    dates = []
    weights = []
    base_date = records[0].record_date
    
    for record in records:
        days_diff = (record.record_date - base_date).days
        dates.append(days_diff)
        weights.append(record.weight)
    
    # 转换为numpy数组
    X = np.array(dates).reshape(-1, 1)
    y = np.array(weights)
    
    # 训练线性回归模型
    model = LinearRegression()
    model.fit(X, y)
    
    # 预测未来体重
    predictions = []
    last_record_date = records[-1].record_date
    
    for i in range(1, days + 1):
        predict_date = last_record_date + timedelta(days=i)
        days_diff = (predict_date - base_date).days
        
        predicted_weight = model.predict([[days_diff]])[0]
        
        # 计算置信区间（简化版，使用标准差）
        residuals = y - model.predict(X)
        std_dev = np.std(residuals)
        
        predictions.append(WeightPrediction(
            date=predict_date,
            predicted_weight=round(predicted_weight, 2),
            confidence_interval_lower=round(predicted_weight - 1.96 * std_dev, 2),
            confidence_interval_upper=round(predicted_weight + 1.96 * std_dev, 2)
        ))
    
    return predictions


async def calculate_bmi(weight: float, height: float) -> float:
    """计算BMI指数"""
    if height <= 0:
        return 0.0
    height_m = height / 100
    return weight / (height_m * height_m)


async def calculate_bmr(weight: float, height: float, age: int, gender: str) -> float:
    """
    计算基础代谢率（BMR）
    使用Harris-Benedict公式
    """
    if gender == "male":
        bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
    elif gender == "female":
        bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)
    else:
        bmr = 0.0
    
    return bmr
