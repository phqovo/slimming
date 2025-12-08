-- 添加第三方登录字段
ALTER TABLE users 
ADD COLUMN wechat_openid VARCHAR(100) UNIQUE COMMENT '微信openid',
ADD COLUMN wechat_unionid VARCHAR(100) COMMENT '微信unionid',
ADD COLUMN qq_openid VARCHAR(100) UNIQUE COMMENT 'QQ openid',
ADD COLUMN oauth_avatar VARCHAR(500) COMMENT '第三方原始头像URL',
MODIFY COLUMN phone VARCHAR(20) UNIQUE COMMENT '手机号（可为空）',
MODIFY COLUMN phone VARCHAR(20) NULL;

-- 为第三方登录字段添加索引
CREATE INDEX idx_wechat_openid ON users(wechat_openid);
CREATE INDEX idx_qq_openid ON users(qq_openid);

-- 注：phone字段改为可空，因为第三方登录可能没有手机号
