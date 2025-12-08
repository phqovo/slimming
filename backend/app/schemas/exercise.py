from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional


class ExerciseRecordBase(BaseModel):
    exercise_type: str = Field(..., description="运动类型")
    duration: int = Field(..., description="运动时长(分钟)")
    calories: Optional[float] = Field(0.0, description="消耗卡路里")
    distance: Optional[float] = Field(0.0, description="运动距离")
    image_url: Optional[str] = Field("", description="运动图片URL")
    note: Optional[str] = Field("", description="备注")
    record_date: date = Field(..., description="记录日期")


class ExerciseRecordCreate(ExerciseRecordBase):
    pass


class ExerciseRecordUpdate(BaseModel):
    exercise_type: Optional[str] = None
    duration: Optional[int] = None
    calories: Optional[float] = None
    distance: Optional[float] = None
    image_url: Optional[str] = None
    note: Optional[str] = None
    record_date: Optional[date] = None


class ExerciseRecordResponse(ExerciseRecordBase):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True
