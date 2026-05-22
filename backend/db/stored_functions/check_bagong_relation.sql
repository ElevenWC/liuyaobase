-- check_bagong_relation: 八宫变化类型（一世~游魂~归魂），不匹配返回 ''
-- 卦代码 index: 1=初爻 ... 6=上爻。上爻(第6位)永不参与变化。
-- SUBSTRING(str, pos, 1) pos 从 1 开始。
-- 例: SELECT check_bagong_relation('111111', '011111'); -- '一世'
DROP FUNCTION IF EXISTS check_bagong_relation;
CREATE FUNCTION check_bagong_relation(ben_code VARCHAR(6), zhi_code VARCHAR(6))
RETURNS VARCHAR(4) CHARSET utf8mb4
DETERMINISTIC
BEGIN
    DECLARE current_code VARCHAR(6);
    DECLARE c1 CHAR(1); DECLARE c2 CHAR(1); DECLARE c3 CHAR(1);
    DECLARE c4 CHAR(1); DECLARE c5 CHAR(1); DECLARE c6 CHAR(1);

    IF ben_code = zhi_code THEN RETURN ''; END IF;

    SET current_code = ben_code;

    -- 一世: 翻初爻(pos=1)
    SET c1 = IF(SUBSTRING(current_code, 1, 1) = '1', '0', '1');
    SET current_code = CONCAT(c1, SUBSTRING(current_code, 2, 5));
    IF current_code = zhi_code THEN RETURN '一世'; END IF;

    -- 二世: 翻二爻(pos=2)
    SET c2 = IF(SUBSTRING(current_code, 2, 1) = '1', '0', '1');
    SET current_code = CONCAT(SUBSTRING(current_code, 1, 1), c2, SUBSTRING(current_code, 3, 4));
    IF current_code = zhi_code THEN RETURN '二世'; END IF;

    -- 三世: 翻三爻(pos=3)
    SET c3 = IF(SUBSTRING(current_code, 3, 1) = '1', '0', '1');
    SET current_code = CONCAT(SUBSTRING(current_code, 1, 2), c3, SUBSTRING(current_code, 4, 3));
    IF current_code = zhi_code THEN RETURN '三世'; END IF;

    -- 四世: 翻四爻(pos=4)
    SET c4 = IF(SUBSTRING(current_code, 4, 1) = '1', '0', '1');
    SET current_code = CONCAT(SUBSTRING(current_code, 1, 3), c4, SUBSTRING(current_code, 5, 2));
    IF current_code = zhi_code THEN RETURN '四世'; END IF;

    -- 五世: 翻五爻(pos=5)
    SET c5 = IF(SUBSTRING(current_code, 5, 1) = '1', '0', '1');
    SET current_code = CONCAT(SUBSTRING(current_code, 1, 4), c5, SUBSTRING(current_code, 6, 1));
    IF current_code = zhi_code THEN RETURN '五世'; END IF;

    -- 游魂: 翻四爻(pos=4)
    SET c4 = IF(SUBSTRING(current_code, 4, 1) = '1', '0', '1');
    SET current_code = CONCAT(SUBSTRING(current_code, 1, 3), c4, SUBSTRING(current_code, 5, 2));
    IF current_code = zhi_code THEN RETURN '游魂'; END IF;

    -- 归魂: 翻初爻+二爻+三爻(pos=1,2,3)
    SET c1 = IF(SUBSTRING(current_code, 1, 1) = '1', '0', '1');
    SET c2 = IF(SUBSTRING(current_code, 2, 1) = '1', '0', '1');
    SET c3 = IF(SUBSTRING(current_code, 3, 1) = '1', '0', '1');
    SET current_code = CONCAT(c1, c2, c3, SUBSTRING(current_code, 4, 3));
    IF current_code = zhi_code THEN RETURN '归魂'; END IF;

    RETURN '';
END;
