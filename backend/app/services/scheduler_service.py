"""定时任务调度服务"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.data_sync import DataSyncConfig
from app.services.data_sync_service import DataSyncService
from datetime import datetime


class SchedulerService:
    """定时任务调度服务"""
    
    _instance = None
    _scheduler = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._scheduler = BackgroundScheduler()
            cls._instance._scheduler.start()
        return cls._instance
    
    def get_scheduler(self):
        """获取调度器实例"""
        return self._scheduler
    
    def _get_job_id(self, config_id: int) -> str:
        """获取任务ID"""
        return f"sync_job_{config_id}"
    
    def _sync_task(self, config_id: int, user_id: int, data_source: str, data_type: str, sync_days: int, sync_yesterday: bool):
        """定时同步任务"""
        db: Session = next(get_db())
        try:
            sync_service = DataSyncService(db)
            # 执行自动同步，使用配置的同步天数
            sync_service.sync_data(
                user_id=user_id,
                data_source=data_source,
                data_type=data_type,
                sync_type="auto",
                days=sync_days,
                sync_yesterday=sync_yesterday
            )
            
            # 更新最后同步时间
            config = db.query(DataSyncConfig).filter(DataSyncConfig.id == config_id).first()
            if config:
                config.last_sync_time = datetime.now()  # type: ignore
                db.commit()
        finally:
            db.close()
    
    def add_job(self, config: DataSyncConfig):
        """
        添加定时任务
        :param config: 同步配置
        """
        if not config.enabled:
            return
        
        job_id = self._get_job_id(config.id)
        
        # 如果任务已存在，先移除
        if self._scheduler.get_job(job_id):
            self._scheduler.remove_job(job_id)
        
        # 根据调度类型选择触发器
        if config.schedule_type == 'cron':
            # 每天指定时间执行
            cron_hour = config.cron_hour if config.cron_hour is not None else 8
            cron_minute = config.cron_minute if config.cron_minute is not None else 0
            trigger = CronTrigger(
                hour=cron_hour,
                minute=cron_minute
            )
        else:
            # 间隔执行（默认）
            trigger = IntervalTrigger(seconds=config.interval_seconds)
        
        # 添加新任务
        self._scheduler.add_job(
            func=self._sync_task,
            trigger=trigger,
            id=job_id,
            args=[config.id, config.user_id, config.data_source, config.data_type, config.sync_days, config.sync_yesterday],
            replace_existing=True
        )
    
    def remove_job(self, config_id: int):
        """
        移除定时任务
        :param config_id: 配置ID
        """
        job_id = self._get_job_id(config_id)
        if self._scheduler.get_job(job_id):
            self._scheduler.remove_job(job_id)
    
    def update_job(self, config: DataSyncConfig):
        """
        更新定时任务
        :param config: 同步配置
        """
        if config.enabled:
            self.add_job(config)
        else:
            self.remove_job(config.id)
    
    def load_all_jobs(self, db: Session):
        """
        加载所有启用的定时任务
        :param db: 数据库会话
        """
        configs = db.query(DataSyncConfig).filter(DataSyncConfig.enabled == True).all()
        for config in configs:
            self.add_job(config)
    
    def shutdown(self):
        """关闭调度器"""
        if self._scheduler:
            self._scheduler.shutdown()


# 全局调度器实例
scheduler_service = SchedulerService()
