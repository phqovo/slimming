from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional


class DietRecordBase(BaseModel):
    meal_type: str = Field(..., description="餐次")
    food_name: str = Field(..., description="食物名称")
    calories: Optional[float] = Field(0.0, description="卡路里")
    protein: Optional[float] = Field(0.0, description="蛋白质")
    carbs: Optional[float] = Field(0.0, description="碳水化合物")
    fat: Optional[float] = Field(0.0, description="脂肪")
    portion: Optional[str] = Field("", description="份量")
    note: Optional[str] = Field("", description="备注")
    record_date: date = Field(..., description="记录日期")


class DietRecordCreate(DietRecordBase):
    pass


class DietRecordUpdate(BaseModel):
    meal_type: Optional[str] = None
    food_name: Optional[str] = None
    calories: Optional[float] = None
    protein: Optional[float] = None
    carbs: Optional[float] = None
    fat: Optional[float] = None
    portion: Optional[str] = None
    note: Optional[str] = None
    record_date: Optional[date] = None


class DietRecordResponse(DietRecordBase):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True
