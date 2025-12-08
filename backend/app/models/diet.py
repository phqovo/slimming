from sqlalchemy import Column, Integer, Float, DateTime, Date, ForeignKey, String, Text
from sqlalchemy.sql import func
from app.core.database import Base


class DietRecord(Base):
    __tablename__ = "diet_records"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="用户ID")
    meal_type = Column(String(20), nullable=False, comment="餐次：breakfast/lunch/dinner/snack")
    food_name = Column(String(100), nullable=False, comment="食物名称")
    calories = Column(Float, default=0.0, comment="卡路里")
    protein = Column(Float, default=0.0, comment="蛋白质(g)")
    carbs = Column(Float, default=0.0, comment="碳水化合物(g)")
    fat = Column(Float, default=0.0, comment="脂肪(g)")
    portion = Column(String(50), default="", comment="份量")
    note = Column(Text, default="", comment="备注")
    record_date = Column(Date, nullable=False, index=True, comment="记录日期")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
