-- check_sanhe: 三合局？返回五行字（水/木/火/金），不形成返回 ''
-- 例: SELECT check_sanhe('申','子','辰'); -- '水'
DROP FUNCTION IF EXISTS check_sanhe;
CREATE FUNCTION check_sanhe(dizhi_a VARCHAR(2), dizhi_b VARCHAR(2), dizhi_c VARCHAR(2))
RETURNS VARCHAR(2) CHARSET utf8mb4
DETERMINISTIC
BEGIN
    -- 重复地支 → 不构成三合
    IF dizhi_a = dizhi_b OR dizhi_b = dizhi_c OR dizhi_a = dizhi_c THEN
        RETURN '';
    END IF;

    -- 将三个地支合起来判断（利用查表 + 6 种排列）
    IF (dizhi_a = '申' AND dizhi_b = '子' AND dizhi_c = '辰')
    OR (dizhi_a = '申' AND dizhi_b = '辰' AND dizhi_c = '子')
    OR (dizhi_a = '子' AND dizhi_b = '申' AND dizhi_c = '辰')
    OR (dizhi_a = '子' AND dizhi_b = '辰' AND dizhi_c = '申')
    OR (dizhi_a = '辰' AND dizhi_b = '申' AND dizhi_c = '子')
    OR (dizhi_a = '辰' AND dizhi_b = '子' AND dizhi_c = '申') THEN
        RETURN '水';
    END IF;

    IF (dizhi_a = '亥' AND dizhi_b = '卯' AND dizhi_c = '未')
    OR (dizhi_a = '亥' AND dizhi_b = '未' AND dizhi_c = '卯')
    OR (dizhi_a = '卯' AND dizhi_b = '亥' AND dizhi_c = '未')
    OR (dizhi_a = '卯' AND dizhi_b = '未' AND dizhi_c = '亥')
    OR (dizhi_a = '未' AND dizhi_b = '亥' AND dizhi_c = '卯')
    OR (dizhi_a = '未' AND dizhi_b = '卯' AND dizhi_c = '亥') THEN
        RETURN '木';
    END IF;

    IF (dizhi_a = '寅' AND dizhi_b = '午' AND dizhi_c = '戌')
    OR (dizhi_a = '寅' AND dizhi_b = '戌' AND dizhi_c = '午')
    OR (dizhi_a = '午' AND dizhi_b = '寅' AND dizhi_c = '戌')
    OR (dizhi_a = '午' AND dizhi_b = '戌' AND dizhi_c = '寅')
    OR (dizhi_a = '戌' AND dizhi_b = '寅' AND dizhi_c = '午')
    OR (dizhi_a = '戌' AND dizhi_b = '午' AND dizhi_c = '寅') THEN
        RETURN '火';
    END IF;

    IF (dizhi_a = '巳' AND dizhi_b = '酉' AND dizhi_c = '丑')
    OR (dizhi_a = '巳' AND dizhi_b = '丑' AND dizhi_c = '酉')
    OR (dizhi_a = '酉' AND dizhi_b = '巳' AND dizhi_c = '丑')
    OR (dizhi_a = '酉' AND dizhi_b = '丑' AND dizhi_c = '巳')
    OR (dizhi_a = '丑' AND dizhi_b = '巳' AND dizhi_c = '酉')
    OR (dizhi_a = '丑' AND dizhi_b = '酉' AND dizhi_c = '巳') THEN
        RETURN '金';
    END IF;

    RETURN '';
END;
