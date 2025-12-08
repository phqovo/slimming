#!/usr/bin/env python3
"""从历史记录表恢复运动记录数据"""
import re
from datetime import datetime
from app.core.database import SessionLocal
from app.models.daily_history import DailyHistory
from app.models.exercise import ExerciseRecord
from sqlalchemy import and_

def parse_exercise_string(exercise_str):
    """
    解析运动字符串，格式：运动类型 时长分钟 卡路里大卡
    示例：跳操 36分钟 500大卡
    """
    if not exercise_str or exercise_str == '无':
        return []
    
    exercises = []
    # 按 + 分割多个运动项
    items = exercise_str.split(' + ')
    
    for item in items:
        item = item.strip()
        if not item:
            continue
        
        # 提取运动类型、时长、卡路里
        # 格式：运动类型 时长分钟 卡路里大卡
        # 或者：运动类型 卡路里大卡（没有时长）
        
        # 尝试匹配：运动类型 时长分钟 卡路里大卡
        match = re.match(r'(.+?)\s+(\d+)分钟\s+(\d+)大卡', item)
        if match:
            exercise_type = match.group(1).strip()
            duration = int(match.group(2))
            calories = int(match.group(3))
            exercises.append({
                'exercise_type': exercise_type,
                'duration': duration,
                'calories': calories
            })
            continue
        
        # 尝试匹配：运动类型 卡路里大卡（没有时长）
        match = re.match(r'(.+?)\s+(\d+)大卡', item)
        if match:
            exercise_type = match.group(1).strip()
            calories = int(match.group(2))
            # 根据卡路里估算时长（假设平均每分钟消耗10卡路里）
            duration = max(1, calories // 10)
            exercises.append({
                'exercise_type': exercise_type,
                'duration': duration,
                'calories': calories
            })
            continue
    
    return exercises


def restore_exercise_records(before_date='2025-11-21', user_id=1):
    """从历史记录恢复运动记录"""
    db = SessionLocal()
    
    try:
        # 查询历史记录
        histories = db.query(DailyHistory).filter(
            and_(
                DailyHistory.record_date < before_date,
                DailyHistory.user_id == user_id,
                DailyHistory.exercise != '无'
            )
        ).order_by(DailyHistory.record_date).all()
        
        print(f'找到 {len(histories)} 条包含运动数据的历史记录')
        
        restored_count = 0
        skipped_count = 0
        
        for history in histories:
            print(f'\n处理日期 {history.record_date}:')
            print(f'  运动数据: {history.exercise}')
            
            # 检查该日期是否已有运动记录
            existing_count = db.query(ExerciseRecord).filter(
                and_(
                    ExerciseRecord.user_id == user_id,
                    ExerciseRecord.record_date == history.record_date,
                    ExerciseRecord.external_id.is_(None)  # 只检查非外部数据
                )
            ).count()
            
            if existing_count > 0:
                print(f'  ⚠️  该日期已有 {existing_count} 条运动记录，跳过')
                skipped_count += 1
                continue
            
            # 解析运动字符串
            exercises = parse_exercise_string(history.exercise)
            
            if not exercises:
                print('  ⚠️  无法解析运动数据，跳过')
                continue
            
            # 插入运动记录
            for ex in exercises:
                exercise_record = ExerciseRecord(
                    user_id=user_id,
                    record_date=history.record_date,
                    exercise_type=ex['exercise_type'],
                    duration=ex['duration'],
                    calories=ex['calories'],
                    distance=0.0,
                    note='从历史记录恢复'
                )
                db.add(exercise_record)
                print(f'  ✅ 添加: {ex["exercise_type"]} {ex["duration"]}分钟 {ex["calories"]}大卡')
                restored_count += 1
        
        # 提交事务
        db.commit()
        
        print(f'\n' + '='*50)
        print(f'恢复完成！')
        print(f'  成功恢复: {restored_count} 条运动记录')
        print(f'  跳过已存在: {skipped_count} 天')
        print('='*50)
        
    except Exception as e:
        print(f'\n❌ 错误: {e}')
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == '__main__':
    print('开始从历史记录恢复运动数据...\n')
    restore_exercise_records(before_date='2025-11-21', user_id=1)
