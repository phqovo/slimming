-- 添加外部数据源ID字段，避免重复同步
-- 执行日期: 2025-11-21

-- 体重记录表添加外部ID字段
ALTER TABLE weight_records 
ADD COLUMN external_id VARCHAR(100) DEFAULT NULL COMMENT '外部数据源ID' AFTER id,
ADD INDEX idx_external_id (external_id);

-- 睡眠记录表添加外部ID字段
ALTER TABLE sleep_records 
ADD COLUMN external_id VARCHAR(100) DEFAULT NULL COMMENT '外部数据源ID' AFTER id,
ADD INDEX idx_external_id (external_id);

-- 运动记录表添加外部ID字段
ALTER TABLE exercise_records 
ADD COLUMN external_id VARCHAR(100) DEFAULT NULL COMMENT '外部数据源ID' AFTER id,
ADD INDEX idx_external_id (external_id);
