-- 添加QQ和微信昵称字段
ALTER TABLE users ADD COLUMN qq_nickname VARCHAR(100) NULL COMMENT 'QQ昵称';
ALTER TABLE users ADD COLUMN wechat_nickname VARCHAR(100) NULL COMMENT '微信昵称';
