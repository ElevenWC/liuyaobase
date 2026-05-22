"""B6 特殊卦判断：六冲/六合卦 + 反吟伏吟。

反吟伏吟判断比较本卦与之卦的内卦(前3位)/外卦(后3位)代码。
"""
from backend.core.enums import CODE_TO_GUA

# ── 六冲卦 10 个 ─────────────────────────────────────
_LIU_CHONG = frozenset({
    "111111",  # 乾为天
    "110110",  # 兑为泽
    "101101",  # 离为火
    "100100",  # 震为雷
    "011011",  # 巽为风
    "010010",  # 坎为水
    "001001",  # 艮为山
    "000000",  # 坤为地
    "100111",  # 雷天大壮
    "111100",  # 天雷无妄
})

# ── 六合卦 8 个 ───────────────────────────────────────
_LIU_HE = frozenset({
    "111000",  # 天地否
    "010100",  # 水雷屯
    "101001",  # 火山旅
    "110101",  # 泽火革
    "000111",  # 地天泰
    "100010",  # 雷水解
    "001101",  # 山火贲
    "011110",  # 风泽中孚
})

# ── 反吟伏吟互变规则 ──────────────────────────────────
# 易冒反吟: 两单卦互变（4对）
_FAN_YIN_YIMAO = frozenset({
    frozenset({"111", "011"}),  # 乾↔巽
    frozenset({"010", "101"}),  # 坎↔离
    frozenset({"001", "000"}),  # 艮↔坤
    frozenset({"100", "110"}),  # 震↔兑
})
# 爻变反吟: 坤巽互变
_FAN_YIN_YAOBIAN = frozenset({frozenset({"000", "011"})})
# 伏吟: 乾震互变
_FU_YIN = frozenset({frozenset({"111", "100"})})


def check_liu_chong(code: str) -> bool:
    """查表判断是否六冲卦"""
    return code in _LIU_CHONG


def check_liu_he(code: str) -> bool:
    """查表判断是否六合卦"""
    return code in _LIU_HE


def get_special_type(code: str) -> str:
    """返回卦的特殊类型"""
    if code in _LIU_CHONG:
        return "六冲"
    if code in _LIU_HE:
        return "六合"
    return "普通"


def check_fan_yin_yimao(ben_code: str, zhi_code: str) -> str:
    """易冒反吟 → '无'/'内卦'/'外卦'

    比较本/之内外卦，判断是否符合乾巽/坎离/
    艮坤/震兑互变规则。
    """
    return _check_fan_yin(ben_code, zhi_code, _FAN_YIN_YIMAO)


def check_fan_yin_yaobian(ben_code: str, zhi_code: str) -> str:
    """爻变反吟 → '无'/'内卦'/'外卦'

    坤巽互变。
    """
    return _check_fan_yin(ben_code, zhi_code, _FAN_YIN_YAOBIAN)


def check_fu_yin(ben_code: str, zhi_code: str) -> str:
    """伏吟 → '无'/'内卦'/'外卦'

    乾震互变。
    """
    return _check_fan_yin(ben_code, zhi_code, _FU_YIN)


def _check_fan_yin(ben_code: str, zhi_code: str, rule_set: frozenset) -> str:
    """通用反吟/伏吟判断。

    分别比较内卦(前3位)和外卦(后3位)，返回匹配的部位名。
    内卦和外卦同时匹配 → 返回'外卦'（优先外卦）
    """
    ben_inner, ben_outer = ben_code[:3], ben_code[3:]
    zhi_inner, zhi_outer = zhi_code[:3], zhi_code[3:]

    inner_match = frozenset({ben_inner, zhi_inner}) in rule_set
    outer_match = frozenset({ben_outer, zhi_outer}) in rule_set

    if outer_match:
        return "外卦"
    if inner_match:
        return "内卦"
    return "无"
