-- 添加自动同步天数配置字段
-- 执行日期: 2025-11-21

ALTER TABLE data_sync_config 
ADD COLUMN sync_days INT DEFAULT 30 NOT NULL COMMENT '自动同步天数（0表示全部数据）' AFTER cron_minute;

ALTER TABLE data_sync_config 
ADD COLUMN sync_yesterday TINYINT(1) DEFAULT 0 NOT NULL COMMENT '是否同步昨天数据（1=昨天整天，0=往前推N天）' AFTER sync_days;
