"""外部数据模型"""
from sqlalchemy import Column, Integer, String, DateTime, Date, DECIMAL, Text, JSON, Index
from sqlalchemy.sql import func
from app.core.database import Base


class ExternalSleepRecord(Base):
    """外部数据-睡眠记录"""
    __tablename__ = "external_sleep_records"

    id = Column(Integer, primary_key=True, index=True, comment='主键ID')
    user_id = Column(Integer, nullable=False, comment='用户ID')
    data_source = Column(String(50), nullable=False, default='xiaomi_sport', comment='数据来源')
    source_id = Column(String(100), comment='来源数据ID')
    data_hash = Column(String(64), nullable=False, unique=True, comment='数据哈希值')
    sleep_date = Column(Date, nullable=False, comment='睡眠日期')
    start_time = Column(DateTime, nullable=False, comment='入睡时间')
    end_time = Column(DateTime, nullable=False, comment='起床时间')
    total_duration = Column(Integer, comment='总睡眠时长（分钟）')
    deep_sleep = Column(Integer, comment='深睡时长（分钟）')
    light_sleep = Column(Integer, comment='浅睡时长（分钟）')
    rem_sleep = Column(Integer, comment='REM睡眠时长（分钟）')
    awake_time = Column(Integer, comment='清醒时长（分钟）')
    sleep_score = Column(Integer, comment='睡眠评分')
    raw_data = Column(JSON, comment='原始数据')
    created_at = Column(DateTime, server_default=func.now(), comment='创建时间')
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')

    __table_args__ = (
        Index('idx_user_date', 'user_id', 'sleep_date'),
        Index('idx_user_source', 'user_id', 'data_source'),
    )


class ExternalExerciseRecord(Base):
    """外部数据-锻炼记录"""
    __tablename__ = "external_exercise_records"

    id = Column(Integer, primary_key=True, index=True, comment='主键ID')
    user_id = Column(Integer, nullable=False, comment='用户ID')
    data_source = Column(String(50), nullable=False, default='xiaomi_sport', comment='数据来源')
    source_id = Column(String(100), comment='来源数据ID')
    data_hash = Column(String(64), nullable=False, unique=True, comment='数据哈希值')
    exercise_date = Column(Date, nullable=False, comment='锻炼日期')
    start_time = Column(DateTime, nullable=False, comment='开始时间')
    end_time = Column(DateTime, nullable=False, comment='结束时间')
    exercise_type = Column(String(50), comment='运动类型')
    duration = Column(Integer, comment='运动时长（分钟）')
    distance = Column(DECIMAL(10, 2), comment='运动距离（米）')
    calories = Column(Integer, comment='消耗卡路里')
    steps = Column(Integer, comment='步数')
    avg_heart_rate = Column(Integer, comment='平均心率')
    max_heart_rate = Column(Integer, comment='最大心率')
    raw_data = Column(JSON, comment='原始数据')
    created_at = Column(DateTime, server_default=func.now(), comment='创建时间')
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')

    __table_args__ = (
        Index('idx_user_date', 'user_id', 'exercise_date'),
        Index('idx_user_source', 'user_id', 'data_source'),
    )


class ExternalWeightRecord(Base):
    """外部数据-体重记录"""
    __tablename__ = "external_weight_records"

    id = Column(Integer, primary_key=True, index=True, comment='主键ID')
    user_id = Column(Integer, nullable=False, comment='用户ID')
    data_source = Column(String(50), nullable=False, default='xiaomi_sport', comment='数据来源')
    source_id = Column(String(100), comment='来源数据ID')
    data_hash = Column(String(64), nullable=False, unique=True, comment='数据哈希值')
    measure_date = Column(Date, nullable=False, comment='测量日期')
    measure_time = Column(DateTime, nullable=False, comment='测量时间')
    weight = Column(DECIMAL(5, 2), nullable=False, comment='体重（kg）')
    bmi = Column(DECIMAL(5, 2), comment='BMI指数')
    body_fat = Column(DECIMAL(5, 2), comment='体脂率（%）')
    muscle_mass = Column(DECIMAL(5, 2), comment='肌肉量（kg）')
    bone_mass = Column(DECIMAL(5, 2), comment='骨量（kg）')
    water = Column(DECIMAL(5, 2), comment='水分（%）')
    protein = Column(DECIMAL(5, 2), comment='蛋白质（%）')
    bmr = Column(Integer, comment='基础代谢率')
    visceral_fat = Column(DECIMAL(5, 2), comment='内脏脂肪等级')
    body_age = Column(Integer, comment='身体年龄')
    body_score = Column(Integer, comment='身体评分')
    heart_rate = Column(Integer, comment='心率（bpm）')
    whr = Column(DECIMAL(5, 2), comment='腰臀比')
    # 八电极秤详细数据
    body_shape = Column(Integer, comment='体型')
    fat_mass = Column(DECIMAL(5, 2), comment='脂肪量（kg）')
    left_lower_limb_fat_mass = Column(DECIMAL(5, 2), comment='左下肢脂肪量')
    left_lower_limb_fat_rank = Column(Integer, comment='左下肢脂肪等级')
    left_lower_limb_muscle_mass = Column(Integer, comment='左下肢肌肉量')
    left_lower_limb_muscle_rank = Column(Integer, comment='左下肢肌肉等级')
    left_upper_limb_fat_mass = Column(DECIMAL(5, 2), comment='左上肢脂肪量')
    left_upper_limb_fat_rank = Column(Integer, comment='左上肢脂肪等级')
    left_upper_limb_muscle_mass = Column(DECIMAL(5, 2), comment='左上肢肌肉量')
    left_upper_limb_muscle_rank = Column(Integer, comment='左上肢肌肉等级')
    limbs_fat_balance = Column(Integer, comment='四肢脂肪平衡')
    limbs_muscle_balance = Column(Integer, comment='四肢肌肉平衡')
    limbs_skeletal_muscle_index = Column(DECIMAL(5, 2), comment='四肢骨骼肌指数')
    lower_limb_fat_balance = Column(Integer, comment='下肢脂肪平衡')
    lower_limb_muscle_balance = Column(Integer, comment='下肢肌肉平衡')
    recommended_calories_intake = Column(Integer, comment='推荐卡路里摄入')
    right_lower_limb_fat_mass = Column(DECIMAL(5, 2), comment='右下肢脂肪量')
    right_lower_limb_fat_rank = Column(Integer, comment='右下肢脂肪等级')
    right_lower_limb_muscle_mass = Column(DECIMAL(5, 2), comment='右下肢肌肉量')
    right_lower_limb_muscle_rank = Column(Integer, comment='右下肢肌肉等级')
    right_upper_limb_fat_mass = Column(DECIMAL(5, 2), comment='右上肢脂肪量')
    right_upper_limb_fat_rank = Column(Integer, comment='右上肢脂肪等级')
    right_upper_limb_muscle_mass = Column(DECIMAL(5, 2), comment='右上肢肌肉量')
    right_upper_limb_muscle_rank = Column(Integer, comment='右上肢肌肉等级')
    trunk_fat_mass = Column(DECIMAL(5, 2), comment='躯干脂肪量')
    trunk_fat_rank = Column(Integer, comment='躯干脂肪等级')
    trunk_muscle_mass = Column(DECIMAL(5, 2), comment='躯干肌肉量')
    trunk_muscle_rank = Column(Integer, comment='躯干肌肉等级')
    upper_limb_fat_balance = Column(Integer, comment='上肢脂肪平衡')
    upper_limb_muscle_balance = Column(Integer, comment='上肢肌肉平衡')
    note = Column(String(500), comment='备注')
    raw_data = Column(JSON, comment='原始数据')
    created_at = Column(DateTime, server_default=func.now(), comment='创建时间')
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')

    __table_args__ = (
        Index('idx_user_date', 'user_id', 'measure_date'),
        Index('idx_user_source', 'user_id', 'data_source'),
    )


class ExternalStepRecord(Base):
    """外部数据-运动步数"""
    __tablename__ = "external_step_records"

    id = Column(Integer, primary_key=True, index=True, comment='主键ID')
    user_id = Column(Integer, nullable=False, comment='用户ID')
    data_source = Column(String(50), nullable=False, default='xiaomi_sport', comment='数据来源')
    source_id = Column(String(100), comment='来源数据ID')
    data_hash = Column(String(64), nullable=False, unique=True, comment='数据哈希值')
    step_date = Column(Date, nullable=False, comment='步数日期')
    steps = Column(Integer, nullable=False, comment='步数')
    distance = Column(DECIMAL(10, 2), comment='距离（米）')
    calories = Column(Integer, comment='消耗卡路里')
    active_time = Column(Integer, comment='活跃时长（分钟）')
    raw_data = Column(JSON, comment='原始数据')
    created_at = Column(DateTime, server_default=func.now(), comment='创建时间')
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')

    __table_args__ = (
        Index('idx_user_date', 'user_id', 'step_date'),
        Index('idx_user_source', 'user_id', 'data_source'),
    )
