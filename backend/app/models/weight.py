from sqlalchemy import Column, Integer, Float, DateTime, Date, ForeignKey, String
from sqlalchemy.sql import func
from app.core.database import Base


class WeightRecord(Base):
    __tablename__ = "weight_records"
    
    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String(100), default=None, index=True, comment="外部数据源ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="用户ID")
    weight = Column(Float, nullable=False, comment="体重(kg)")
    morning_weight = Column(Float, default=None, comment="早晨体重(kg)")
    evening_weight = Column(Float, default=None, comment="睡前体重(kg)")
    body_fat = Column(Float, default=0.0, comment="体脂率(%)")
    bmi = Column(Float, default=0.0, comment="BMI指数")
    record_date = Column(Date, nullable=False, index=True, comment="记录日期")
    note = Column(String(255), default="", comment="备注")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
