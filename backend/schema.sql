-- 创建数据库
CREATE DATABASE IF NOT EXISTS slimming_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE slimming_db;

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    phone VARCHAR(20) UNIQUE NOT NULL COMMENT '手机号',
    nickname VARCHAR(50) DEFAULT '' COMMENT '昵称',
    avatar VARCHAR(255) DEFAULT '' COMMENT '头像URL',
    age INT DEFAULT 0 COMMENT '年龄',
    gender VARCHAR(10) DEFAULT '' COMMENT '性别',
    height FLOAT DEFAULT 0.0 COMMENT '身高(cm)',
    target_weight FLOAT DEFAULT 0.0 COMMENT '目标体重(kg)',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_phone (phone)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- 体重记录表
CREATE TABLE IF NOT EXISTS weight_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL COMMENT '用户ID',
    weight FLOAT NOT NULL COMMENT '体重(kg)',
    body_fat FLOAT DEFAULT 0.0 COMMENT '体脂率(%)',
    bmi FLOAT DEFAULT 0.0 COMMENT 'BMI指数',
    record_date DATE NOT NULL COMMENT '记录日期',
    note VARCHAR(255) DEFAULT '' COMMENT '备注',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_user_id (user_id),
    INDEX idx_record_date (record_date),
    UNIQUE KEY uk_user_date (user_id, record_date),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='体重记录表';

-- 运动记录表
CREATE TABLE IF NOT EXISTS exercise_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL COMMENT '用户ID',
    exercise_type VARCHAR(50) NOT NULL COMMENT '运动类型',
    duration INT DEFAULT 0 COMMENT '运动时长(分钟)',
    calories FLOAT DEFAULT 0.0 COMMENT '消耗卡路里',
    distance FLOAT DEFAULT 0.0 COMMENT '运动距离(km)',
    image_url VARCHAR(255) DEFAULT '' COMMENT '运动图片URL',
    note TEXT COMMENT '备注',
    record_date DATE NOT NULL COMMENT '记录日期',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_user_id (user_id),
    INDEX idx_record_date (record_date),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='运动记录表';

-- 饮食记录表
CREATE TABLE IF NOT EXISTS diet_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL COMMENT '用户ID',
    meal_type VARCHAR(20) NOT NULL COMMENT '餐次',
    food_name VARCHAR(100) NOT NULL COMMENT '食物名称',
    calories FLOAT DEFAULT 0.0 COMMENT '卡路里',
    protein FLOAT DEFAULT 0.0 COMMENT '蛋白质(g)',
    carbs FLOAT DEFAULT 0.0 COMMENT '碳水化合物(g)',
    fat FLOAT DEFAULT 0.0 COMMENT '脂肪(g)',
    portion VARCHAR(50) DEFAULT '' COMMENT '份量',
    note TEXT COMMENT '备注',
    record_date DATE NOT NULL COMMENT '记录日期',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_user_id (user_id),
    INDEX idx_record_date (record_date),
    INDEX idx_meal_type (meal_type),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='饮食记录表';

-- 饮水记录表
CREATE TABLE IF NOT EXISTS water_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL COMMENT '用户ID',
    amount FLOAT NOT NULL COMMENT '饮水量(ml)',
    record_date DATE NOT NULL COMMENT '记录日期',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_user_id (user_id),
    INDEX idx_record_date (record_date),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='饮水记录表';

-- 睡眠记录表
CREATE TABLE IF NOT EXISTS sleep_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL COMMENT '用户ID',
    duration FLOAT NOT NULL COMMENT '睡眠时长(小时)',
    quality VARCHAR(20) DEFAULT '' COMMENT '睡眠质量',
    sleep_time DATETIME COMMENT '入睡时间',
    wake_time DATETIME COMMENT '起床时间',
    record_date DATE NOT NULL COMMENT '记录日期',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_user_id (user_id),
    INDEX idx_record_date (record_date),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='睡眠记录表';
