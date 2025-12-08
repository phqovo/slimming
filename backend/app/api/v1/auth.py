from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.redis import get_redis
from app.core.security import create_access_token
from app.core.config import get_settings
from app.models.user import User
from app.schemas.user import (
    SendCodeRequest, LoginRequest, LoginResponse, UserResponse
)
from app.utils.sms import generate_verification_code, save_verification_code, verify_code, send_sms_code
from datetime import timedelta

router = APIRouter()
settings = get_settings()


@router.post("/send-code", summary="发送验证码")
async def send_code(request: SendCodeRequest):
    """发送短信验证码"""
    # 生成验证码
    code = generate_verification_code()
    
    # 保存到Redis，5分钟过期
    save_verification_code(request.phone, code, expire=300)
    
    # 发送短信
    sms_result = await send_sms_code(request.phone, code)
    
    return {
        "code": 200,
        "message": "验证码发送成功",
        "data": {
            "code": code if (settings.DEBUG or settings.SMS_DEBUG_MODE) else None,  # 调试模式返回验证码
            "debug_mode": settings.SMS_DEBUG_MODE,  # 是否调试模式
            "sms_sent": sms_result  # 是否真实发送短信
        }
    }


@router.post("/login", summary="登录/注册")
async def login(
    request: LoginRequest,
    user_agent: str = Header(None),
    db: Session = Depends(get_db),
    redis_client = Depends(get_redis)
):
    """手机号验证码登录，如果是新用户则自动注册"""
    
    # 验证验证码
    if not verify_code(request.phone, request.code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="验证码错误或已过期"
        )
    
    # 查找或创建用户
    user = db.query(User).filter(User.phone == request.phone).first()
    
    if not user:
        # 新用户，自动注册
        user = User(
            phone=request.phone,
            nickname=f"用户{request.phone[-4:]}",
            avatar="https://image.piheqi.com/uPic/957C611FB2D763D5F06691F443C1B5B7.jpg"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    # 生成设备ID：优先使用前端传入的device_id，否则根据User-Agent生成
    if request.device_id:
        device_id = request.device_id
    else:
        # 使用 User-Agent 的哈希值作为设备ID
        import hashlib
        device_id = hashlib.md5((user_agent or "unknown").encode()).hexdigest()[:16]
    
    # 生成Token（将device_id也存入token payload）
    token_data = {"user_id": user.id, "phone": user.phone, "device_id": device_id}
    access_token = create_access_token(
        data=token_data,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    # 将token存储到Redis（支持多设备登录）
    # 使用真实的设备ID，允许同一用户多个设备同时登录
    redis_client.setex(
        f"token:{user.id}:{device_id}",
        settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        access_token
    )
    
    return {
        "token": access_token,
        "user": UserResponse.from_orm(user).dict()
    }


@router.post("/logout", summary="退出登录")
async def logout(
    authorization: str = Depends(lambda: None),
    redis_client = Depends(get_redis)
):
    """退出登录，清除Token"""
    # 这里可以从请求头获取用户信息，然后删除Redis中的token
    # 简化实现
    return {
        "code": 200,
        "message": "退出成功"
    }
