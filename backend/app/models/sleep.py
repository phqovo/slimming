from sqlalchemy import Column, Integer, Float, DateTime, Date, ForeignKey, String
from sqlalchemy.sql import func
from app.core.database import Base


class SleepRecord(Base):
    __tablename__ = "sleep_records"
    
    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String(100), default=None, index=True, comment="外部数据源ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="用户ID")
    duration = Column(Float, nullable=False, comment="睡眠时长(小时)")
    quality = Column(String(20), default="", comment="睡眠质量：excellent/good/fair/poor")
    sleep_time = Column(DateTime, comment="入睡时间")
    wake_time = Column(DateTime, comment="起床时间")
    record_date = Column(Date, nullable=False, index=True, comment="记录日期")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
