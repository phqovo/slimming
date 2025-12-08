"""将三方数据同步到本地库的服务"""
from datetime import datetime, time, timedelta
from sqlalchemy.orm import Session
from app.models.weight import WeightRecord
from app.models.sleep import SleepRecord
from app.models.exercise import ExerciseRecord
from app.models.external_data import ExternalWeightRecord, ExternalSleepRecord, ExternalExerciseRecord
from app.utils.health_calculator import calculate_bmi, update_user_health_stats
from typing import List, Dict, Set
import logging

logger = logging.getLogger(__name__)


def sync_weight_to_local(user_id: int, db: Session, start_date: datetime, end_date: datetime) -> int:
    """
    将外部体重数据同步到本地库
    
    逻辑：
    - 某天有多条数据：0-12:00最早的为早晨体重，12:00-23:59:59最晚的为晚间体重
    - 某天只有一条数据：早晨体重、体重、睡前体重都取这条数据
    """
    # 查询时间范围内的外部体重数据
    external_records = db.query(ExternalWeightRecord).filter(
        ExternalWeightRecord.user_id == user_id,
        ExternalWeightRecord.measure_time >= start_date,
        ExternalWeightRecord.measure_time <= end_date,
        ExternalWeightRecord.data_source == 'xiaomi_sport'
    ).order_by(ExternalWeightRecord.measure_time).all()
    
    if not external_records:
        return 0
    
    # 按日期分组
    records_by_date: Dict[str, List[ExternalWeightRecord]] = {}
    for record in external_records:
        date_str = record.measure_time.date().isoformat()
        if date_str not in records_by_date:
            records_by_date[date_str] = []
        records_by_date[date_str].append(record)
    
    synced_count = 0
    synced_dates: Set[datetime.date] = set()  # 记录所有同步的日期
    
    for date_str, day_records in records_by_date.items():
        record_date = datetime.fromisoformat(date_str).date()
        
        # 查询该日期在外部体重记录表中的所有数据（包括本次拉取和之前已有的）
        all_day_records = db.query(ExternalWeightRecord).filter(
            ExternalWeightRecord.user_id == user_id,
            ExternalWeightRecord.measure_date == record_date,
            ExternalWeightRecord.data_source == 'xiaomi_sport'
        ).order_by(ExternalWeightRecord.measure_time).all()
        
        # 检查本地是否已存在该日期的记录
        existing = db.query(WeightRecord).filter(
            WeightRecord.user_id == user_id,
            WeightRecord.record_date == record_date
        ).first()
        
        # 如果已存在用户手动维护的数据（external_id为NULL），跳过不覆盖
        if existing and existing.external_id is None:
            continue
        
        if len(all_day_records) == 1:
            # 只有一条数据，早晨、体重、晚间都取这条
            record = all_day_records[0]
            
            # 检查external_id避免重复
            if existing and existing.external_id == str(record.id):
                continue
            
            # 检查该日期是否已有用户手动数据（external_id为NULL）
            existing_manual = db.query(WeightRecord).filter(
                WeightRecord.user_id == user_id,
                WeightRecord.record_date == record_date,
                WeightRecord.external_id.is_(None)
            ).first()
            
            # 如果已有用户手动数据，跳过不覆盖
            if existing_manual:
                continue
            
            weight_data = {
                'user_id': user_id,
                'external_id': str(record.id),
                'weight': record.weight,
                'morning_weight': record.weight,
                'evening_weight': record.weight,
                'body_fat': record.body_fat or 0.0,
                'bmi': record.bmi or calculate_bmi(record.weight, None) if record.weight else 0.0,
                'record_date': record_date,
                'note': '来自小米运动'
            }
            
            if existing:
                # 更新
                for key, value in weight_data.items():
                    if key != 'user_id':
                        setattr(existing, key, value)
            else:
                # 新增
                db.add(WeightRecord(**weight_data))
            synced_count += 1
            synced_dates.add(record_date)  # 记录同步的日期
            
        else:
            # 多条数据，分早晨和晚间
            morning_record = None
            evening_record = None
            
            for record in all_day_records:
                hour = record.measure_time.hour
                if hour < 12:
                    # 0-12:00，取最早的
                    if morning_record is None or record.measure_time < morning_record.measure_time:
                        morning_record = record
                else:
                    # 12:00-23:59:59，取最晚的
                    if evening_record is None or record.measure_time > evening_record.measure_time:
                        evening_record = record
            
            # 构建weight_data
            weight_data = {
                'user_id': user_id,
                'record_date': record_date,
                'note': '来自小米运动'
            }
            
            # 使用早晨或晚间的external_id（优先早晨）
            primary_record = morning_record or evening_record
            weight_data['external_id'] = str(primary_record.id)
            
            # 检查是否已存在同一external_id的记录
            if existing and existing.external_id == weight_data['external_id']:
                continue
            
            # 检查该日期是否已有用户手动数据（external_id为NULL）
            existing_manual = db.query(WeightRecord).filter(
                WeightRecord.user_id == user_id,
                WeightRecord.record_date == record_date,
                WeightRecord.external_id.is_(None)
            ).first()
            
            # 如果已有用户手动数据，跳过不覆盖
            if existing_manual:
                continue
            
            if morning_record:
                weight_data['morning_weight'] = morning_record.weight
                weight_data['weight'] = morning_record.weight
                weight_data['body_fat'] = morning_record.body_fat or 0.0
                weight_data['bmi'] = morning_record.bmi or calculate_bmi(morning_record.weight, None) if morning_record.weight else 0.0
            
            if evening_record:
                weight_data['evening_weight'] = evening_record.weight
                # 如果没有早晨体重，用晚间的作为主体重
                if not morning_record:
                    weight_data['weight'] = evening_record.weight
                    weight_data['body_fat'] = evening_record.body_fat or 0.0
                    weight_data['bmi'] = evening_record.bmi or calculate_bmi(evening_record.weight, None) if evening_record.weight else 0.0
            
            if existing:
                for key, value in weight_data.items():
                    if key != 'user_id':
                        setattr(existing, key, value)
            else:
                db.add(WeightRecord(**weight_data))
            synced_count += 1
            synced_dates.add(record_date)  # 记录同步的日期
    
    db.commit()
    
    # 触发历史记录重算
    from app.api.v1.weight import trigger_daily_history_recalculate
    for sync_date in synced_dates:
        trigger_daily_history_recalculate(db, user_id, sync_date)
    
    # 更新用户的健康数据（当前体重、BMI、基础代谢）
    if synced_count > 0:
        update_user_health_stats(db, user_id)
    
    return synced_count


def sync_sleep_to_local(user_id: int, db: Session, start_date: datetime, end_date: datetime) -> int:
    """将外部睡眠数据同步到本地库"""
    external_records = db.query(ExternalSleepRecord).filter(
        ExternalSleepRecord.user_id == user_id,
        ExternalSleepRecord.start_time >= start_date,
        ExternalSleepRecord.start_time <= end_date,
        ExternalSleepRecord.data_source == 'xiaomi_sport'
    ).all()
    
    if not external_records:
        return 0
    
    synced_count = 0
    synced_dates: Set[datetime.date] = set()  # 记录所有同步的日期
    
    for ext_record in external_records:
        # 计算睡眠日期（以起床时间的日期为准）
        record_date = ext_record.end_time.date() if ext_record.end_time else ext_record.start_time.date()
        
        # 检查是否已存在同一external_id的记录（避免重复）
        existing_by_external_id = db.query(SleepRecord).filter(
            SleepRecord.user_id == user_id,
            SleepRecord.external_id == str(ext_record.id)
        ).first()
        
        if existing_by_external_id:
            continue
        
        # 检查该日期是否已有用户手动数据（external_id为NULL）
        existing_manual = db.query(SleepRecord).filter(
            SleepRecord.user_id == user_id,
            SleepRecord.record_date == record_date,
            SleepRecord.external_id.is_(None)
        ).first()
        
        # 如果已有用户手动数据，跳过不覆盖
        if existing_manual:
            continue
        
        sleep_data = {
            'user_id': user_id,
            'external_id': str(ext_record.id),
            'duration': ext_record.total_duration / 60.0,  # 转换为小时
            'quality': '',  # 外部数据可能没有质量评级
            'sleep_time': ext_record.start_time,
            'wake_time': ext_record.end_time,
            'record_date': record_date
        }
        
        db.add(SleepRecord(**sleep_data))
        synced_count += 1
        synced_dates.add(record_date)  # 记录同步的日期
    
    db.commit()
    
    # 触发历史记录重算
    from app.api.v1.weight import trigger_daily_history_recalculate
    for sync_date in synced_dates:
        trigger_daily_history_recalculate(db, user_id, sync_date)
    
    return synced_count


def sync_exercise_to_local(user_id: int, db: Session, start_date: datetime, end_date: datetime) -> int:
    """将外部运动数据同步到本地库"""
    external_records = db.query(ExternalExerciseRecord).filter(
        ExternalExerciseRecord.user_id == user_id,
        ExternalExerciseRecord.start_time >= start_date,
        ExternalExerciseRecord.start_time <= end_date,
        ExternalExerciseRecord.data_source == 'xiaomi_sport'
    ).all()
    
    if not external_records:
        return 0
    
    synced_count = 0
    synced_dates: Set[datetime.date] = set()  # 记录所有同步的日期
    
    for ext_record in external_records:
        # 检查是否已存在
        existing = db.query(ExerciseRecord).filter(
            ExerciseRecord.user_id == user_id,
            ExerciseRecord.external_id == str(ext_record.id)
        ).first()
        
        if existing:
            continue
        
        # 计算运动日期
        record_date = ext_record.start_time.date()
        
        # 检查该日期是否已有用户手动数据（external_id为NULL）
        existing_manual = db.query(ExerciseRecord).filter(
            ExerciseRecord.user_id == user_id,
            ExerciseRecord.record_date == record_date,
            ExerciseRecord.external_id.is_(None)
        ).first()
        
        # 如果已有用户手动数据，跳过不覆盖
        if existing_manual:
            continue
        
        exercise_data = {
            'user_id': user_id,
            'external_id': str(ext_record.id),
            'exercise_type': ext_record.exercise_type or '运动',
            'duration': ext_record.duration,
            'calories': ext_record.calories or 0.0,
            'distance': (ext_record.distance or 0.0) / 1000,  # 米转换为公里
            'note': '来自小米运动',
            'record_date': record_date
        }
        
        db.add(ExerciseRecord(**exercise_data))
        synced_count += 1
        synced_dates.add(record_date)  # 记录同步的日期
    
    db.commit()
    
    # 触发历史记录重算
    from app.api.v1.weight import trigger_daily_history_recalculate
    for sync_date in synced_dates:
        trigger_daily_history_recalculate(db, user_id, sync_date)
    
    return synced_count
