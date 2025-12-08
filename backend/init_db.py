"""
数据库初始化脚本
运行此脚本以创建所有数据库表
"""
from app.core.database import engine, Base
from app.models import User, WeightRecord, ExerciseRecord, DietRecord, WaterRecord, SleepRecord


def init_db():
    """初始化数据库，创建所有表"""
    print("正在创建数据库表...")
    Base.metadata.create_all(bind=engine)
    print("数据库表创建完成！")
    print("创建的表包括：")
    print("  - users (用户表)")
    print("  - weight_records (体重记录表)")
    print("  - exercise_records (运动记录表)")
    print("  - diet_records (饮食记录表)")
    print("  - water_records (饮水记录表)")
    print("  - sleep_records (睡眠记录表)")


if __name__ == "__main__":
    init_db()
