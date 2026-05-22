-- check_chong: 六冲？（6 组，无顺序）
-- 例: SELECT check_chong('子', '午'); -- 1
DROP FUNCTION IF EXISTS check_chong;
CREATE FUNCTION check_chong(dizhi_a VARCHAR(2), dizhi_b VARCHAR(2))
RETURNS BOOLEAN
DETERMINISTIC
BEGIN
    IF dizhi_a = dizhi_b THEN RETURN FALSE; END IF;

    RETURN (dizhi_a = '子' AND dizhi_b = '午') OR (dizhi_a = '午' AND dizhi_b = '子')
        OR (dizhi_a = '丑' AND dizhi_b = '未') OR (dizhi_a = '未' AND dizhi_b = '丑')
        OR (dizhi_a = '寅' AND dizhi_b = '申') OR (dizhi_a = '申' AND dizhi_b = '寅')
        OR (dizhi_a = '卯' AND dizhi_b = '酉') OR (dizhi_a = '酉' AND dizhi_b = '卯')
        OR (dizhi_a = '辰' AND dizhi_b = '戌') OR (dizhi_a = '戌' AND dizhi_b = '辰')
        OR (dizhi_a = '巳' AND dizhi_b = '亥') OR (dizhi_a = '亥' AND dizhi_b = '巳');
END;
