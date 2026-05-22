-- check_shengwang: 生旺墓绝判断
-- sw_type: '长生'/'帝旺'/'墓'/'绝'
-- 土与水同宫（申子辰巳）
-- 例: SELECT check_shengwang('寅', '亥', '长生'); -- 1（木长生在亥）
DROP FUNCTION IF EXISTS check_shengwang;
CREATE FUNCTION check_shengwang(dizhi VARCHAR(2), target VARCHAR(2), sw_type VARCHAR(4))
RETURNS BOOLEAN
DETERMINISTIC
BEGIN
    DECLARE wx VARCHAR(1);
    DECLARE expected VARCHAR(2);

    -- 地支 → 五行
    SET wx = CASE dizhi
        WHEN '子' THEN '水' WHEN '亥' THEN '水'
        WHEN '寅' THEN '木' WHEN '卯' THEN '木'
        WHEN '巳' THEN '火' WHEN '午' THEN '火'
        WHEN '申' THEN '金' WHEN '酉' THEN '金'
        WHEN '丑' THEN '土' WHEN '辰' THEN '土'
        WHEN '未' THEN '土' WHEN '戌' THEN '土'
        ELSE '' END;

    IF wx = '' THEN RETURN FALSE; END IF;

    -- 土与水同宫
    IF wx = '土' THEN SET wx = '水'; END IF;

    -- 查表
    IF sw_type = '长生' THEN
        SET expected = CASE wx
            WHEN '木' THEN '亥' WHEN '火' THEN '寅'
            WHEN '金' THEN '巳' WHEN '水' THEN '申' END;
    ELSEIF sw_type = '帝旺' THEN
        SET expected = CASE wx
            WHEN '木' THEN '卯' WHEN '火' THEN '午'
            WHEN '金' THEN '酉' WHEN '水' THEN '子' END;
    ELSEIF sw_type = '墓' THEN
        SET expected = CASE wx
            WHEN '木' THEN '未' WHEN '火' THEN '戌'
            WHEN '金' THEN '丑' WHEN '水' THEN '辰' END;
    ELSEIF sw_type = '绝' THEN
        SET expected = CASE wx
            WHEN '木' THEN '申' WHEN '火' THEN '亥'
            WHEN '金' THEN '寅' WHEN '水' THEN '巳' END;
    ELSE
        RETURN FALSE;
    END IF;

    RETURN target = expected;
END;
