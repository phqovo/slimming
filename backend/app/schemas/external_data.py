"""外部数据 Schemas"""
from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional, Dict, Any
from decimal import Decimal


# ========== 睡眠记录 ==========
class ExternalSleepRecordResponse(BaseModel):
    id: int
    user_id: int
    data_source: str
    sleep_date: date
    start_time: datetime
    end_time: datetime
    total_duration: Optional[int] = None
    deep_sleep: Optional[int] = None
    light_sleep: Optional[int] = None
    rem_sleep: Optional[int] = None
    awake_time: Optional[int] = None
    sleep_score: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# ========== 锻炼记录 ==========
class ExternalExerciseRecordResponse(BaseModel):
    id: int
    user_id: int
    data_source: str
    exercise_date: date
    start_time: datetime
    end_time: datetime
    exercise_type: Optional[str] = None
    duration: Optional[int] = None
    distance: Optional[Decimal] = None
    calories: Optional[int] = None
    steps: Optional[int] = None
    avg_heart_rate: Optional[int] = None
    max_heart_rate: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# ========== 体重记录 ==========
class ExternalWeightRecordResponse(BaseModel):
    id: int
    user_id: int
    data_source: str
    measure_date: date
    measure_time: datetime
    weight: Decimal
    bmi: Optional[Decimal] = None
    body_fat: Optional[Decimal] = None
    muscle_mass: Optional[Decimal] = None
    bone_mass: Optional[Decimal] = None
    water: Optional[Decimal] = None
    protein: Optional[Decimal] = None
    bmr: Optional[int] = None
    visceral_fat: Optional[Decimal] = None
    body_age: Optional[int] = None
    body_score: Optional[int] = None
    # 八电极秤数据
    body_shape: Optional[int] = None
    fat_mass: Optional[Decimal] = None
    left_lower_limb_fat_mass: Optional[Decimal] = None
    left_lower_limb_fat_rank: Optional[int] = None
    left_lower_limb_muscle_mass: Optional[int] = None
    left_lower_limb_muscle_rank: Optional[int] = None
    left_upper_limb_fat_mass: Optional[Decimal] = None
    left_upper_limb_fat_rank: Optional[int] = None
    left_upper_limb_muscle_mass: Optional[Decimal] = None
    left_upper_limb_muscle_rank: Optional[int] = None
    limbs_fat_balance: Optional[int] = None
    limbs_muscle_balance: Optional[int] = None
    limbs_skeletal_muscle_index: Optional[Decimal] = None
    lower_limb_fat_balance: Optional[int] = None
    lower_limb_muscle_balance: Optional[int] = None
    recommended_calories_intake: Optional[int] = None
    right_lower_limb_fat_mass: Optional[Decimal] = None
    right_lower_limb_fat_rank: Optional[int] = None
    right_lower_limb_muscle_mass: Optional[Decimal] = None
    right_lower_limb_muscle_rank: Optional[int] = None
    right_upper_limb_fat_mass: Optional[Decimal] = None
    right_upper_limb_fat_rank: Optional[int] = None
    right_upper_limb_muscle_mass: Optional[Decimal] = None
    right_upper_limb_muscle_rank: Optional[int] = None
    trunk_fat_mass: Optional[Decimal] = None
    trunk_fat_rank: Optional[int] = None
    trunk_muscle_mass: Optional[Decimal] = None
    trunk_muscle_rank: Optional[int] = None
    upper_limb_fat_balance: Optional[int] = None
    upper_limb_muscle_balance: Optional[int] = None
    note: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# ========== 运动步数 ==========
class ExternalStepRecordResponse(BaseModel):
    id: int
    user_id: int
    data_source: str
    step_date: date
    steps: int
    distance: Optional[Decimal] = None
    calories: Optional[int] = None
    active_time: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# ========== 通用列表响应 ==========
class ExternalDataListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int
    items: list
