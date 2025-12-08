"""数据同步配置和日志模型"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.sql import func
from app.core.database import Base


class DataSyncConfig(Base):
    """数据同步配置表"""
    __tablename__ = "data_sync_config"

    id = Column(Integer, primary_key=True, index=True, comment="主键ID")
    user_id = Column(Integer, nullable=False, comment="用户ID")
    data_source = Column(String(50), nullable=False, comment="数据来源")
    data_type = Column(String(50), nullable=False, comment="数据类型")
    enabled = Column(Boolean, default=False, nullable=False, comment="是否启用定时同步")
    interval_seconds = Column(Integer, default=3600, nullable=False, comment="同步间隔（秒）")
    schedule_type = Column(String(20), default='interval', nullable=False, comment="调度类型：interval=间隔执行, cron=每天定时")
    cron_hour = Column(Integer, nullable=True, comment="每天执行的小时（0-23），仅schedule_type=cron时有效")
    cron_minute = Column(Integer, default=0, nullable=False, comment="每天执行的分钟（0-59），仅schedule_type=cron时有效")
    sync_days = Column(Integer, default=30, nullable=False, comment="自动同步天数（0表示全部数据）")
    sync_yesterday = Column(Boolean, default=False, nullable=False, comment="是否同步昨天数据（True=昨天整天，False=往前推N天）")
    last_sync_time = Column(DateTime, nullable=True, comment="最后同步时间")
    auto_sync_to_local = Column(Boolean, default=False, nullable=False, comment="是否自动同步到本地库")
    sync_weight = Column(Boolean, default=False, nullable=False, comment="同步体重数据")
    sync_sleep = Column(Boolean, default=False, nullable=False, comment="同步睡眠数据")
    sync_exercise = Column(Boolean, default=False, nullable=False, comment="同步锻炼数据")
    created_at = Column(DateTime, server_default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间")


class DataSyncLog(Base):
    """数据拉取日志表"""
    __tablename__ = "data_sync_log"

    id = Column(Integer, primary_key=True, index=True, comment="主键ID")
    user_id = Column(Integer, nullable=False, comment="用户ID")
    data_source = Column(String(50), nullable=False, comment="数据来源")
    data_type = Column(String(50), nullable=False, comment="数据类型")
    sync_type = Column(String(20), nullable=False, comment="同步类型（manual/auto）")
    status = Column(String(20), nullable=False, comment="状态（running/success/failed）")
    start_time = Column(DateTime, nullable=False, comment="开始时间")
    end_time = Column(DateTime, nullable=True, comment="结束时间")
    duration = Column(Integer, nullable=True, comment="耗时（毫秒）")
    data_count = Column(Integer, nullable=True, comment="数据条数")
    error_message = Column(Text, nullable=True, comment="错误信息")
    created_at = Column(DateTime, server_default=func.now(), nullable=False, comment="创建时间")
