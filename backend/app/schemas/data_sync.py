"""数据同步配置和日志Schema"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class DataSyncConfigBase(BaseModel):
    """同步配置基础Schema"""
    data_source: str = Field(..., description="数据来源")
    data_type: str = Field(..., description="数据类型")
    enabled: bool = Field(default=False, description="是否启用定时同步")
    interval_seconds: int = Field(default=3600, ge=1, description="同步间隔（秒）")
    schedule_type: str = Field(default='interval', description="调度类型：interval=间隔执行, cron=每天定时")
    cron_hour: Optional[int] = Field(None, ge=0, le=23, description="每天执行的小时（0-23）")
    cron_minute: int = Field(default=0, ge=0, le=59, description="每天执行的分钟（0-59）")
    sync_days: int = Field(default=30, ge=0, le=365, description="自动同步天数（0表示全部数据）")
    sync_yesterday: bool = Field(default=False, description="是否同步昨天数据（True=昨天整天，False=往前推N天）")


class DataSyncConfigCreate(DataSyncConfigBase):
    """创建同步配置"""
    pass


class DataSyncConfigUpdate(BaseModel):
    """更新同步配置"""
    enabled: Optional[bool] = None
    interval_seconds: Optional[int] = Field(None, ge=1)
    schedule_type: Optional[str] = Field(None, description="调度类型")
    cron_hour: Optional[int] = Field(None, ge=0, le=23, description="每天执行的小时")
    cron_minute: Optional[int] = Field(None, ge=0, le=59, description="每天执行的分钟")
    sync_days: Optional[int] = Field(None, ge=0, le=365, description="自动同步天数")
    sync_yesterday: Optional[bool] = Field(None, description="是否同步昨天数据")


class DataSyncConfigResponse(DataSyncConfigBase):
    """同步配置响应"""
    id: int
    user_id: int
    last_sync_time: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DataSyncLogBase(BaseModel):
    """同步日志基础Schema"""
    data_source: str = Field(..., description="数据来源")
    data_type: str = Field(..., description="数据类型")
    sync_type: str = Field(..., description="同步类型（manual/auto）")
    status: str = Field(..., description="状态（running/success/failed）")


class DataSyncLogResponse(DataSyncLogBase):
    """同步日志响应"""
    id: int
    user_id: int
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[int] = None
    data_count: Optional[int] = None
    error_message: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class SyncRequest(BaseModel):
    """手动同步请求"""
    data_source: str = Field(..., description="数据来源")
    data_type: str = Field(..., description="数据类型")
    days: int = Field(default=30, ge=-1, le=365, description="同步最近多少天的数据，-1表示昨天数据，0表示全部数据")
