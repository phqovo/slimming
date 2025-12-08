from sqlalchemy import Column, Integer, Float, DateTime, Date, ForeignKey, String, Text
from sqlalchemy.sql import func
from app.core.database import Base


class DailyHistory(Base):
    __tablename__ = "daily_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="用户ID")
    record_date = Column(Date, nullable=False, index=True, comment="记录日期（前一天及之前）")
    
    # 饮食信息
    breakfast = Column(String(500), default="无", comment="早餐")
    lunch = Column(String(500), default="无", comment="中餐")
    dinner = Column(String(500), default="无", comment="晚餐")
    
    # 运动信息
    exercise = Column(String(500), default="无", comment="运动")
    
    # 体重信息
    morning_weight = Column(Float, default=None, comment="早晨体重(kg)")
    evening_weight = Column(Float, default=None, comment="睡前体重(kg)")
    
    # 饮水信息
    water = Column(String(50), default="0L", comment="饮水")
    
    # 备注
    note = Column(Text, default="", comment="备注")
    
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    class Config:
        from_attributes = True
