"""数据同步服务 - 整合数据拉取、存储和Redis锁"""
import json
from datetime import datetime, timedelta
from typing import Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.core.redis import get_redis
from app.models.data_sync import DataSyncLog, DataSyncConfig
from app.models.user_settings import UserSettings
from app.models.external_data import (
    ExternalSleepRecord,
    ExternalExerciseRecord,
    ExternalWeightRecord,
    ExternalStepRecord
)
from app.models.auth_management import AuthManagement
from app.services.xiaomi_data_sync import XiaomiDataSyncService
from app.utils.exercise_types import XIAOMI_EXERCISE_TYPE_MAP
import base64


class DataSyncService:
    """数据同步服务"""
    
    LOCK_TIMEOUT = 3600  # Redis锁超时时间（秒），1小时
    
    def __init__(self, db: Session):
        self.db = db
        self.redis = get_redis()
    
    def _get_lock_key(self, user_id: int, data_source: str, data_type: str) -> str:
        """获取Redis锁的key"""
        return f"sync_lock:{user_id}:{data_source}:{data_type}"
    
    def acquire_lock(self, user_id: int, data_source: str, data_type: str) -> bool:
        """
        尝试获取同步锁
        :return: 是否成功获取锁
        """
        lock_key = self._get_lock_key(user_id, data_source, data_type)
        # 使用 SET NX EX 原子操作
        return self.redis.set(lock_key, "1", nx=True, ex=self.LOCK_TIMEOUT)
    
    def release_lock(self, user_id: int, data_source: str, data_type: str):
        """释放同步锁"""
        lock_key = self._get_lock_key(user_id, data_source, data_type)
        self.redis.delete(lock_key)
    
    def is_syncing(self, user_id: int, data_source: str, data_type: str) -> bool:
        """检查是否正在同步"""
        lock_key = self._get_lock_key(user_id, data_source, data_type)
        return self.redis.exists(lock_key) > 0
    
    def create_sync_log(
        self,
        user_id: int,
        data_source: str,
        data_type: str,
        sync_type: str
    ) -> DataSyncLog:
        """创建同步日志"""
        log = DataSyncLog(
            user_id=user_id,
            data_source=data_source,
            data_type=data_type,
            sync_type=sync_type,
            status="running",
            start_time=datetime.now()
        )
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log
    
    def update_sync_log(
        self,
        log_id: int,
        status: str,
        data_count: Optional[int] = None,
        error_message: Optional[str] = None
    ):
        """更新同步日志"""
        log = self.db.query(DataSyncLog).filter(DataSyncLog.id == log_id).first()
        if log:
            log.status = status
            log.end_time = datetime.now()
            log.duration = int((log.end_time - log.start_time).total_seconds() * 1000)
            if data_count is not None:
                log.data_count = data_count
            if error_message:
                log.error_message = error_message
            self.db.commit()
    
    def _get_xiaomi_sync_service(self, user_id: int) -> Optional[XiaomiDataSyncService]:
        """获取小米数据同步服务实例"""
        # 查询用户的小米运动健康授权信息
        auth = self.db.query(AuthManagement).filter(
            and_(
                AuthManagement.user_id == user_id,
                AuthManagement.auth_type == "xiaomi_sport",
                AuthManagement.status == 1
            )
        ).first()
        
        if not auth or not auth.token or not auth.ssecurity:
            return None
        
        return XiaomiDataSyncService(
            token=auth.token,
            ssecurity=auth.ssecurity,
            cookies=auth.cookies or "",
            auth_id=auth.id,  # 传入auth_id用于token刷新
            db_session=self.db  # 传入db会话用于token刷新
        )
    
    def _save_sleep_records(self, user_id: int, records: list) -> int:
        """保存睡眠记录（批量处理）"""
        if not records:
            return 0
        
        # 批量查询已存在的data_hash
        data_hashes = [r.get('data_hash') for r in records]
        existing_hashes = set(
            row[0] for row in self.db.query(ExternalSleepRecord.data_hash)
            .filter(ExternalSleepRecord.data_hash.in_(data_hashes))
            .all()
        )
        
        # 批量准备要插入的数据
        batch_size = 3000
        total_count = 0
        new_records = []
        
        for record in records:
            try:
                # 跳过已存在的记录
                if record.get('data_hash') in existing_hashes:
                    continue
                
                # 使用bedtime作为睡眠开始时间（秒级时间戳）
                start_time = datetime.fromtimestamp(record.get('bedtime', 0))
                # 使用wake_up_time作为睡眠结束时间（秒级时间戳）
                end_time = datetime.fromtimestamp(record.get('wake_up_time', 0))
                
                # 解析数据
                sleep_data = ExternalSleepRecord(
                    user_id=user_id,
                    data_source="xiaomi_sport",
                    data_hash=record.get('data_hash'),
                    sleep_date=start_time.date(),
                    start_time=start_time,
                    end_time=end_time,
                    total_duration=record.get('duration', 0),  # 已经是分钟
                    deep_sleep=record.get('sleep_deep_duration', 0),
                    light_sleep=record.get('sleep_light_duration', 0),
                    rem_sleep=record.get('sleep_rem_duration', 0),
                    awake_time=record.get('sleep_awake_duration', 0),
                    sleep_score=0,  # 小米睡眠数据中没有睡眠分数
                    raw_data=json.dumps(record)
                )
                new_records.append(sleep_data)
                
                # 达到批量大小，执行批量插入
                if len(new_records) >= batch_size:
                    self.db.bulk_save_objects(new_records)
                    self.db.commit()
                    total_count += len(new_records)
                    print(f"已批量保存 {len(new_records)} 条睡眠记录")
                    new_records = []
                    
            except Exception as e:
                print(f"处理睡眠记录失败: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        # 保存剩余的记录
        if new_records:
            self.db.bulk_save_objects(new_records)
            self.db.commit()
            total_count += len(new_records)
            print(f"已批量保存 {len(new_records)} 条睡眠记录")
        
        return total_count
    
    def _save_exercise_records(self, user_id: int, records: list) -> int:
        """保存运动记录（批量处理）"""
        if not records:
            return 0
        
        # 批量查询已存在的data_hash
        data_hashes = [r.get('data_hash') for r in records]
        existing_hashes = set(
            row[0] for row in self.db.query(ExternalExerciseRecord.data_hash)
            .filter(ExternalExerciseRecord.data_hash.in_(data_hashes))
            .all()
        )
        
        # 批量准备要插入的数据
        batch_size = 3000
        total_count = 0
        new_records = []
        
        for record in records:
            try:
                # 跳过已存在的记录
                if record.get('data_hash') in existing_hashes:
                    continue
                
                # 使用start_time和end_time，如果没有end_time则根据duration计算
                start_timestamp = record.get('start_time', record.get('time', 0))
                duration_seconds = record.get('duration', 0)
                end_timestamp = record.get('end_time', start_timestamp + duration_seconds)
                
                # 获取运动类型（英文）并转换为中文
                category = record.get('category', '')
                exercise_type_cn = XIAOMI_EXERCISE_TYPE_MAP.get(category, category)  # 如果找不到映射，保留原始值
                
                exercise_data = ExternalExerciseRecord(
                    user_id=user_id,
                    data_source="xiaomi_sport",
                    data_hash=record.get('data_hash'),
                    exercise_date=datetime.fromtimestamp(start_timestamp).date(),
                    start_time=datetime.fromtimestamp(start_timestamp),
                    end_time=datetime.fromtimestamp(end_timestamp),
                    exercise_type=exercise_type_cn,  # 使用中文类型
                    duration=duration_seconds // 60,  # 转换为分钟
                    distance=record.get('distance', 0),  # 已经是米
                    calories=record.get('calories', 0),
                    steps=record.get('steps', 0),
                    avg_heart_rate=record.get('avg_hrm', 0),  # 小米用avg_hrm
                    max_heart_rate=record.get('max_hrm', 0),  # 小米用max_hrm
                    raw_data=json.dumps(record)
                )
                new_records.append(exercise_data)
                
                # 达到批量大小，执行批量插入
                if len(new_records) >= batch_size:
                    self.db.bulk_save_objects(new_records)
                    self.db.commit()
                    total_count += len(new_records)
                    print(f"已批量保存 {len(new_records)} 条运动记录")
                    new_records = []
                    
            except Exception as e:
                print(f"处理运动记录失败: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        # 保存剩余的记录
        if new_records:
            self.db.bulk_save_objects(new_records)
            self.db.commit()
            total_count += len(new_records)
            print(f"已批量保存 {len(new_records)} 条运动记录")
        
        return total_count
    
    def _save_weight_records(self, user_id: int, records: list) -> int:
        """保存体重记录（批量处理）"""
        if not records:
            return 0
        
        # 批量查询已存在的data_hash
        data_hashes = [r.get('data_hash') for r in records]
        existing_hashes = set(
            row[0] for row in self.db.query(ExternalWeightRecord.data_hash)
            .filter(ExternalWeightRecord.data_hash.in_(data_hashes))
            .all()
        )
        
        # 批量准备要插入的数据
        batch_size = 3000
        total_count = 0
        new_records = []
        
        for record in records:
            try:
                # 跳过已存在的记录
                if record.get('data_hash') in existing_hashes:
                    continue
                
                # 使用time字段作为测量时间（秒级时间戳）
                measure_time = datetime.fromtimestamp(record.get('time', 0))
                
                weight_data = ExternalWeightRecord(
                    user_id=user_id,
                    data_source="xiaomi_sport",
                    data_hash=record.get('data_hash'),
                    measure_date=measure_time.date(),
                    measure_time=measure_time,
                    # 基础体成分数据
                    weight=record.get('weight', 0),
                    bmi=record.get('bmi', 0),
                    body_fat=record.get('body_fat_rate', 0),
                    muscle_mass=record.get('muscle_mass', 0),
                    bone_mass=record.get('bone_mass', 0),
                    water=record.get('body_moisture_mass', 0),
                    protein=record.get('protein_mass', 0),
                    bmr=record.get('basal_metabolism', 0),
                    visceral_fat=record.get('visceral_fat', 0),
                    body_age=record.get('body_age', 0),
                    body_score=record.get('body_score', 0),
                    heart_rate=record.get('bpm', 0),  # 小米返回的心率字段
                    whr=record.get('whr', 0),  # 小米返回的腰臀比字段
                    body_shape=record.get('body_shape'),
                    fat_mass=record.get('fat_mass', 0),
                    # 八电极秤数据 - 左下肢
                    left_lower_limb_fat_mass=record.get('left_lower_limb_fat_mass', 0),
                    left_lower_limb_fat_rank=record.get('left_lower_limb_fat_rank', 0),
                    left_lower_limb_muscle_mass=record.get('left_lower_limb_muscle_mass', 0),
                    left_lower_limb_muscle_rank=record.get('left_lower_limb_muscle_rank', 0),
                    # 八电极秤数据 - 左上肢
                    left_upper_limb_fat_mass=record.get('left_upper_limb_fat_mass', 0),
                    left_upper_limb_fat_rank=record.get('left_upper_limb_fat_rank', 0),
                    left_upper_limb_muscle_mass=record.get('left_upper_limb_muscle_mass', 0),
                    left_upper_limb_muscle_rank=record.get('left_upper_limb_muscle_rank', 0),
                    # 八电极秤数据 - 右下肢
                    right_lower_limb_fat_mass=record.get('right_lower_limb_fat_mass', 0),
                    right_lower_limb_fat_rank=record.get('right_lower_limb_fat_rank', 0),
                    right_lower_limb_muscle_mass=record.get('right_lower_limb_muscle_mass', 0),
                    right_lower_limb_muscle_rank=record.get('right_lower_limb_muscle_rank', 0),
                    # 八电极秤数据 - 右上肢
                    right_upper_limb_fat_mass=record.get('right_upper_limb_fat_mass', 0),
                    right_upper_limb_fat_rank=record.get('right_upper_limb_fat_rank', 0),
                    right_upper_limb_muscle_mass=record.get('right_upper_limb_muscle_mass', 0),
                    right_upper_limb_muscle_rank=record.get('right_upper_limb_muscle_rank', 0),
                    # 八电极秤数据 - 躯干
                    trunk_fat_mass=record.get('trunk_fat_mass', 0),
                    trunk_fat_rank=record.get('trunk_fat_rank', 0),
                    trunk_muscle_mass=record.get('trunk_muscle_mass', 0),
                    trunk_muscle_rank=record.get('trunk_muscle_rank', 0),
                    # 八电极秤数据 - 平衡指标
                    limbs_fat_balance=record.get('limbs_fat_balance', 0),
                    limbs_muscle_balance=record.get('limbs_muscle_balance', 0),
                    limbs_skeletal_muscle_index=record.get('limbs_skeletal_muscle_index', 0),
                    lower_limb_fat_balance=record.get('lower_limb_fat_balance', 0),
                    lower_limb_muscle_balance=record.get('lower_limb_muscle_balance', 0),
                    upper_limb_fat_balance=record.get('upper_limb_fat_balance', 0),
                    upper_limb_muscle_balance=record.get('upper_limb_muscle_balance', 0),
                    # 其他指标
                    recommended_calories_intake=record.get('recommended_calories_intake', 0),
                    raw_data=json.dumps(record)
                )
                new_records.append(weight_data)
                
                # 达到批量大小，执行批量插入
                if len(new_records) >= batch_size:
                    self.db.bulk_save_objects(new_records)
                    self.db.commit()
                    total_count += len(new_records)
                    print(f"已批量保存 {len(new_records)} 条体重记录")
                    new_records = []
                    
            except Exception as e:
                print(f"处理体重记录失败: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        # 保存剩余的记录
        if new_records:
            self.db.bulk_save_objects(new_records)
            self.db.commit()
            total_count += len(new_records)
            print(f"已批量保存 {len(new_records)} 条体重记录")
        
        return total_count
    
    def _save_step_records(self, user_id: int, records: list) -> int:
        """保存步数记录（批量处理）"""
        if not records:
            return 0
        
        # 批量查询已存在的data_hash
        data_hashes = [r.get('data_hash') for r in records]
        existing_hashes = set(
            row[0] for row in self.db.query(ExternalStepRecord.data_hash)
            .filter(ExternalStepRecord.data_hash.in_(data_hashes))
            .all()
        )
        
        # 批量准备要插入的数据
        batch_size = 3000
        total_count = 0
        new_records = []
        
        for record in records:
            try:
                # 跳过已存在的记录
                if record.get('data_hash') in existing_hashes:
                    continue
                
                step_data = ExternalStepRecord(
                    user_id=user_id,
                    data_source="xiaomi_sport",
                    data_hash=record.get('data_hash'),
                    step_date=datetime.fromtimestamp(record.get('date', 0) / 1000).date(),
                    steps=record.get('step', 0),
                    distance=record.get('distance', 0),
                    calories=record.get('calories', 0),
                    active_time=record.get('ttm', 0) // 60,
                    raw_data=json.dumps(record)
                )
                new_records.append(step_data)
                
                # 达到批量大小，执行批量插入
                if len(new_records) >= batch_size:
                    self.db.bulk_save_objects(new_records)
                    self.db.commit()
                    total_count += len(new_records)
                    print(f"已批量保存 {len(new_records)} 条步数记录")
                    new_records = []
                    
            except Exception as e:
                print(f"处理步数记录失败: {e}")
                continue
        
        # 保存剩余的记录
        if new_records:
            self.db.bulk_save_objects(new_records)
            self.db.commit()
            total_count += len(new_records)
            print(f"已批量保存 {len(new_records)} 条步数记录")
        
        return total_count
    
    def sync_data(
        self,
        user_id: int,
        data_source: str,
        data_type: str,
        sync_type: str = "manual",
        days: int = 30,
        sync_yesterday: bool = False
    ) -> Dict:
        """
        同步数据
        :param user_id: 用户ID
        :param data_source: 数据来源
        :param data_type: 数据类型
        :param sync_type: 同步类型（manual/auto）
        :param days: 同步最近多少天的数据，0表示全部数据
        :param sync_yesterday: 是否同步昨天数据（True=昨天整天，False=往前推N天）
        :return: 同步结果
        """
        # 检查是否正在同步
        if self.is_syncing(user_id, data_source, data_type):
            return {
                "success": False,
                "message": "该数据类型正在同步中，请稍后再试"
            }
        
        # 尝试获取锁
        if not self.acquire_lock(user_id, data_source, data_type):
            return {
                "success": False,
                "message": "获取同步锁失败，请稍后再试"
            }
        
        # 创建同步日志
        log = self.create_sync_log(user_id, data_source, data_type, sync_type)
        
        try:
            # 获取小米数据同步服务
            if data_source == "xiaomi_sport":
                sync_service = self._get_xiaomi_sync_service(user_id)
                if not sync_service:
                    raise Exception("未找到小米运动健康授权信息或授权未验证")
                
                # 计算时间范围
                if sync_yesterday:
                    # 同步昨天的数据（昨天00:00:00 到 昨天23:59:59）
                    today = datetime.now().date()
                    yesterday = today - timedelta(days=1)
                    start_time = datetime.combine(yesterday, datetime.min.time())
                    end_time = datetime.combine(yesterday, datetime.max.time())
                elif days == 0:
                    # 同步全部数据，从1970年1月1日开始
                    start_time = datetime.fromtimestamp(1)
                    end_time = datetime.now()
                else:
                    # 往前推N天（从现在往前推）
                    end_time = datetime.now()
                    start_time = end_time - timedelta(days=days)
                
                # 根据数据类型调用不同的方法
                if data_type == "sleep":
                    records = sync_service.get_sleep_records(start_time, end_time)
                    count = self._save_sleep_records(user_id, records)
                elif data_type == "exercise":
                    records = sync_service.get_exercise_records(start_time, end_time)
                    count = self._save_exercise_records(user_id, records)
                elif data_type == "weight":
                    records = sync_service.get_weight_records(start_time, end_time)
                    count = self._save_weight_records(user_id, records)
                elif data_type == "steps":
                    records = sync_service.get_step_records(start_time, end_time)
                    count = self._save_step_records(user_id, records)
                else:
                    raise Exception(f"不支持的数据类型: {data_type}")
                
                # 更新同步日志为成功
                self.update_sync_log(log.id, "success", count)
                
                # 更新配置的最后同步时间
                config = self.db.query(DataSyncConfig).filter(
                    DataSyncConfig.user_id == user_id,
                    DataSyncConfig.data_source == data_source,
                    DataSyncConfig.data_type == data_type
                ).first()
                if config:
                    config.last_sync_time = datetime.now()  # type: ignore
                    self.db.commit()
                
                # 统一读取【个人设置】决定是否自动同步到本地
                user_settings = self.db.query(UserSettings).filter(
                    UserSettings.user_id == user_id
                ).first()
                
                # 如果配置了自动同步到本地，则执行同步
                if user_settings and user_settings.auto_sync_to_local:
                    from app.services.local_sync_service import (
                        sync_weight_to_local,
                        sync_sleep_to_local,
                        sync_exercise_to_local
                    )
                    
                    local_sync_count = 0
                    
                    # 根据配置决定同步哪些数据类型到本地
                    if user_settings.sync_weight and data_type == "weight":
                        local_sync_count = sync_weight_to_local(user_id, self.db, start_time, end_time)
                        print(f"已同步 {local_sync_count} 条体重数据到本地库")
                    elif user_settings.sync_sleep and data_type == "sleep":
                        local_sync_count = sync_sleep_to_local(user_id, self.db, start_time, end_time)
                        print(f"已同步 {local_sync_count} 条睡眠数据到本地库")
                    elif user_settings.sync_exercise and data_type == "exercise":
                        local_sync_count = sync_exercise_to_local(user_id, self.db, start_time, end_time)
                        print(f"已同步 {local_sync_count} 条运动数据到本地库")
                
                if sync_yesterday:
                    sync_range = "昨天数据"
                elif days == 0:
                    sync_range = "全部数据"
                else:
                    sync_range = f"最近{days}天"
                    
                return {
                    "success": True,
                    "message": f"同步成功（{sync_range}），共同步 {count} 条新数据",
                    "data_count": count
                }
            else:
                raise Exception(f"不支持的数据来源: {data_source}")
        
        except Exception as e:
            # 更新同步日志为失败
            self.update_sync_log(log.id, "failed", error_message=str(e))
            return {
                "success": False,
                "message": f"同步失败: {str(e)}"
            }
        
        finally:
            # 释放锁
            self.release_lock(user_id, data_source, data_type)
