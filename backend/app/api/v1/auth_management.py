from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.auth_management import AuthManagement
from app.schemas.auth_management import (
    AuthManagementCreate,
    AuthManagementUpdate,
    AuthManagementResponse,
    AuthManagementListResponse,
    AuthVerifyRequest
)
from app.services.xiaomi_auth import XiaomiAuth
from typing import Optional
from datetime import datetime
import math
import traceback

router = APIRouter()


@router.get("/", response_model=AuthManagementListResponse, summary="获取授权列表")
async def get_auth_list(
    page: int = 1,
    page_size: int = 10,
    auth_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取当前用户的授权列表（分页）"""
    # 构建查询
    query = db.query(AuthManagement).filter(AuthManagement.user_id == current_user.id)
    
    # 按类型筛选
    if auth_type:
        query = query.filter(AuthManagement.auth_type == auth_type)
    
    # 计算总数
    total = query.count()
    
    # 分页
    query = query.order_by(AuthManagement.created_at.desc())
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": math.ceil(total / page_size) if total > 0 else 0,
        "items": items
    }


@router.post("/verify", summary="验证授权")
async def verify_auth(
    verify_data: AuthVerifyRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """验证小米运动健康账号密码，生成token"""
    xiaomi_auth = None
    try:
        # 创建小米认证实例
        xiaomi_auth = XiaomiAuth(app_type="miothealth")
        
        # 执行登录
        result = xiaomi_auth.login(verify_data.account, verify_data.password)
        
        # 检查是否需要二次验证
        if result.get('need_verify'):
            return {
                "success": True,
                "need_verify": True,
                "notification_url": result['notification_url'],
                "message": result['message']
            }
        
        return {
            "success": True,
            "need_verify": False,
            "message": "验证成功",
            "data": {
                "token": result['token'],
                "user_id": result['user_id'],
                "ssecurity": result['ssecurity'],
                "cookies": result['cookies']
            }
        }
    except Exception as e:
        error_msg = str(e)
        print(f"小米登录失败: {error_msg}")
        print(traceback.format_exc())
        return {
            "success": False,
            "need_verify": False,
            "message": f"验证失败: {error_msg}",
            "data": None
        }
    finally:
        if xiaomi_auth:
            xiaomi_auth.close()


@router.post("/", response_model=AuthManagementResponse, summary="新增授权")
async def create_auth(
    auth_data: AuthManagementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """新增授权配置（同一用户同一类型不能重复）"""
    try:
        # 创建授权记录（状态为未验证）
        auth = AuthManagement(
            user_id=current_user.id,
            status=0,  # 未验证
            **auth_data.dict()
        )
        db.add(auth)
        db.commit()
        db.refresh(auth)
        return auth
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该类型授权已存在，不能重复添加"
        )


@router.get("/{auth_id}", response_model=AuthManagementResponse, summary="获取授权详情")
async def get_auth_detail(
    auth_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取授权详情"""
    auth = db.query(AuthManagement).filter(
        AuthManagement.id == auth_id,
        AuthManagement.user_id == current_user.id
    ).first()
    
    if not auth:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="授权记录不存在"
        )
    
    return auth


@router.put("/{auth_id}", response_model=AuthManagementResponse, summary="更新授权")
async def update_auth(
    auth_id: int,
    auth_data: AuthManagementUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新授权配置"""
    auth = db.query(AuthManagement).filter(
        AuthManagement.id == auth_id,
        AuthManagement.user_id == current_user.id
    ).first()
    
    if not auth:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="授权记录不存在"
        )
    
    # 更新字段
    update_data = auth_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(auth, field, value)
    
    # 如果修改了账号或密码，重置验证状态
    if 'account' in update_data or 'password' in update_data:
        auth.status = 0
        auth.token = None
        auth.ssecurity = None
        auth.cookies = None
        auth.last_verify_time = None
        auth.error_message = None
    
    db.commit()
    db.refresh(auth)
    return auth


@router.post("/{auth_id}/verify-and-save", response_model=AuthManagementResponse, summary="验证并保存Token")
async def verify_and_save_token(
    auth_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """验证授权并保存Token到数据库"""
    auth = db.query(AuthManagement).filter(
        AuthManagement.id == auth_id,
        AuthManagement.user_id == current_user.id
    ).first()
    
    if not auth:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="授权记录不存在"
        )
    
    xiaomi_auth = None
    try:
        # 创建小米认证实例
        xiaomi_auth = XiaomiAuth(app_type="miothealth")
        
        # 执行登录（不传callback_url）
        result = xiaomi_auth.login(auth.account, auth.password)
        
        # 检查是否需要二次验证
        if result.get('need_verify'):
            # 更新状态为等待验证
            auth.status = 0  # 未验证
            auth.last_verify_time = datetime.now()
            auth.error_message = result['message']
            db.commit()
            
            raise HTTPException(
                status_code=status.HTTP_202_ACCEPTED,
                detail={
                    "need_verify": True,
                    "notification_url": result['notification_url'],
                    "message": result['message']
                }
            )
        
        # 更新授权记录
        auth.token = result['token']
        auth.ssecurity = result['ssecurity']
        auth.cookies = result['cookies']
        auth.status = 1  # 验证成功
        auth.last_verify_time = datetime.now()
        auth.error_message = None
        
        db.commit()
        db.refresh(auth)
        
        return auth
    except HTTPException:
        raise
    except Exception as e:
        # 验证失败
        error_msg = str(e)
        auth.status = 2  # 验证失败
        auth.last_verify_time = datetime.now()
        auth.error_message = error_msg[:500] if len(error_msg) > 500 else error_msg
        
        db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"验证失败: {error_msg}"
        )
    finally:
        if xiaomi_auth:
            xiaomi_auth.close()


@router.post("/{auth_id}/check-verify-status", summary="检查验证状态")
async def check_verify_status(
    auth_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """检查二次验证状态（轮询）"""
    # 直接调用 verify_and_save_token，它会检查验证状态
    return await verify_and_save_token(auth_id, db, current_user)


@router.delete("/{auth_id}", summary="删除授权")
async def delete_auth(
    auth_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除授权配置"""
    auth = db.query(AuthManagement).filter(
        AuthManagement.id == auth_id,
        AuthManagement.user_id == current_user.id
    ).first()
    
    if not auth:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="授权记录不存在"
        )
    
    db.delete(auth)
    db.commit()
    
    return {"message": "删除成功"}
