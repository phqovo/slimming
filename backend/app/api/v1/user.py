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
    - 预计达到目标需要的天数
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
    
    # 5. 根据历史趋势计算预计达到目标需要的天数
    estimated_days_to_goal = None
    if current_user.target_weight and weight_to_goal and weight_to_goal > 0:
        # 智能选择时间范围：根据用户记录频率动态调整
        all_records = db.query(WeightRecord).filter(
            WeightRecord.user_id == current_user.id
        ).order_by(WeightRecord.record_date.asc()).all()
        
        # 至少需要3条记录才能计算趋势
        if len(all_records) >= 3:
            # 计算用户的记录频率（总记录数 / 总天数）
            first_date = all_records[0].record_date
            last_date = all_records[-1].record_date
            total_days = (last_date - first_date).days
            
            if total_days > 0:
                record_frequency = len(all_records) / total_days  # 每天平均记录次数
                
                # 根据记录频率选择数据范围：
                # - 如果记录频率 >= 0.7（约每天都记录），使用最近60天数据
                # - 如果记录频率 >= 0.4（约2-3天记录一次），使用最近45天数据
                # - 否则使用最近30天数据
                if record_frequency >= 0.7:
                    days_range = 60  # 频繁记录用户，用更多数据
                elif record_frequency >= 0.4:
                    days_range = 45  # 中等频率用户
                else:
                    days_range = 30  # 低频率用户
                
                # 获取指定时间范围的记录
                range_records = db.query(WeightRecord).filter(
                    WeightRecord.user_id == current_user.id,
                    WeightRecord.record_date >= today - timedelta(days=days_range)
                ).order_by(WeightRecord.record_date.asc()).all()
                
                # 如果范围内记录少于5条，回退到全部数据
                if len(range_records) >= 5:
                    records_to_use = range_records
                else:
                    # 数据太少，用全部历史数据
                    records_to_use = all_records if len(all_records) >= 5 else None
            else:
                # 所有记录在同一天，无法计算
                records_to_use = None
            
            # 计算平均每天的体重变化率
            if records_to_use and len(records_to_use) >= 5:
                start_weight = records_to_use[0].weight
                end_weight = records_to_use[-1].weight
                days_span = (records_to_use[-1].record_date - records_to_use[0].record_date).days
                
                if days_span > 0:
                    daily_change = (end_weight - start_weight) / days_span  # 负数表示在减重
                    
                    # 如果趋势是在减重（daily_change < 0）
                    if daily_change < 0:
                        # 预计还需要多少天
                        estimated_days_to_goal = int(abs(weight_to_goal / daily_change))
                        # 限制在合理范围内（1-1000天）
                        if estimated_days_to_goal < 1:
                            estimated_days_to_goal = 1
                        elif estimated_days_to_goal > 1000:
                            estimated_days_to_goal = None  # 太久了，不显示
    
    return {
        "code": 200,
        "data": {
            "current_weight": current_weight,
            "target_weight": current_user.target_weight,
            "weight_change": weight_change,  # 相比昨天的变化（kg）
            "weight_change_date": weight_change_date,  # 对比的日期
            "weight_lost": weight_lost,  # 已减去的体重（kg）
            "weight_to_goal": weight_to_goal,  # 距离目标还有多少（kg）
            "days_elapsed": days_elapsed,  # 耗时天数
            "estimated_days_to_goal": estimated_days_to_goal  # 预计达到目标需要的天数
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
