from sqlalchemy import Column, Integer, String, DateTime, Text, SmallInteger, UniqueConstraint, JSON
from sqlalchemy.sql import func
from app.core.database import Base


class AuthManagement(Base):
    """授权管理表"""
    __tablename__ = "auth_management"

    id = Column(Integer, primary_key=True, index=True, comment="主键ID")
    user_id = Column(Integer, nullable=False, index=True, comment="用户ID")
    auth_type = Column(String(50), nullable=False, comment="授权类型")
    account = Column(String(100), nullable=False, comment="账号")
    password = Column(String(255), nullable=False, comment="密码")
    token = Column(Text, comment="登录Token")
    ssecurity = Column(Text, comment="加密密钥")
    cookies = Column(Text, comment="登录Cookies")
    extra_data = Column(JSON, comment="额外数据")
    status = Column(SmallInteger, default=0, comment="状态：0=未验证，1=验证成功，2=验证失败")
    last_verify_time = Column(DateTime, comment="最后验证时间")
    error_message = Column(String(500), comment="错误信息")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    __table_args__ = (
        UniqueConstraint('user_id', 'auth_type', name='uk_user_auth_type'),
        {'comment': '授权管理表'}
    )
