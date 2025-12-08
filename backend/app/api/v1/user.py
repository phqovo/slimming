from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate
from app.api.deps import get_current_user
from app.utils.storage import upload_file
from app.utils.health_calculator import update_user_health_stats
from pydantic import BaseModel
import os
from datetime import datetime

router = APIRouter()


@router.get("/me", response_model=UserResponse, summary="获取当前用户信息")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """获取当前登录用户的信息"""
    return UserResponse.from_orm(current_user).dict()


@router.put("/me", response_model=UserResponse, summary="更新用户信息")
async def update_user_info(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新用户信息"""
    from app.utils.health_calculator import calculate_bmi, calculate_bmr
    
    # 更新用户信息
    for field, value in user_update.dict(exclude_unset=True).items():
        setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    
    # 如果更新了当前体重或影响BMI/BMR的字段，重新计算
    update_fields = user_update.dict(exclude_unset=True)
    if 'current_weight' in update_fields or any(field in update_fields for field in ['height', 'age', 'gender']):
        # 重新计算 BMI
        if current_user.current_weight > 0 and current_user.height > 0:
            current_user.bmi = calculate_bmi(current_user.current_weight, current_user.height)
        
        # 重新计算 BMR
        if current_user.current_weight > 0 and current_user.height > 0 and current_user.age > 0:
            current_user.bmr = calculate_bmr(
                current_user.current_weight,
                current_user.height,
                current_user.age,
                current_user.gender
            )
        
        db.commit()
        db.refresh(current_user)
    
    return UserResponse.from_orm(current_user).dict()


@router.post("/upload-avatar", summary="上传头像")
async def upload_avatar(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """上传用户头像（支持本地/七牛云）"""
    # 检查文件类型
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只支持上传图片文件"
        )
    
    # 读取文件数据
    file_data = await file.read()
    
    # 获取文件扩展名
    file_ext = os.path.splitext(file.filename)[1]
    
    # 上传文件（自动根据配置选择存储方式）
    result = await upload_file(file_data, file_ext, folder="avatars/")
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"上传失败: {result.get('error', '未知错误')}"
        )
    
    # 更新用户头像URL
    avatar_url = result["url"]
    current_user.avatar = avatar_url
    db.commit()
    
    return {
        "code": 200,
        "message": "上传成功",
        "data": {"avatar_url": avatar_url}
    }


@router.get("/stats", summary="获取用户统计信息")
async def get_user_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取用户的统计信息（BMI、基础代谢等）直接从用户表读取"""
    return {
        "code": 200,
        "data": {
            "bmi": current_user.bmi,
            "bmr": current_user.bmr,
            "current_weight": current_user.current_weight,
            "target_weight": current_user.target_weight,
            "height": current_user.height
        }
    }


@router.get("/progress", summary="获取减肥进度信息")
async def get_weight_progress(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取减肥进度信息：
    - 相比昨天的体重变化
    - 已减去的体重
    - 距离目标还有多少
    - 耗时天数
    """
    from app.models.weight import WeightRecord
    from datetime import date, timedelta
    
    today = date.today()
    
    # 1. 获取今天的体重记录
    today_record = db.query(WeightRecord).filter(
        WeightRecord.user_id == current_user.id,
        WeightRecord.record_date == today
    ).first()
    
    # 如果今天有记录，使用今天的；否则使用用户表的当前体重
    current_weight = today_record.weight if today_record else current_user.current_weight
    
    # 2. 获取昨天或更早的体重记录（用于比较）
    yesterday_or_before = db.query(WeightRecord).filter(
        WeightRecord.user_id == current_user.id,
        WeightRecord.record_date < today
    ).order_by(WeightRecord.record_date.desc()).first()
    
    # 计算相比昨天（或上次记录）的变化
    weight_change = None
    weight_change_date = None
    if yesterday_or_before:
        weight_change = current_weight - yesterday_or_before.weight
        weight_change_date = yesterday_or_before.record_date.isoformat()
    
    # 3. 获取最早的体重记录（作为起始体重）
    first_record = db.query(WeightRecord).filter(
        WeightRecord.user_id == current_user.id
    ).order_by(WeightRecord.record_date.asc()).first()
    
    # 计算已减去的体重和耗时
    weight_lost = None
    days_elapsed = None
    if first_record:
        weight_lost = first_record.weight - current_weight  # 正数表示减重，负数表示增重
        days_elapsed = (today - first_record.record_date).days
    
    # 4. 计算距离目标还有多少
    weight_to_goal = None
    if current_user.target_weight:
        weight_to_goal = current_weight - current_user.target_weight
    
    return {
        "code": 200,
        "data": {
            "current_weight": current_weight,
            "target_weight": current_user.target_weight,
            "weight_change": weight_change,  # 相比昨天的变化（kg）
            "weight_change_date": weight_change_date,  # 对比的日期
            "weight_lost": weight_lost,  # 已减去的体重（kg）
            "weight_to_goal": weight_to_goal,  # 距离目标还有多少（kg）
            "days_elapsed": days_elapsed  # 耗时天数
        }
    }


# 绑定/解绑相关Schema
class BindPhoneRequest(BaseModel):
    phone: str
    code: str


class UnbindRequest(BaseModel):
    account_type: str  # phone, qq, wechat


@router.post("/bind/phone", summary="绑定手机号")
async def bind_phone(
    request: BindPhoneRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """绑定手机号（需要验证码）"""
    from app.core.redis import get_redis
    redis_client = get_redis()
    
    # 1. 验证验证码
    stored_code = redis_client.get(f"sms_code:{request.phone}")
    if not stored_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="验证码已过期"
        )
    
    if stored_code != request.code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="验证码错误"
        )
    
    # 2. 检查手机号是否已被其他用户绑定
    existing_user = db.query(User).filter(
        User.phone == request.phone,
        User.id != current_user.id
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该手机号已被其他用户绑定"
        )
    
    # 3. 绑定手机号
    current_user.phone = request.phone
    db.commit()
    
    # 4. 删除验证码
    redis_client.delete(f"sms_code:{request.phone}")
    
    return {"message": "绑定成功"}


@router.post("/unbind", summary="解绑账号")
async def unbind_account(
    request: UnbindRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """解绑账号（手机/QQ/微信）"""
    
    # 1. 检查至少保疙1个绑定方式
    has_phone = bool(current_user.phone)
    has_qq = bool(current_user.qq_openid)
    has_wechat = bool(current_user.wechat_openid)
    
    bind_count = sum([has_phone, has_qq, has_wechat])
    
    if bind_count <= 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="至少需要保疙1个绑定方式"
        )
    
    # 2. 根据类型解绑
    if request.account_type == "phone":
        if not has_phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="未绑定手机号"
            )
        current_user.phone = None
    elif request.account_type == "qq":
        if not has_qq:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="未绑定QQ号"
            )
        current_user.qq_openid = None
    elif request.account_type == "wechat":
        if not has_wechat:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="未绑定微信号"
            )
        current_user.wechat_openid = None
        current_user.wechat_unionid = None
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的账号类型"
        )
    
    db.commit()
    
    return {"message": "解绑成功"}
