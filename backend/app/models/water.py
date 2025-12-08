from sqlalchemy import Column, Integer, Float, DateTime, Date, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base


class WaterRecord(Base):
    __tablename__ = "water_records"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="用户ID")
    amount = Column(Float, nullable=False, comment="饮水量(ml)")
    record_date = Column(Date, nullable=False, index=True, comment="记录日期")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
