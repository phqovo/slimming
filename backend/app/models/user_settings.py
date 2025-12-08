from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.sql import func
from app.core.database import Base


class UserSettings(Base):
    __tablename__ = "user_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, comment="用户ID")
    weight_unit = Column(String(10), default="kg", comment="体重单位：kg/jin")
    data_public = Column(Boolean, default=False, nullable=False, comment="数据是否公开")
    auto_sync_to_local = Column(Boolean, default=False, nullable=False, comment="是否自动同步到本地库")
    sync_weight = Column(Boolean, default=False, nullable=False, comment="同步体重数据")
    sync_sleep = Column(Boolean, default=False, nullable=False, comment="同步睡眠数据")
    sync_exercise = Column(Boolean, default=False, nullable=False, comment="同步锻炼数据")
    
    class Config:
        from_attributes = True
