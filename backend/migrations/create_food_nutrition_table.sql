-- 食物营养成分表
CREATE TABLE IF NOT EXISTS food_nutrition (
    id INT PRIMARY KEY AUTO_INCREMENT,
    external_id VARCHAR(50) COMMENT '外部数据源ID',
    name VARCHAR(100) NOT NULL COMMENT '食物名称',
    category VARCHAR(50) COMMENT '分类（谷薯/蛋类/蔬菜等）',
    calories DECIMAL(8,2) NOT NULL COMMENT '热量(千卡/100g)',
    protein DECIMAL(8,2) DEFAULT 0 COMMENT '蛋白质(g/100g)',
    carbs DECIMAL(8,2) DEFAULT 0 COMMENT '碳水化合物(g/100g)',
    fat DECIMAL(8,2) DEFAULT 0 COMMENT '脂肪(g/100g)',
    fiber DECIMAL(8,2) DEFAULT 0 COMMENT '膳食纤维(g/100g)',
    sodium DECIMAL(8,2) DEFAULT 0 COMMENT '钠(mg/100g)',
    image_url VARCHAR(500) COMMENT '图片URL（七牛云）',
    unit VARCHAR(20) DEFAULT '100g' COMMENT '计量单位',
    source VARCHAR(50) DEFAULT 'miaofoods' COMMENT '数据来源',
    is_custom TINYINT(1) DEFAULT 0 COMMENT '是否用户自定义',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_name (name),
    INDEX idx_category (category),
    INDEX idx_external_id (external_id),
    UNIQUE KEY uk_external_id_source (external_id, source)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='食物营养成分表';
