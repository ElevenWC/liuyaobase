-- 六爻卦例分析系统 - 爻详情表创建脚本
-- (已包含在 create_guali_table.sql 中，此文件为独立创建脚本)

USE liuyao;

-- 爻详情表
CREATE TABLE IF NOT EXISTS yao_detail (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '爻详情ID',
    guali_id INT NOT NULL COMMENT '卦例ID',
    position INT NOT NULL COMMENT '爻位(1-6: 初爻到上爻)',
    yao_type INT NOT NULL COMMENT '爻类型(1=阳爻, 0=阴爻)',
    state INT NOT NULL DEFAULT 0 COMMENT '爻状态(1=动爻, 0=静爻)',
    dizhi VARCHAR(4) NOT NULL COMMENT '地支',
    liuqin VARCHAR(8) DEFAULT NULL COMMENT '六亲',
    liushen VARCHAR(8) DEFAULT NULL COMMENT '六神',
    is_world BOOLEAN DEFAULT FALSE COMMENT '是否世爻',
    is_response BOOLEAN DEFAULT FALSE COMMENT '是否应爻',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',

    FOREIGN KEY (guali_id) REFERENCES guali(id) ON DELETE CASCADE,
    INDEX idx_guali_id (guali_id),
    INDEX idx_dizhi (dizhi),
    INDEX idx_liuqin (liuqin),
    INDEX idx_liushen (liushen),
    INDEX idx_position (position)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='爻详情表';
