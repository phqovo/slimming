-- 添加数据公开字段到用户设置表
ALTER TABLE user_settings ADD COLUMN data_public TINYINT(1) DEFAULT 0 COMMENT '数据是否公开';
