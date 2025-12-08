-- 添加自动同步到本地库配置字段
-- 执行日期: 2025-11-21

ALTER TABLE data_sync_config 
ADD COLUMN auto_sync_to_local BOOLEAN DEFAULT FALSE COMMENT '是否自动同步到本地库' AFTER last_sync_time,
ADD COLUMN sync_weight BOOLEAN DEFAULT FALSE COMMENT '同步体重数据' AFTER auto_sync_to_local,
ADD COLUMN sync_sleep BOOLEAN DEFAULT FALSE COMMENT '同步睡眠数据' AFTER sync_weight,
ADD COLUMN sync_exercise BOOLEAN DEFAULT FALSE COMMENT '同步锻炼数据' AFTER sync_sleep;
