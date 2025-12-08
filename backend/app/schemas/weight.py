from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional


class WeightRecordBase(BaseModel):
    weight: float = Field(..., description="体重")
    morning_weight: Optional[float] = Field(None, description="早晨体重")
    evening_weight: Optional[float] = Field(None, description="睡前体重")
    body_fat: Optional[float] = Field(0.0, description="体脂率")
    record_date: date = Field(..., description="记录日期")
    note: Optional[str] = Field("", description="备注")


class WeightRecordCreate(WeightRecordBase):
    pass


class WeightRecordUpdate(BaseModel):
    weight: Optional[float] = None
    body_fat: Optional[float] = None
    record_date: Optional[date] = None
    note: Optional[str] = None


class WeightRecordResponse(WeightRecordBase):
    id: int
    user_id: int
    bmi: float
    created_at: datetime
    
    class Config:
        from_attributes = True


class WeightPrediction(BaseModel):
    date: date
    predicted_weight: float
    confidence_interval_lower: Optional[float] = None
    confidence_interval_upper: Optional[float] = None


class WeightTrendRequest(BaseModel):
    days: int = Field(7, description="预测天数：7/30/90")
