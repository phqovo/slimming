from pydantic import BaseModel, Field
from typing import Optional


class FoodUnitBase(BaseModel):
    """食物单位基础模型"""
    unit_name: str = Field(..., min_length=1, max_length=20, description="单位名称，如：份、个、只、碗等")
    unit_weight: float = Field(..., gt=0, description="单位重量（克）")
    food_id: int = Field(..., description="食物ID")
    source_type: Optional[str] = Field(default="local", description="食物来源类型（local=本地食物库，online=在线食物库）")


class FoodUnitCreate(FoodUnitBase):
    """创建食物单位请求"""
    pass


class FoodUnitUpdate(BaseModel):
    """更新食物单位请求"""
    unit_name: Optional[str] = Field(None, min_length=1, max_length=20)
    unit_weight: Optional[float] = Field(None, gt=0)


class FoodUnitResponse(FoodUnitBase):
    """食物单位响应"""
    unit_id: str = Field(..., description="单位ID（Redis中的唯一标识）")

    class Config:
        from_attributes = True


class FoodUnitRecordCreate(BaseModel):
    """食物单位转换记录创建请求"""
    food_id: int = Field(..., description="食物ID")
    unit_id: str = Field(..., description="单位ID")
    quantity: int = Field(..., gt=0, description="单位数量")
    total_weight: float = Field(..., description="总重量（克）")
    calories: float = Field(..., ge=0, description="热量（kcal）")
    protein: float = Field(..., ge=0, description="蛋白质（g）")
    carbs: float = Field(..., ge=0, description="碳水（g）")
    fat: float = Field(..., ge=0, description="脚肪（g）")
    source_type: Optional[str] = Field(default="local", description="食物来源类型（local=本地食物库，online=在线食物库）")


class FoodUnitRecordResponse(FoodUnitRecordCreate):
    """食物单位转换记录响应"""
    record_id: str = Field(..., description="记录ID")

    class Config:
        from_attributes = True
