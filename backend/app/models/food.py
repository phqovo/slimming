from sqlalchemy import Column, Integer, String, DECIMAL, Text, Boolean, TIMESTAMP
from sqlalchemy.sql import func
from app.core.database import Base


class FoodNutrition(Base):
    """食物营养成分表"""
    __tablename__ = "food_nutrition"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    external_id = Column(String(50), comment="外部数据源ID")
    name = Column(String(100), nullable=False, comment="食物名称", index=True)
    category = Column(String(50), comment="分类", index=True)
    calories = Column(DECIMAL(8, 2), nullable=False, comment="热量(千卡/100g)")
    protein = Column(DECIMAL(8, 2), default=0, comment="蛋白质(g/100g)")
    carbs = Column(DECIMAL(8, 2), default=0, comment="碳水化合物(g/100g)")
    fat = Column(DECIMAL(8, 2), default=0, comment="脂肪(g/100g)")
    image_url = Column(String(500), comment="图片URL（七牛云）")
    unit = Column(String(20), default="100g", comment="计量单位")
    source = Column(String(50), default="miaofoods", comment="数据来源")
    is_custom = Column(Boolean, default=False, comment="是否用户自定义")
    created_at = Column(TIMESTAMP, server_default=func.now(), comment="创建时间")
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), comment="更新时间")
