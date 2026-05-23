-- ============================================
-- liuyaobase 建表 SQL（18 张表 + 36 个索引）
-- 来源：.AIDiscuss/.A1数据库设计.md v5.1 §六
-- ============================================

-- 删除旧版遗留表（不属于当前设计，可能引用当前表）
DROP TABLE IF EXISTS yao_detail;
DROP TABLE IF EXISTS yanqing;

-- 删除旧表（按依赖关系倒序删除 —— 当前设计 18 张表）
DROP TABLE IF EXISTS guali_yao;
DROP TABLE IF EXISTS guali_gua;
DROP TABLE IF EXISTS guali_shensha;
DROP TABLE IF EXISTS guali_time;
DROP TABLE IF EXISTS futures_minute_kline;
DROP TABLE IF EXISTS futures_info;
DROP TABLE IF EXISTS stock_minute_kline;
DROP TABLE IF EXISTS stock_day_kline;
DROP TABLE IF EXISTS stock_info;
DROP TABLE IF EXISTS guali_tag;
DROP TABLE IF EXISTS tag;
DROP TABLE IF EXISTS guaci;
DROP TABLE IF EXISTS static_fushen_yimao;
DROP TABLE IF EXISTS static_fushen_zengshan;
DROP TABLE IF EXISTS static_gua_yao_info;
DROP TABLE IF EXISTS bagong_gua;
DROP TABLE IF EXISTS guali;
DROP TABLE IF EXISTS system_config;

-- ============================================
-- 一、核心模块（5张表）
-- ============================================

-- 1. 卦例表
CREATE TABLE guali (
    id INT AUTO_INCREMENT PRIMARY KEY,
    zhanwen_time DATETIME NOT NULL COMMENT '占问时间',
    zhanwen_shiyou TEXT COMMENT '占问事由',
    zhanduan TEXT COMMENT '占断内容',
    ben_code VARCHAR(6) NOT NULL COMMENT '本卦代码',
    yao_bian_code VARCHAR(6) NOT NULL DEFAULT '000000' COMMENT '爻变代码',
    zhi_code VARCHAR(6) NOT NULL DEFAULT '000000' COMMENT '之卦代码',
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT '卦例主表';

-- guali 索引
CREATE INDEX idx_ben_code ON guali(ben_code);
CREATE INDEX idx_zhi_code ON guali(zhi_code);

-- 2. 标签表
CREATE TABLE tag (
    id INT AUTO_INCREMENT PRIMARY KEY,
    parent_id INT NULL COMMENT '父标签ID',
    name VARCHAR(50) NOT NULL COMMENT '标签名称',
    FOREIGN KEY (parent_id) REFERENCES tag(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT '标签表';

-- 3. 卦例-标签关联表
CREATE TABLE guali_tag (
    guali_id INT NOT NULL,
    tag_id INT NOT NULL,
    PRIMARY KEY (guali_id, tag_id),
    FOREIGN KEY (guali_id) REFERENCES guali(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tag(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT '卦例-标签关联表';

-- 4. 八宫卦序表
CREATE TABLE bagong_gua (
    code VARCHAR(6) PRIMARY KEY COMMENT '卦代码',
    name VARCHAR(20) NOT NULL COMMENT '卦名',
    palace VARCHAR(10) NOT NULL COMMENT '卦宫',
    element VARCHAR(5) NOT NULL COMMENT '五行',
    palace_type VARCHAR(10) NOT NULL COMMENT '宫位类型'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT '八宫卦序表';

-- 5. 卦爻辞表
CREATE TABLE guaci (
    code VARCHAR(6) PRIMARY KEY COMMENT '卦代码',
    gua_ci TEXT COMMENT '卦辞',
    tuan_zhuan TEXT COMMENT '彖传',
    xiang_zhuan TEXT COMMENT '象传',
    yao_ci JSON COMMENT '爻辞（JSON格式）',
    wenyan TEXT COMMENT '文言（仅乾坤二卦）',
    yong JSON COMMENT '用九/用六（仅乾坤二卦）',
    FOREIGN KEY (code) REFERENCES bagong_gua(code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT '卦爻辞表';

-- ============================================
-- 二、系统配置（1张表）
-- ============================================

-- 6. 系统配置表
CREATE TABLE system_config (
    config_key VARCHAR(50) PRIMARY KEY COMMENT '配置项名称',
    config_value TEXT COMMENT '配置项值'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT '系统配置表';

-- ============================================
-- 三、股票模块（3张表）
-- ============================================

-- 7. 股票信息表
CREATE TABLE stock_info (
    id INT AUTO_INCREMENT PRIMARY KEY,
    stock_code VARCHAR(20) NOT NULL UNIQUE COMMENT '股票代码',
    stock_name VARCHAR(50) NOT NULL COMMENT '股票名称',
    exchange VARCHAR(20) COMMENT '交易所',
    data_source VARCHAR(20) COMMENT '数据来源',
    tag_id INT COMMENT '关联标签ID',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tag_id) REFERENCES tag(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT '股票信息表';

-- 8. 日K数据表
CREATE TABLE stock_day_kline (
    id INT AUTO_INCREMENT PRIMARY KEY,
    stock_id INT NOT NULL COMMENT '股票ID',
    trade_date DATE NOT NULL COMMENT '交易日期',
    open_price DECIMAL(10,2) COMMENT '开盘价',
    high_price DECIMAL(10,2) COMMENT '最高价',
    low_price DECIMAL(10,2) COMMENT '最低价',
    close_price DECIMAL(10,2) COMMENT '收盘价',
    volume BIGINT COMMENT '成交量',
    FOREIGN KEY (stock_id) REFERENCES stock_info(id) ON DELETE CASCADE,
    UNIQUE KEY uk_stock_date (stock_id, trade_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT '股票日K数据表';

-- 9. 股票分钟K线表（OHLC结构）
CREATE TABLE stock_minute_kline (
    id INT AUTO_INCREMENT PRIMARY KEY,
    stock_id INT NOT NULL COMMENT '股票ID',
    trade_time DATETIME NOT NULL COMMENT '交易时间（精确到分钟）',
    open_price DECIMAL(10,2) COMMENT '开盘价',
    high_price DECIMAL(10,2) COMMENT '最高价',
    low_price DECIMAL(10,2) COMMENT '最低价',
    close_price DECIMAL(10,2) COMMENT '收盘价',
    volume BIGINT COMMENT '成交量',
    FOREIGN KEY (stock_id) REFERENCES stock_info(id) ON DELETE CASCADE,
    INDEX idx_stock_time (stock_id, trade_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT '股票分时数据表';

-- ============================================
-- 四、64卦固定属性预计算（3张表）static_* 前缀
-- ============================================

-- 10. 卦爻属性表
CREATE TABLE static_gua_yao_info (
    code VARCHAR(6) NOT NULL COMMENT '卦代码',
    yao_index INT NOT NULL COMMENT '爻位（1-6）',
    dizhi VARCHAR(1) NOT NULL COMMENT '地支',
    tiangan VARCHAR(1) COMMENT '天干（普通卦）',
    tiangan_summer VARCHAR(1) COMMENT '天干-夏至后（乾坤相关卦）',
    tiangan_winter VARCHAR(1) COMMENT '天干-冬至后（乾坤相关卦）',
    liuqin VARCHAR(10) NOT NULL COMMENT '六亲',
    PRIMARY KEY (code, yao_index),
    FOREIGN KEY (code) REFERENCES bagong_gua(code) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT '64卦×6爻=384条记录';

-- 11. 增删伏神表
CREATE TABLE static_fushen_zengshan (
    code VARCHAR(6) NOT NULL COMMENT '卦代码',
    yao_index INT NOT NULL COMMENT '爻位（伏神伏在此爻位下）',
    missing_liuqin VARCHAR(10) NOT NULL COMMENT '缺失的六亲',
    fushen_dizhi VARCHAR(1) NOT NULL COMMENT '伏神地支',
    fushen_liuqin VARCHAR(10) NOT NULL COMMENT '伏神六亲',
    feishen_dizhi VARCHAR(1) NOT NULL COMMENT '飞神地支',
    feishen_liuqin VARCHAR(10) NOT NULL COMMENT '飞神六亲',
    PRIMARY KEY (code, yao_index),
    FOREIGN KEY (code) REFERENCES bagong_gua(code) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT '64卦约64条记录';

-- 12. 易冒伏神表
CREATE TABLE static_fushen_yimao (
    code VARCHAR(6) NOT NULL COMMENT '卦代码',
    yao_index INT NOT NULL COMMENT '爻位',
    fushen_dizhi VARCHAR(1) NOT NULL COMMENT '伏神地支',
    fushen_liuqin VARCHAR(10) NOT NULL COMMENT '伏神六亲',
    PRIMARY KEY (code, yao_index),
    FOREIGN KEY (code) REFERENCES bagong_gua(code) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT '64卦×6爻=384条记录';

-- ============================================
-- 五、卦例动态属性预计算（4张表）guali_* 前缀
-- ============================================

-- 13. 时间扩展表
CREATE TABLE guali_time (
    id INT AUTO_INCREMENT PRIMARY KEY,
    guali_id INT NOT NULL COMMENT '关联卦例ID',
    year_pillar VARCHAR(4) COMMENT '年柱',
    year_gan VARCHAR(2) COMMENT '年干',
    year_zhi VARCHAR(2) COMMENT '年支',
    month_pillar VARCHAR(4) COMMENT '月柱',
    month_gan VARCHAR(2) COMMENT '月干',
    month_zhi VARCHAR(2) COMMENT '月支',
    day_pillar VARCHAR(4) COMMENT '日柱',
    day_gan VARCHAR(2) COMMENT '日干',
    day_zhi VARCHAR(2) COMMENT '日支',
    xun_kong VARCHAR(4) COMMENT '旬空',
    UNIQUE KEY uk_guali_id (guali_id),
    FOREIGN KEY (guali_id) REFERENCES guali(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT '时间扩展表（1行/卦例）';

-- guali_time 索引
CREATE INDEX idx_time_guali_id ON guali_time(guali_id);
CREATE INDEX idx_year_zhi ON guali_time(year_zhi);
CREATE INDEX idx_month_zhi ON guali_time(month_zhi);
CREATE INDEX idx_day_gan ON guali_time(day_gan);
CREATE INDEX idx_day_zhi ON guali_time(day_zhi);
CREATE INDEX idx_xun_kong ON guali_time(xun_kong);

-- 14. 神煞扩展表
CREATE TABLE guali_shensha (
    id INT AUTO_INCREMENT PRIMARY KEY,
    guali_id INT NOT NULL COMMENT '关联卦例ID',
    gan_lu VARCHAR(2) COMMENT '干禄地支',
    yi_ma VARCHAR(2) COMMENT '驿马地支',
    yang_ren VARCHAR(2) COMMENT '羊刃地支',
    tao_hua VARCHAR(2) COMMENT '桃花地支',
    yimao_is_ganlu VARCHAR(10) DEFAULT '' COMMENT '是干禄的爻位',
    yimao_dai_ganlu VARCHAR(10) DEFAULT '' COMMENT '带干禄的爻位',
    yimao_is_yima VARCHAR(10) DEFAULT '' COMMENT '是驿马的爻位',
    yimao_dai_yima VARCHAR(10) DEFAULT '' COMMENT '带驿马的爻位',
    yimao_is_yangren VARCHAR(10) DEFAULT '' COMMENT '是羊刃的爻位',
    yimao_dai_yangren VARCHAR(10) DEFAULT '' COMMENT '带羊刃的爻位',
    yimao_is_taohua VARCHAR(10) DEFAULT '' COMMENT '是桃花的爻位',
    yimao_dai_taohua VARCHAR(10) DEFAULT '' COMMENT '带桃花的爻位',
    zengshan_is_ganlu VARCHAR(10) DEFAULT '' COMMENT '是干禄的爻位',
    zengshan_dai_ganlu VARCHAR(10) DEFAULT '' COMMENT '带干禄的爻位',
    zengshan_is_yima VARCHAR(10) DEFAULT '' COMMENT '是驿马的爻位',
    zengshan_dai_yima VARCHAR(10) DEFAULT '' COMMENT '带驿马的爻位',
    zengshan_is_yangren VARCHAR(10) DEFAULT '' COMMENT '是羊刃的爻位',
    zengshan_dai_yangren VARCHAR(10) DEFAULT '' COMMENT '带羊刃的爻位',
    zengshan_is_taohua VARCHAR(10) DEFAULT '' COMMENT '是桃花的爻位',
    zengshan_dai_taohua VARCHAR(10) DEFAULT '' COMMENT '带桃花的爻位',
    ben_is_ganlu VARCHAR(10) DEFAULT '' COMMENT '是干禄的爻位',
    ben_dai_ganlu VARCHAR(10) DEFAULT '' COMMENT '带干禄的爻位',
    ben_is_yima VARCHAR(10) DEFAULT '' COMMENT '是驿马的爻位',
    ben_dai_yima VARCHAR(10) DEFAULT '' COMMENT '带驿马的爻位',
    ben_is_yangren VARCHAR(10) DEFAULT '' COMMENT '是羊刃的爻位',
    ben_dai_yangren VARCHAR(10) DEFAULT '' COMMENT '带羊刃的爻位',
    ben_is_taohua VARCHAR(10) DEFAULT '' COMMENT '是桃花的爻位',
    ben_dai_taohua VARCHAR(10) DEFAULT '' COMMENT '带桃花的爻位',
    zhi_is_ganlu VARCHAR(10) DEFAULT '' COMMENT '是干禄的爻位',
    zhi_dai_ganlu VARCHAR(10) DEFAULT '' COMMENT '带干禄的爻位',
    zhi_is_yima VARCHAR(10) DEFAULT '' COMMENT '是驿马的爻位',
    zhi_dai_yima VARCHAR(10) DEFAULT '' COMMENT '带驿马的爻位',
    zhi_is_yangren VARCHAR(10) DEFAULT '' COMMENT '是羊刃的爻位',
    zhi_dai_yangren VARCHAR(10) DEFAULT '' COMMENT '带羊刃的爻位',
    zhi_is_taohua VARCHAR(10) DEFAULT '' COMMENT '是桃花的爻位',
    zhi_dai_taohua VARCHAR(10) DEFAULT '' COMMENT '带桃花的爻位',
    UNIQUE KEY uk_guali_id (guali_id),
    FOREIGN KEY (guali_id) REFERENCES guali(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT '神煞扩展表（1行/卦例，37字段）';

-- guali_shensha 索引
CREATE INDEX idx_shensha_guali_id ON guali_shensha(guali_id);
CREATE INDEX idx_gan_lu ON guali_shensha(gan_lu);
CREATE INDEX idx_yi_ma ON guali_shensha(yi_ma);
CREATE INDEX idx_yang_ren ON guali_shensha(yang_ren);
CREATE INDEX idx_tao_hua ON guali_shensha(tao_hua);

-- 15. 卦类扩展表
CREATE TABLE guali_gua (
    id INT AUTO_INCREMENT PRIMARY KEY,
    guali_id INT NOT NULL COMMENT '关联卦例ID',
    ben_inner_code VARCHAR(3) COMMENT '本卦内卦代码',
    ben_outer_code VARCHAR(3) COMMENT '本卦外卦代码',
    ben_palace VARCHAR(10) COMMENT '本卦卦宫',
    ben_palace_type VARCHAR(10) COMMENT '本卦宫位',
    ben_special_type VARCHAR(10) COMMENT '本卦特殊类型',
    zhi_inner_code VARCHAR(3) COMMENT '之卦内卦代码',
    zhi_outer_code VARCHAR(3) COMMENT '之卦外卦代码',
    zhi_palace VARCHAR(10) COMMENT '之卦卦宫',
    zhi_palace_type VARCHAR(10) COMMENT '之卦宫位',
    zhi_special_type VARCHAR(10) COMMENT '之卦特殊类型',
    fan_yin_yimao VARCHAR(4) COMMENT '易冒反吟',
    fan_yin_yaobian VARCHAR(4) COMMENT '爻变反吟',
    fu_yin VARCHAR(4) COMMENT '伏吟',
    UNIQUE KEY uk_guali_id (guali_id),
    FOREIGN KEY (guali_id) REFERENCES guali(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT '卦类扩展表（1行/卦例，14字段）';

-- guali_gua 索引
CREATE INDEX idx_gua_guali_id ON guali_gua(guali_id);
CREATE INDEX idx_ben_palace ON guali_gua(ben_palace);
CREATE INDEX idx_zhi_palace ON guali_gua(zhi_palace);
CREATE INDEX idx_ben_palace_type ON guali_gua(ben_palace_type);
CREATE INDEX idx_zhi_palace_type ON guali_gua(zhi_palace_type);
CREATE INDEX idx_ben_special_type ON guali_gua(ben_special_type);
CREATE INDEX idx_zhi_special_type ON guali_gua(zhi_special_type);
CREATE INDEX idx_fan_yin ON guali_gua(fan_yin_yimao, fan_yin_yaobian, fu_yin);

-- 16. 爻类扩展表
CREATE TABLE guali_yao (
    id INT AUTO_INCREMENT PRIMARY KEY,
    guali_id INT NOT NULL COMMENT '关联卦例ID',
    yao_position TINYINT NOT NULL COMMENT '爻位（1-6）',
    liushen VARCHAR(10) COMMENT '六神',
    yimao_liuqin VARCHAR(10) COMMENT '易冒伏神六亲',
    yimao_dizhi VARCHAR(2) COMMENT '易冒伏神地支',
    zengshan_exists BOOLEAN DEFAULT FALSE COMMENT '是否存在增删伏神',
    zengshan_liuqin VARCHAR(10) COMMENT '增删伏神六亲',
    zengshan_dizhi VARCHAR(2) COMMENT '增删伏神地支',
    ben_yao_type VARCHAR(2) COMMENT '本卦爻类型（阴/阳）',
    ben_liuqin VARCHAR(10) COMMENT '本卦六亲',
    ben_tiangan VARCHAR(2) COMMENT '本卦天干',
    ben_dizhi VARCHAR(2) COMMENT '本卦地支',
    ben_shi_ying VARCHAR(4) COMMENT '本卦世应',
    is_dong BOOLEAN DEFAULT FALSE COMMENT '是否动爻',
    is_an_dong BOOLEAN DEFAULT FALSE COMMENT '是否暗动',
    zhi_yao_type VARCHAR(2) COMMENT '之卦爻类型（阴/阳）',
    zhi_liuqin VARCHAR(10) COMMENT '之卦六亲',
    zhi_tiangan VARCHAR(2) COMMENT '之卦天干',
    zhi_dizhi VARCHAR(2) COMMENT '之卦地支',
    zhi_shi_ying VARCHAR(4) COMMENT '之卦世应',
    UNIQUE KEY uk_guali_yao (guali_id, yao_position),
    FOREIGN KEY (guali_id) REFERENCES guali(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT '爻类扩展表（6行/卦例，20字段）';

-- guali_yao 索引
CREATE INDEX idx_yao_guali_id ON guali_yao(guali_id);
CREATE INDEX idx_liushen ON guali_yao(liushen);
CREATE INDEX idx_ben_yao_type ON guali_yao(ben_yao_type);
CREATE INDEX idx_ben_liuqin ON guali_yao(ben_liuqin);
CREATE INDEX idx_ben_dizhi ON guali_yao(ben_dizhi);
CREATE INDEX idx_ben_shi_ying ON guali_yao(ben_shi_ying);
CREATE INDEX idx_is_dong ON guali_yao(is_dong);
CREATE INDEX idx_is_an_dong ON guali_yao(is_an_dong);
CREATE INDEX idx_zhi_liuqin ON guali_yao(zhi_liuqin);
CREATE INDEX idx_zhi_dizhi ON guali_yao(zhi_dizhi);
CREATE INDEX idx_yimao_liuqin ON guali_yao(yimao_liuqin);
CREATE INDEX idx_yimao_dizhi ON guali_yao(yimao_dizhi);
CREATE INDEX idx_zengshan_liuqin ON guali_yao(zengshan_liuqin);
CREATE INDEX idx_zengshan_dizhi ON guali_yao(zengshan_dizhi);
CREATE INDEX idx_zengshan_exists ON guali_yao(zengshan_exists);

-- ============================================
-- 六、期货模块（2张表）
-- ============================================

-- 17. 期货信息表
CREATE TABLE futures_info (
    id INT AUTO_INCREMENT PRIMARY KEY,
    futures_code VARCHAR(20) NOT NULL UNIQUE COMMENT '期货代码',
    futures_name VARCHAR(50) NOT NULL COMMENT '期货名称',
    exchange VARCHAR(20) COMMENT '交易所',
    night_session VARCHAR(10) COMMENT '交易时段类型：无/短(23:00)/长(02:30)/外盘(24h)',
    data_source VARCHAR(20) COMMENT '数据来源',
    tag_id INT COMMENT '关联标签ID',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tag_id) REFERENCES tag(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT '期货信息表';

-- 18. 期货分钟K线表（OHLC结构，日K由此实时聚合）
CREATE TABLE futures_minute_kline (
    id INT AUTO_INCREMENT PRIMARY KEY,
    futures_id INT NOT NULL COMMENT '期货ID',
    trade_time DATETIME NOT NULL COMMENT '交易时间（精确到分钟，含夜盘跨天时间）',
    open_price DECIMAL(10,2) COMMENT '开盘价',
    high_price DECIMAL(10,2) COMMENT '最高价',
    low_price DECIMAL(10,2) COMMENT '最低价',
    close_price DECIMAL(10,2) COMMENT '收盘价',
    volume BIGINT COMMENT '成交量',
    FOREIGN KEY (futures_id) REFERENCES futures_info(id) ON DELETE CASCADE,
    INDEX idx_futures_time (futures_id, trade_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT '期货分钟K线表';
