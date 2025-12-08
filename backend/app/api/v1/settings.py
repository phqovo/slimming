from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.models.user_settings import UserSettings
from app.schemas.user_settings import UserSettingsResponse, UserSettingsUpdate
from app.api.deps import get_current_user

router = APIRouter()


@router.get("/", response_model=UserSettingsResponse, summary="获取用户设置")
async def get_user_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取当前用户的设置，如果不存在则返回默认值"""
    settings = db.query(UserSettings).filter(
        UserSettings.user_id == current_user.id
    ).first()
    
    if not settings:
        # 不存在则创建默认设置
        settings = UserSettings(
            user_id=current_user.id,
            weight_unit="kg",
            data_public=False,
            auto_sync_to_local=False,
            sync_weight=False,
            sync_sleep=False,
            sync_exercise=False
        )
        db.add(settings)
        db.commit()
        db.refresh(settings)
    
    return UserSettingsResponse.from_orm(settings).dict()


@router.put("/", response_model=UserSettingsResponse, summary="更新用户设置")
async def update_user_settings(
    settings_update: UserSettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新用户设置"""
    settings = db.query(UserSettings).filter(
        UserSettings.user_id == current_user.id
    ).first()
    
    if not settings:
        # 不存在则创建
        settings = UserSettings(
            user_id=current_user.id,
            weight_unit=settings_update.weight_unit or "kg",
            auto_sync_to_local=settings_update.auto_sync_to_local or False,
            sync_weight=settings_update.sync_weight or False,
            sync_sleep=settings_update.sync_sleep or False,
            sync_exercise=settings_update.sync_exercise or False
        )
        db.add(settings)
    else:
        # 存在则更新
        if settings_update.weight_unit is not None:
            settings.weight_unit = settings_update.weight_unit  # pyright: ignore[reportAttributeAccessIssue]
        if settings_update.data_public is not None:
            settings.data_public = settings_update.data_public  # pyright: ignore[reportAttributeAccessIssue]
        if settings_update.auto_sync_to_local is not None:
            settings.auto_sync_to_local = settings_update.auto_sync_to_local  # pyright: ignore[reportAttributeAccessIssue]
        if settings_update.sync_weight is not None:
            settings.sync_weight = settings_update.sync_weight  # pyright: ignore[reportAttributeAccessIssue]
        if settings_update.sync_sleep is not None:
            settings.sync_sleep = settings_update.sync_sleep  # pyright: ignore[reportAttributeAccessIssue]
        if settings_update.sync_exercise is not None:
            settings.sync_exercise = settings_update.sync_exercise  # pyright: ignore[reportAttributeAccessIssue]
    
    db.commit()
    db.refresh(settings)
    
    return UserSettingsResponse.from_orm(settings).dict()
