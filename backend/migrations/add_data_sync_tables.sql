-- 数据同步配置表
CREATE TABLE `data_sync_config` (
  `id` INT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `user_id` INT NOT NULL COMMENT '用户ID',
  `data_source` VARCHAR(50) NOT NULL COMMENT '数据来源（xiaomi_sport等）',
  `data_type` VARCHAR(50) NOT NULL COMMENT '数据类型（sleep/exercise/weight/steps）',
  `enabled` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否启用定时同步',
  `interval_seconds` INT NOT NULL DEFAULT 3600 COMMENT '同步间隔（秒）',
  `last_sync_time` DATETIME NULL COMMENT '最后同步时间',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_user_source_type` (`user_id`, `data_source`, `data_type`),
  INDEX `idx_enabled` (`enabled`),
  INDEX `idx_user_source` (`user_id`, `data_source`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='数据同步配置表';

-- 数据拉取日志表
CREATE TABLE `data_sync_log` (
  `id` INT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `user_id` INT NOT NULL COMMENT '用户ID',
  `data_source` VARCHAR(50) NOT NULL COMMENT '数据来源',
  `data_type` VARCHAR(50) NOT NULL COMMENT '数据类型',
  `sync_type` VARCHAR(20) NOT NULL COMMENT '同步类型（manual/auto）',
  `status` VARCHAR(20) NOT NULL COMMENT '状态（running/success/failed）',
  `start_time` DATETIME NOT NULL COMMENT '开始时间',
  `end_time` DATETIME NULL COMMENT '结束时间',
  `duration` INT NULL COMMENT '耗时（毫秒）',
  `data_count` INT NULL COMMENT '数据条数',
  `error_message` TEXT NULL COMMENT '错误信息',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  INDEX `idx_user_source_type` (`user_id`, `data_source`, `data_type`),
  INDEX `idx_status` (`status`),
  INDEX `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='数据拉取日志表';
