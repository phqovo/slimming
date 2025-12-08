-- 为用户表添加当前体重、BMI、基础代谢字段
ALTER TABLE users 
ADD COLUMN current_weight FLOAT DEFAULT 0.0 COMMENT '当前体重(kg)',
ADD COLUMN bmi FLOAT DEFAULT 0.0 COMMENT 'BMI指数',
ADD COLUMN bmr FLOAT DEFAULT 0.0 COMMENT '基础代谢率(kcal/天)';
