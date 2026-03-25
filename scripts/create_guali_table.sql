-- 六爻卦例分析系统 - 数据库表结构
-- 数据库名: liuyao

-- 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS liuyao DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE liuyao;

-- 卦例表
CREATE TABLE IF NOT EXISTS guali (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '卦例ID',
    solar_year INT NOT NULL COMMENT '公历年',
    solar_month INT NOT NULL COMMENT '公历月',
    solar_day INT NOT NULL COMMENT '公历日',
    ganzhi_year VARCHAR(4) NOT NULL COMMENT '年柱(干支)',
    ganzhi_month VARCHAR(4) NOT NULL COMMENT '月柱(干支)',
    ganzhi_day VARCHAR(4) NOT NULL COMMENT '日柱(干支)',
    xunkong VARCHAR(8) NOT NULL COMMENT '旬空',
    ben_gua_code INT NOT NULL COMMENT '本卦代码(6位二进制转十进制)',
    zhi_gua_code INT DEFAULT NULL COMMENT '之卦代码(6位二进制转十进制)',
    yao_bian_code INT NOT NULL DEFAULT 0 COMMENT '爻变代码(6位二进制转十进制)',
    gongwei VARCHAR(8) NOT NULL COMMENT '卦宫',
    gongwei_index VARCHAR(8) NOT NULL COMMENT '宫位',
    zhan_wen TEXT DEFAULT NULL COMMENT '占问事由',
    zhan_duan TEXT DEFAULT NULL COMMENT '占断',
    image_path VARCHAR(512) DEFAULT NULL COMMENT '图片路径',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    INDEX idx_time (solar_year, solar_month, solar_day),
    INDEX idx_gua (ben_gua_code, zhi_gua_code),
    INDEX idx_gongwei (gongwei),
    INDEX idx_gongwei_index (gongwei_index)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='卦例表';

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

-- 占验情况表 (独立于主数据库的弱耦合系统)
CREATE TABLE IF NOT EXISTS yanqing (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '占验ID',
    guali_id INT NOT NULL COMMENT '卦例ID',
    status VARCHAR(8) NOT NULL COMMENT '占验状态(应验/模糊/不验)',
    note TEXT DEFAULT NULL COMMENT '标注说明',
    annotated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '标注时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    UNIQUE INDEX idx_guali_id (guali_id),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='占验情况表';
