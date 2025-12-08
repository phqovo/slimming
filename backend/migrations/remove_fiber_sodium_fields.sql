-- 移除食物营养表中的膳食纤维和钠字段
-- 执行日期: 2025-11-17

ALTER TABLE food_nutrition DROP COLUMN fiber;
ALTER TABLE food_nutrition DROP COLUMN sodium;
