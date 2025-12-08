from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional


class WaterRecordBase(BaseModel):
    amount: float = Field(..., description="饮水量(ml)")
    record_date: date = Field(..., description="记录日期")


class WaterRecordCreate(WaterRecordBase):
    pass


class WaterRecordResponse(WaterRecordBase):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class SleepRecordBase(BaseModel):
    duration: float = Field(..., description="睡眠时长(小时)")
    quality: Optional[str] = Field("", description="睡眠质量")
    sleep_time: Optional[datetime] = Field(None, description="入睡时间")
    wake_time: Optional[datetime] = Field(None, description="起床时间")
    record_date: date = Field(..., description="记录日期")


class SleepRecordCreate(SleepRecordBase):
    pass


class SleepRecordUpdate(BaseModel):
    duration: Optional[float] = None
    quality: Optional[str] = None
    sleep_time: Optional[datetime] = None
    wake_time: Optional[datetime] = None
    record_date: Optional[date] = None


class SleepRecordResponse(SleepRecordBase):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True
