from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.core.redis import get_redis
from app.core.security import verify_token
from app.models.user import User


async def get_current_user(
    authorization: Optional[str] = Header(None),
    user_agent: Optional[str] = Header(None, alias="User-Agent"),
    db: Session = Depends(get_db),
    redis_client = Depends(get_redis)
) -> User:
    """获取当前登录用户"""
    print(f"\n=== 验证Token ===")
    print(f"Authorization Header: {authorization[:50] if authorization else 'None'}...")
    
    if not authorization or not authorization.startswith("Bearer "):
        print("❌ 未提供认证令牌")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未提供认证令牌"
        )
    
    token = authorization.replace("Bearer ", "")
    print(f"Token: {token[:50]}...")
    
    # 验证token
    payload = verify_token(token)
    if not payload:
        print("❌ Token验证失败")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的令牌"
        )
    
    user_id = payload.get("user_id")
    if not user_id:
        print("❌ Token中没有user_id")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的令牌"
        )
    
    print(f"User ID: {user_id}")
    
    # 从 token payload 中获取 device_id，如果没有则用 user_agent 生成（向下兼容旧token）
    device_id = payload.get("device_id")
    if not device_id:
        # 兼容旧版本：如果 token 中没有 device_id，则用 user_agent 生成
        import hashlib
        device_id = hashlib.md5((user_agent or "unknown").encode()).hexdigest()[:16]
        print(f"Device ID (从User-Agent生成): {device_id}")
    else:
        print(f"Device ID (从Token获取): {device_id}")
    
    # 检查Redis中的token（支持多设备登录）
    redis_key = f"token:{user_id}:{device_id}"
    print(f"Redis Key: {redis_key}")
    
    stored_token = redis_client.get(redis_key)
    print(f"Redis中的Token: {stored_token[:50] if stored_token else 'None'}...")
    
    if not stored_token:
        print("❌ Redis中没有找到Token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="令牌已过期或已失效"
        )
    
    if stored_token != token:
        print("❌ Token不匹配")
        print(f"存储的: {stored_token[:50]}...")
        print(f"传入的: {token[:50]}...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="令牌已过期或已失效"
        )
    
    print("✅ Token验证成功")
    
    # 获取用户信息
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        print(f"❌ 用户不存在: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    print(f"✅ 用户信息获取成功: {user.nickname}")
    print(f"===================\n")
    
    return user
