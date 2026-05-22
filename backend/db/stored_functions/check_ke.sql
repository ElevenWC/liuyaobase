-- check_ke: A 克 B？（有方向）
-- 例: SELECT check_ke('子', '午'); -- 1（水克火）
DROP FUNCTION IF EXISTS check_ke;
CREATE FUNCTION check_ke(dizhi_a VARCHAR(2), dizhi_b VARCHAR(2))
RETURNS BOOLEAN
DETERMINISTIC
BEGIN
    DECLARE wx_a VARCHAR(1);
    DECLARE wx_b VARCHAR(1);

    SET wx_a = CASE dizhi_a
        WHEN '子' THEN '水' WHEN '亥' THEN '水'
        WHEN '寅' THEN '木' WHEN '卯' THEN '木'
        WHEN '巳' THEN '火' WHEN '午' THEN '火'
        WHEN '申' THEN '金' WHEN '酉' THEN '金'
        WHEN '丑' THEN '土' WHEN '辰' THEN '土'
        WHEN '未' THEN '土' WHEN '戌' THEN '土'
        ELSE '' END;

    SET wx_b = CASE dizhi_b
        WHEN '子' THEN '水' WHEN '亥' THEN '水'
        WHEN '寅' THEN '木' WHEN '卯' THEN '木'
        WHEN '巳' THEN '火' WHEN '午' THEN '火'
        WHEN '申' THEN '金' WHEN '酉' THEN '金'
        WHEN '丑' THEN '土' WHEN '辰' THEN '土'
        WHEN '未' THEN '土' WHEN '戌' THEN '土'
        ELSE '' END;

    IF wx_a = '' OR wx_b = '' THEN RETURN FALSE; END IF;

    -- 相克链: 木→土→水→火→金→木
    RETURN (wx_a = '木' AND wx_b = '土')
        OR (wx_a = '土' AND wx_b = '水')
        OR (wx_a = '水' AND wx_b = '火')
        OR (wx_a = '火' AND wx_b = '金')
        OR (wx_a = '金' AND wx_b = '木');
END;
