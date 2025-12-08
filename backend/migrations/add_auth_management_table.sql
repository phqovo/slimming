-- 创建授权管理表
CREATE TABLE IF NOT EXISTS `auth_management` (
  `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
  `user_id` INT NOT NULL COMMENT '用户ID',
  `auth_type` VARCHAR(50) NOT NULL COMMENT '授权类型（xiaomi_sport等）',
  `account` VARCHAR(100) NOT NULL COMMENT '账号',
  `password` VARCHAR(255) NOT NULL COMMENT '密码',
  `token` TEXT COMMENT '登录Token（如userID:passToken）',
  `ssecurity` TEXT COMMENT '加密密钥（小米运动健康）',
  `cookies` TEXT COMMENT '登录Cookies',
  `extra_data` JSON COMMENT '额外数据（JSON格式，如region等）',
  `status` TINYINT DEFAULT 0 COMMENT '状态：0=未验证，1=验证成功，2=验证失败',
  `last_verify_time` TIMESTAMP NULL COMMENT '最后验证时间',
  `error_message` VARCHAR(500) COMMENT '错误信息',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  UNIQUE KEY `uk_user_auth_type` (`user_id`, `auth_type`) COMMENT '同一用户同一类型唯一',
  INDEX `idx_user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='授权管理表';
