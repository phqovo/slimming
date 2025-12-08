from sqlalchemy import Column, Integer, Float, DateTime, Date, ForeignKey, String, Text
from sqlalchemy.sql import func
from app.core.database import Base


class ExerciseRecord(Base):
    __tablename__ = "exercise_records"
    
    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String(100), default=None, index=True, comment="外部数据源ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="用户ID")
    exercise_type = Column(String(50), nullable=False, comment="运动类型：跑步/游泳/健身等")
    duration = Column(Integer, default=0, comment="运动时长(分钟)")
    calories = Column(Float, default=0.0, comment="消耗卡路里")
    distance = Column(Float, default=0.0, comment="运动距离(km)")
    image_url = Column(String(255), default="", comment="运动图片URL")
    note = Column(Text, default="", comment="备注")
    record_date = Column(Date, nullable=False, index=True, comment="记录日期")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
