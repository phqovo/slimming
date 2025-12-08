from pydantic import BaseModel, Field
from typing import Optional


class UserSettingsBase(BaseModel):
    weight_unit: str = Field("kg", description="体重单位：kg/jin")
    data_public: bool = False
    auto_sync_to_local: bool = False
    sync_weight: bool = False
    sync_sleep: bool = False
    sync_exercise: bool = False


class UserSettingsCreate(UserSettingsBase):
    pass


class UserSettingsUpdate(BaseModel):
    weight_unit: Optional[str] = None
    data_public: Optional[bool] = None
    auto_sync_to_local: Optional[bool] = None
    sync_weight: Optional[bool] = None
    sync_sleep: Optional[bool] = None
    sync_exercise: Optional[bool] = None


class UserSettingsResponse(UserSettingsBase):
    id: int
    user_id: int
    
    class Config:
        from_attributes = True
