-- 为四个外部数据表添加逻辑删除字段

-- 1. 外部睡眠记录表
ALTER TABLE `external_sleep_records` 
ADD COLUMN `is_deleted` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '逻辑删除标记（0=未删除，1=已删除）' AFTER `raw_data`;

ALTER TABLE `external_sleep_records` 
ADD INDEX `idx_is_deleted` (`is_deleted`);

-- 2. 外部运动记录表
ALTER TABLE `external_exercise_records` 
ADD COLUMN `is_deleted` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '逻辑删除标记（0=未删除，1=已删除）' AFTER `raw_data`;

ALTER TABLE `external_exercise_records` 
ADD INDEX `idx_is_deleted` (`is_deleted`);

-- 3. 外部体重记录表
ALTER TABLE `external_weight_records` 
ADD COLUMN `is_deleted` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '逻辑删除标记（0=未删除，1=已删除）' AFTER `raw_data`;

ALTER TABLE `external_weight_records` 
ADD INDEX `idx_is_deleted` (`is_deleted`);

-- 4. 外部步数记录表
ALTER TABLE `external_step_records` 
ADD COLUMN `is_deleted` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '逻辑删除标记（0=未删除，1=已删除）' AFTER `raw_data`;

ALTER TABLE `external_step_records` 
ADD INDEX `idx_is_deleted` (`is_deleted`);
