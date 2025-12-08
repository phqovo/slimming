-- 添加心率和腰臀比字段到体重记录表
-- 执行日期: 2025-11-21

ALTER TABLE external_weight_records 
ADD COLUMN heart_rate INT DEFAULT NULL COMMENT '心率（bpm）' AFTER body_score;

ALTER TABLE external_weight_records 
ADD COLUMN whr DECIMAL(5, 2) DEFAULT NULL COMMENT '腰臀比' AFTER heart_rate;
