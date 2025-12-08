-- 添加定时任务cron调度支持字段
-- 执行日期: 2025-11-20

-- 添加调度类型字段
ALTER TABLE data_sync_config 
ADD COLUMN schedule_type VARCHAR(20) DEFAULT 'interval' COMMENT '调度类型：interval=间隔执行, cron=每天定时' AFTER interval_seconds;

-- 添加cron小时字段
ALTER TABLE data_sync_config 
ADD COLUMN cron_hour INT DEFAULT NULL COMMENT '每天执行的小时（0-23），仅schedule_type=cron时有效' AFTER schedule_type;

-- 添加cron分钟字段
ALTER TABLE data_sync_config 
ADD COLUMN cron_minute INT DEFAULT 0 COMMENT '每天执行的分钟（0-59），仅schedule_type=cron时有效' AFTER cron_hour;
