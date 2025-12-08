"""数据同步配置API"""
from fastapi import APIRouter, Depends, Query, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.data_sync import DataSyncConfig, DataSyncLog
from app.schemas.data_sync import (
    DataSyncConfigCreate,
    DataSyncConfigUpdate,
    DataSyncConfigResponse,
    DataSyncLogResponse,
    SyncRequest
)
from app.services.data_sync_service import DataSyncService
from app.services.scheduler_service import scheduler_service
from typing import List, Optional
from datetime import date
import math
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/configs", summary="获取同步配置列表")
async def get_sync_configs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[DataSyncConfigResponse]:
    """获取用户的所有同步配置"""
    configs = db.query(DataSyncConfig).filter(
        DataSyncConfig.user_id == current_user.id
    ).all()
    return configs


@router.post("/configs", summary="创建同步配置")
async def create_sync_config(
    config_data: DataSyncConfigCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> DataSyncConfigResponse:
    """创建新的同步配置"""
    # 检查是否已存在相同的配置
    exists = db.query(DataSyncConfig).filter(
        and_(
            DataSyncConfig.user_id == current_user.id,
            DataSyncConfig.data_source == config_data.data_source,
            DataSyncConfig.data_type == config_data.data_type
        )
    ).first()
    
    if exists:
        raise HTTPException(status_code=400, detail="该数据类型的同步配置已存在")
    
    # 创建配置
    config = DataSyncConfig(
        user_id=current_user.id,
        data_source=config_data.data_source,
        data_type=config_data.data_type,
        enabled=config_data.enabled,
        interval_seconds=config_data.interval_seconds,
        schedule_type=config_data.schedule_type,
        cron_hour=config_data.cron_hour,
        cron_minute=config_data.cron_minute,
        sync_days=config_data.sync_days,
        sync_yesterday=config_data.sync_yesterday
    )
    db.add(config)
    db.commit()
    db.refresh(config)
    
    # 如果启用，添加定时任务
    if config.enabled:
        scheduler_service.add_job(config)
    
    return config


@router.put("/configs/{config_id}", summary="更新同步配置")
async def update_sync_config(
    config_id: int,
    config_data: DataSyncConfigUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> DataSyncConfigResponse:
    """更新同步配置"""
    config = db.query(DataSyncConfig).filter(
        and_(
            DataSyncConfig.id == config_id,
            DataSyncConfig.user_id == current_user.id
        )
    ).first()
    
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    
    # 更新配置
    if config_data.enabled is not None:
        config.enabled = config_data.enabled  # type: ignore
    if config_data.interval_seconds is not None:
        config.interval_seconds = config_data.interval_seconds  # type: ignore
    if config_data.schedule_type is not None:
        config.schedule_type = config_data.schedule_type  # type: ignore
    if config_data.cron_hour is not None:
        config.cron_hour = config_data.cron_hour  # type: ignore
    if config_data.cron_minute is not None:
        config.cron_minute = config_data.cron_minute  # type: ignore
    if config_data.sync_days is not None:
        config.sync_days = config_data.sync_days  # type: ignore
    if config_data.sync_yesterday is not None:
        config.sync_yesterday = config_data.sync_yesterday  # type: ignore
    
    db.commit()
    db.refresh(config)
    
    # 更新定时任务
    scheduler_service.update_job(config)
    
    return config


@router.delete("/configs/{config_id}", summary="删除同步配置")
async def delete_sync_config(
    config_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除同步配置"""
    config = db.query(DataSyncConfig).filter(
        and_(
            DataSyncConfig.id == config_id,
            DataSyncConfig.user_id == current_user.id
        )
    ).first()
    
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    
    # 移除定时任务
    scheduler_service.remove_job(config.id)
    
    # 删除配置
    db.delete(config)
    db.commit()
    
    return {"message": "删除成功"}


@router.post("/manual-sync", summary="手动同步数据")
async def manual_sync(
    sync_request: SyncRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """手动触发数据同步"""
    logger.info("="*50)
    logger.info("手动同步请求")
    logger.info(f"用户ID: {current_user.id}")
    logger.info(f"数据来源: {sync_request.data_source}")
    logger.info(f"数据类型: {sync_request.data_type}")
    logger.info(f"同步天数: {sync_request.days}")
    logger.info("="*50)
    
    sync_service = DataSyncService(db)
    
    # 检查是否正在同步
    if sync_service.is_syncing(
        current_user.id,
        sync_request.data_source,
        sync_request.data_type
    ):
        raise HTTPException(status_code=409, detail="该数据类型正在同步中，请稍后再试")
    
    # 处理 days=-1 的情况（昨天数据）
    sync_yesterday = sync_request.days == -1
    actual_days = 1 if sync_yesterday else sync_request.days
    
    # 使用后台任务异步同步
    background_tasks.add_task(
        sync_service.sync_data,
        user_id=current_user.id,
        data_source=sync_request.data_source,
        data_type=sync_request.data_type,
        sync_type="manual",
        days=actual_days,
        sync_yesterday=sync_yesterday
    )
    
    return {
        "message": "同步任务已提交，正在后台执行",
        "status": "pending"
    }


@router.get("/sync-status", summary="检查同步状态")
async def check_sync_status(
    data_source: str = Query(..., description="数据来源"),
    data_type: str = Query(..., description="数据类型"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """检查某个数据类型是否正在同步"""
    sync_service = DataSyncService(db)
    is_syncing = sync_service.is_syncing(
        current_user.id,
        data_source,
        data_type
    )
    
    return {"is_syncing": is_syncing}


@router.get("/logs", summary="获取同步日志")
async def get_sync_logs(
    data_source: Optional[str] = Query(None, description="数据来源"),
    data_type: Optional[str] = Query(None, description="数据类型"),
    status: Optional[str] = Query(None, description="状态"),
    start_date: Optional[date] = Query(None, description="开始日期"),
    end_date: Optional[date] = Query(None, description="结束日期"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取同步日志列表"""
    # 构建查询
    query = db.query(DataSyncLog).filter(DataSyncLog.user_id == current_user.id)
    
    # 数据来源筛选
    if data_source:
        query = query.filter(DataSyncLog.data_source == data_source)
    
    # 数据类型筛选
    if data_type:
        query = query.filter(DataSyncLog.data_type == data_type)
    
    # 状态筛选
    if status:
        query = query.filter(DataSyncLog.status == status)
    
    # 时间范围筛选
    if start_date:
        query = query.filter(DataSyncLog.created_at >= start_date)
    if end_date:
        query = query.filter(DataSyncLog.created_at <= end_date)
    
    # 总数
    total = query.count()
    
    # 按创建时间倒序排序
    query = query.order_by(desc(DataSyncLog.created_at))
    
    # 分页
    offset = (page - 1) * page_size
    logs = query.offset(offset).limit(page_size).all()
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": math.ceil(total / page_size) if total > 0 else 0,
        "items": logs
    }
