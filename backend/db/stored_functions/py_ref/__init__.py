"""8 个地支关系判断函数 —— Python 参考实现

每个函数先在此验证逻辑正确性，再移植为 MySQL 存储函数。
"""
from typing import List

# ── 常量 ──────────────────────────────────────────────

# 地支 → 五行
_WUXING: dict[str, str] = {
    "子": "水", "丑": "土", "寅": "木", "卯": "木",
    "辰": "土", "巳": "火", "午": "火", "未": "土",
    "申": "金", "酉": "金", "戌": "土", "亥": "水",
}

# 相生链（key 生 values）
_SHENG: dict[str, list[str]] = {
    "木": ["火"], "火": ["土"], "土": ["金"],
    "金": ["水"], "水": ["木"],
}
# 相克链（key 克 values）
_KE: dict[str, list[str]] = {
    "木": ["土"], "土": ["水"], "水": ["火"],
    "火": ["金"], "金": ["木"],
}

# 六合 6 组（无序）
_HE_PAIRS = [
    {"子", "丑"}, {"寅", "亥"}, {"卯", "戌"},
    {"辰", "酉"}, {"巳", "申"}, {"午", "未"},
]
# 六冲 6 组（无序）
_CHONG_PAIRS = [
    {"子", "午"}, {"丑", "未"}, {"寅", "申"},
    {"卯", "酉"}, {"辰", "戌"}, {"巳", "亥"},
]
# 半合 8 组（无序）
_BANHE_PAIRS = [
    {"申", "子"}, {"子", "辰"}, {"亥", "卯"}, {"卯", "未"},
    {"寅", "午"}, {"午", "戌"}, {"巳", "酉"}, {"酉", "丑"},
]
# 三合 4 局（frozenset 消除顺序）
_SANHE_JU = {
    frozenset({"申", "子", "辰"}): "水",
    frozenset({"亥", "卯", "未"}): "木",
    frozenset({"寅", "午", "戌"}): "火",
    frozenset({"巳", "酉", "丑"}): "金",
}

# 生旺墓绝表：五行 → [长生, 帝旺, 墓, 绝]
# 土与水同宫（申子辰巳）
_SHENGWANG_TABLE: dict[str, list[str]] = {
    "木": ["亥", "卯", "未", "申"],
    "火": ["寅", "午", "戌", "亥"],
    "土": ["申", "子", "辰", "巳"],
    "金": ["巳", "酉", "丑", "寅"],
    "水": ["申", "子", "辰", "巳"],
}
_SW_INDEX = {"长生": 0, "帝旺": 1, "墓": 2, "绝": 3}

# 八宫变化：从 000 到 111 的 8 个三爻码
_EIGHT_GUA = ["000", "001", "010", "011", "100", "101", "110", "111"]

# ── 函数实现 ──────────────────────────────────────────

def _valid(zhi: str) -> str:
    if zhi not in _WUXING:
        raise ValueError(f"无效地支: {zhi}")
    return zhi


def check_sheng(a: str, b: str) -> bool:
    """A 生 B？有方向。"""
    return _WUXING[b] in _SHENG.get(_WUXING[_valid(a)], [])


def check_ke(a: str, b: str) -> bool:
    """A 克 B？有方向。"""
    return _WUXING[b] in _KE.get(_WUXING[_valid(a)], [])


def check_he(a: str, b: str) -> bool:
    """六合？6 组，无顺序。"""
    _valid(a); _valid(b)
    if a == b:
        return False
    return {a, b} in _HE_PAIRS


def check_chong(a: str, b: str) -> bool:
    """六冲？6 组，无顺序。"""
    _valid(a); _valid(b)
    if a == b:
        return False
    return {a, b} in _CHONG_PAIRS


def check_banhe(a: str, b: str) -> bool:
    """半合？8 组，无顺序。"""
    _valid(a); _valid(b)
    if a == b:
        return False
    return {a, b} in _BANHE_PAIRS


def check_sanhe(a: str, b: str, c: str) -> str:
    """三合局？返回五行字（水/木/火/金），不形成返回 ''。"""
    _valid(a); _valid(b); _valid(c)
    if a == b or b == c or a == c:
        return ""
    return _SANHE_JU.get(frozenset({a, b, c}), "")


def check_shengwang(dizhi: str, target: str, sw_type: str) -> bool:
    """生旺墓绝判断。sw_type: '长生'/'帝旺'/'墓'/'绝'"""
    _valid(dizhi); _valid(target)
    if sw_type not in _SW_INDEX:
        raise ValueError(f"无效的生旺墓绝类型: {sw_type}")
    wuxing = _WUXING[dizhi]
    idx = _SW_INDEX[sw_type]
    return target == _SHENGWANG_TABLE[wuxing][idx]


def check_bagong_relation(ben_code: str, zhi_code: str) -> str:
    """八宫变化类型（一世~游魂~归魂）。不匹配返回 ''。

    卦代码 index 0=初爻, index 5=上爻。上爻永不参与变化。
    """
    assert len(ben_code) == 6 and len(zhi_code) == 6, "卦代码必须为 6 位"
    if ben_code == zhi_code:
        return ""

    g: list[int] = [int(c) for c in ben_code]

    # 每步累积变化：index 0=初爻, 1=二爻, 2=三爻, 3=四爻, 4=五爻, 5=上爻(不动)
    steps: list[tuple[str, list[int]]] = [
        ("一世", [0]),           # 初爻
        ("二世", [1]),           # 二爻 (承接一世)
        ("三世", [2]),           # 三爻 (承接二世)
        ("四世", [3]),           # 四爻 (承接三世)
        ("五世", [4]),           # 五爻 (承接四世)
        ("游魂", [3]),           # 四爻 (承接五世, flip 四爻 back)
        ("归魂", [0, 1, 2]),     # 初二三爻 (承接游魂, flip all three)
    ]

    for name, indices in steps:
        for idx in indices:
            g[idx] = 1 - g[idx]
        if "".join(str(b) for b in g) == zhi_code:
            return name

    return ""


# ── 测试用例 ──────────────────────────────────────────

def _run_tests() -> list[str]:
    """运行所有测试，返回失败的用例描述列表。"""
    failures: list[str] = []
    def assert_eq(actual, expected, label=""):
        if actual != expected:
            failures.append(f"{label}: expected {expected!r}, got {actual!r}")

    # --- check_sheng (≥10) ---
    assert_eq(check_sheng("子", "寅"), True, "子生寅")
    assert_eq(check_sheng("寅", "子"), False, "寅生子")
    assert_eq(check_sheng("寅", "午"), True, "木生火")
    assert_eq(check_sheng("午", "辰"), True, "火生土")
    assert_eq(check_sheng("辰", "酉"), True, "土生金")
    assert_eq(check_sheng("酉", "亥"), True, "金生水")
    assert_eq(check_sheng("亥", "卯"), True, "水生木")
    assert_eq(check_sheng("巳", "丑"), True, "火生土")
    assert_eq(check_sheng("子", "午"), False, "水不生火")
    assert_eq(check_sheng("申", "寅"), False, "金不生木")
    assert_eq(check_sheng("丑", "戌"), False, "土不生土(同五行)")

    # --- check_ke (≥10) ---
    assert_eq(check_ke("子", "午"), True, "子克午")
    assert_eq(check_ke("午", "酉"), True, "火克金")
    assert_eq(check_ke("酉", "卯"), True, "金克木")
    assert_eq(check_ke("卯", "丑"), True, "木克土")
    assert_eq(check_ke("丑", "亥"), True, "土克水")
    assert_eq(check_ke("午", "寅"), False, "火不克木(被生)")
    assert_eq(check_ke("寅", "午"), False, "木不克火(生火)")
    assert_eq(check_ke("子", "寅"), False, "水不克木(生木)")
    assert_eq(check_ke("巳", "申"), True, "火克金")
    assert_eq(check_ke("申", "子"), False, "金不克水(生水)")
    assert_eq(check_ke("辰", "戌"), False, "土不克土(同五行)")

    # --- check_he (≥10) ---
    assert_eq(check_he("子", "丑"), True, "子丑合")
    assert_eq(check_he("丑", "子"), True, "丑子合(无顺序)")
    assert_eq(check_he("寅", "亥"), True, "寅亥合")
    assert_eq(check_he("卯", "戌"), True, "卯戌合")
    assert_eq(check_he("辰", "酉"), True, "辰酉合")
    assert_eq(check_he("巳", "申"), True, "巳申合")
    assert_eq(check_he("午", "未"), True, "午未合")
    assert_eq(check_he("子", "寅"), False, "子寅不合")
    assert_eq(check_he("子", "子"), False, "相同地支")
    assert_eq(check_he("丑", "卯"), False, "丑卯不合")

    # --- check_chong (≥10) ---
    assert_eq(check_chong("子", "午"), True, "子午冲")
    assert_eq(check_chong("午", "子"), True, "午子冲(无顺序)")
    assert_eq(check_chong("丑", "未"), True, "丑未冲")
    assert_eq(check_chong("寅", "申"), True, "寅申冲")
    assert_eq(check_chong("卯", "酉"), True, "卯酉冲")
    assert_eq(check_chong("辰", "戌"), True, "辰戌冲")
    assert_eq(check_chong("巳", "亥"), True, "巳亥冲")
    assert_eq(check_chong("子", "寅"), False, "子寅不冲")
    assert_eq(check_chong("子", "子"), False, "相同地支")
    assert_eq(check_chong("丑", "辰"), False, "丑辰不冲")

    # --- check_banhe (≥10) ---
    assert_eq(check_banhe("申", "子"), True, "申子半合")
    assert_eq(check_banhe("子", "申"), True, "子申半合(无顺序)")
    assert_eq(check_banhe("子", "辰"), True, "子辰半合")
    assert_eq(check_banhe("亥", "卯"), True, "亥卯半合")
    assert_eq(check_banhe("卯", "未"), True, "卯未半合")
    assert_eq(check_banhe("寅", "午"), True, "寅午半合")
    assert_eq(check_banhe("午", "戌"), True, "午戌半合")
    assert_eq(check_banhe("巳", "酉"), True, "巳酉半合")
    assert_eq(check_banhe("酉", "丑"), True, "酉丑半合")
    assert_eq(check_banhe("子", "丑"), False, "子丑不是半合(是六合)")
    assert_eq(check_banhe("申", "寅"), False, "申寅不是半合(是冲)")

    # --- check_sanhe (≥10) ---
    assert_eq(check_sanhe("申", "子", "辰"), "水", "申子辰→水")
    assert_eq(check_sanhe("辰", "申", "子"), "水", "无顺序")
    assert_eq(check_sanhe("亥", "卯", "未"), "木", "亥卯未→木")
    assert_eq(check_sanhe("寅", "午", "戌"), "火", "寅午戌→火")
    assert_eq(check_sanhe("巳", "酉", "丑"), "金", "巳酉丑→金")
    assert_eq(check_sanhe("子", "丑", "寅"), "", "不成局")
    assert_eq(check_sanhe("申", "子", "丑"), "", "仅两个匹配")
    assert_eq(check_sanhe("子", "子", "辰"), "", "重复地支")
    assert_eq(check_sanhe("申", "申", "申"), "", "全部相同")
    assert_eq(check_sanhe("卯", "午", "酉"), "", "随机三地支")

    # --- check_shengwang (≥10) ---
    assert_eq(check_shengwang("寅", "亥", "长生"), True, "木长生在亥")
    assert_eq(check_shengwang("寅", "卯", "帝旺"), True, "木帝旺在卯")
    assert_eq(check_shengwang("寅", "未", "墓"), True, "木墓在未")
    assert_eq(check_shengwang("寅", "申", "绝"), True, "木绝在申")
    assert_eq(check_shengwang("午", "寅", "长生"), True, "火长生在寅")
    assert_eq(check_shengwang("辰", "申", "长生"), True, "土长生在申(同水)")
    assert_eq(check_shengwang("子", "申", "长生"), True, "水长生在申")
    assert_eq(check_shengwang("酉", "寅", "绝"), True, "金绝在寅")
    assert_eq(check_shengwang("寅", "子", "长生"), False, "木长生不在子")
    assert_eq(check_shengwang("申", "亥", "长生"), False, "金长生不在亥")
    assert_eq(check_shengwang("子", "辰", "墓"), True, "水墓在辰")

    # --- check_bagong_relation (≥10) ---
    assert_eq(check_bagong_relation("111111", "011111"), "一世", "乾→姤 一世")
    assert_eq(check_bagong_relation("111111", "001111"), "二世", "乾→遁 二世")
    assert_eq(check_bagong_relation("111111", "000111"), "三世", "乾→否 三世")
    assert_eq(check_bagong_relation("111111", "000011"), "四世", "乾→观 四世")
    assert_eq(check_bagong_relation("111111", "000001"), "五世", "乾→剥 五世")
    assert_eq(check_bagong_relation("111111", "000101"), "游魂", "乾→晋 游魂")
    assert_eq(check_bagong_relation("111111", "111101"), "归魂", "乾→大有 归魂")
    assert_eq(check_bagong_relation("111111", "111111"), "", "相同卦")
    assert_eq(check_bagong_relation("000000", "100000"), "一世", "坤→复 一世")
    assert_eq(check_bagong_relation("101111", "101101"), "归魂", "天火同人→归魂步")

    return failures


if __name__ == "__main__":
    errs = _run_tests()
    if errs:
        for e in errs:
            print(f"FAIL: {e}")
        print(f"\n{len(errs)} tests failed")
    else:
        print("All tests passed!")
