from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    phone: str = Field(..., description="手机号")
    nickname: Optional[str] = Field("", description="昵称")
    avatar: Optional[str] = Field("", description="头像URL")
    age: Optional[int] = Field(0, description="年龄")
    gender: Optional[str] = Field("", description="性别")
    height: Optional[float] = Field(0.0, description="身高")
    target_weight: Optional[float] = Field(0.0, description="目标体重")
    current_weight: Optional[float] = Field(0.0, description="当前体重")
    bmi: Optional[float] = Field(0.0, description="BMI指数")
    bmr: Optional[float] = Field(0.0, description="基础代谢率")


class UserCreate(BaseModel):
    phone: str = Field(..., description="手机号")


class UserUpdate(BaseModel):
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    height: Optional[float] = None
    target_weight: Optional[float] = None
    current_weight: Optional[float] = None


class UserResponse(BaseModel):
    id: int
    phone: Optional[str] = None  # QQ/微信登录的用户可能没有手机号
    nickname: str
    avatar: str
    age: int
    gender: str
    height: float
    target_weight: float
    current_weight: float
    bmi: float
    bmr: float
    created_at: datetime
    
    # 第三方账号信息
    qq_openid: Optional[str] = None
    qq_nickname: Optional[str] = None
    wechat_openid: Optional[str] = None
    wechat_nickname: Optional[str] = None
    oauth_avatar: Optional[str] = None
    
    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    phone: str = Field(..., description="手机号")
    code: str = Field(..., description="验证码")
    device_id: Optional[str] = Field(None, description="设备ID，用于多设备登录")


class SendCodeRequest(BaseModel):
    phone: str = Field(..., description="手机号")


class LoginResponse(BaseModel):
    token: str
    user: UserResponse
