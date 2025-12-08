from sqlalchemy import Column, Integer, String, DateTime, Float, Text
from sqlalchemy.sql import func
from app.core.database import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String(20), unique=True, index=True, nullable=True, comment="手机号（可为空）")
    nickname = Column(String(50), default="", comment="昵称")
    avatar = Column(String(255), default="", comment="头像URL")
    
    # 第三方登录字段
    wechat_openid = Column(String(100), unique=True, nullable=True, comment="微信openid")
    wechat_unionid = Column(String(100), nullable=True, comment="微信unionid")
    qq_openid = Column(String(100), unique=True, nullable=True, comment="QQ openid")
    qq_nickname = Column(String(100), nullable=True, comment="QQ昵称")
    wechat_nickname = Column(String(100), nullable=True, comment="微信昵称")
    oauth_avatar = Column(String(500), nullable=True, comment="第三方原始头像URL")
    
    age = Column(Integer, default=0, comment="年龄")
    gender = Column(String(10), default="", comment="性别：male/female")
    height = Column(Float, default=0.0, comment="身高(cm)")
    target_weight = Column(Float, default=0.0, comment="目标体重(kg)")
    current_weight = Column(Float, default=0.0, comment="当前体重(kg)")
    bmi = Column(Float, default=0.0, comment="BMI指数")
    bmr = Column(Float, default=0.0, comment="基础代谢率(kcal/天)")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
