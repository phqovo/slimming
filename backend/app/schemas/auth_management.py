from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any, List


class AuthManagementBase(BaseModel):
    auth_type: str = Field(..., description="授权类型：xiaomi_sport=小米运动健康")
    account: str = Field(..., description="账号")
    password: str = Field(..., description="密码")


class AuthManagementCreate(AuthManagementBase):
    pass


class AuthManagementUpdate(BaseModel):
    account: Optional[str] = None
    password: Optional[str] = None


class AuthManagementResponse(BaseModel):
    id: int
    user_id: int
    auth_type: str
    account: str
    # 密码字段不返回，保护用户隐私
    token: Optional[str] = None
    ssecurity: Optional[str] = None
    cookies: Optional[str] = None
    extra_data: Optional[Dict[str, Any]] = None
    status: int
    last_verify_time: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class AuthManagementListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int
    items: List[AuthManagementResponse]


class AuthVerifyRequest(BaseModel):
    """Token验证请求"""
    account: str = Field(..., description="账号")
    password: str = Field(..., description="密码")
