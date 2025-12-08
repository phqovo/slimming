-- 为daily_history表添加唯一约束，防止同一天同一用户有多条记录

-- 1. 先清理重复数据，保留每个用户每天最新的一条记录
DELETE t1 FROM daily_history t1
INNER JOIN daily_history t2 
WHERE 
    t1.user_id = t2.user_id 
    AND t1.record_date = t2.record_date 
    AND t1.id < t2.id;

-- 2. 添加唯一约束
ALTER TABLE daily_history 
ADD UNIQUE KEY `uk_user_date` (`user_id`, `record_date`);
