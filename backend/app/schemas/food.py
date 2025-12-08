from pydantic import BaseModel, validator
from typing import Optional
from decimal import Decimal
from datetime import datetime


class FoodNutritionBase(BaseModel):
    """食物营养成分基础模型"""
    name: str
    category: Optional[str] = None
    calories: Decimal
    protein: Optional[Decimal] = Decimal('0')
    carbs: Optional[Decimal] = Decimal('0')
    fat: Optional[Decimal] = Decimal('0')
    image_url: Optional[str] = None
    unit: str = "100g"


class FoodNutritionCreate(FoodNutritionBase):
    """创建食物营养信息"""
    external_id: Optional[str] = None
    source: str = "miaofoods"
    is_custom: bool = False


class FoodNutritionUpdate(BaseModel):
    """更新食物营养信息"""
    name: Optional[str] = None
    category: Optional[str] = None
    calories: Optional[Decimal] = None
    protein: Optional[Decimal] = None
    carbs: Optional[Decimal] = None
    fat: Optional[Decimal] = None
    image_url: Optional[str] = None
    unit: Optional[str] = None


class FoodNutritionResponse(FoodNutritionBase):
    """食物营养信息响应"""
    id: int
    external_id: Optional[str]
    source: str
    is_custom: bool
    created_at: str
    updated_at: str
    
    @validator('created_at', 'updated_at', pre=True)
    def datetime_to_str(cls, v):
        if isinstance(v, datetime):
            return v.strftime('%Y-%m-%d %H:%M:%S')
        return v
    
    class Config:
        from_attributes = True
