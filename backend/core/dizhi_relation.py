"""B9 地支关系判断：7 个函数的 Python 正式版。

MySQL 存储函数的算法基准，逻辑确认后移植为 SQL。
"""
from backend.core.enums import DIZHI_WUXING

# ── 常量 ──────────────────────────────────────────────

_SHENG = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
_KE = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}

_HE = frozenset({
    frozenset({"子", "丑"}), frozenset({"寅", "亥"}), frozenset({"卯", "戌"}),
    frozenset({"辰", "酉"}), frozenset({"巳", "申"}), frozenset({"午", "未"}),
})
_CHONG = frozenset({
    frozenset({"子", "午"}), frozenset({"丑", "未"}), frozenset({"寅", "申"}),
    frozenset({"卯", "酉"}), frozenset({"辰", "戌"}), frozenset({"巳", "亥"}),
})
_BANHE = frozenset({
    frozenset({"申", "子"}), frozenset({"子", "辰"}),
    frozenset({"亥", "卯"}), frozenset({"卯", "未"}),
    frozenset({"寅", "午"}), frozenset({"午", "戌"}),
    frozenset({"巳", "酉"}), frozenset({"酉", "丑"}),
})
_SANHE = {
    frozenset({"申", "子", "辰"}): "水",
    frozenset({"亥", "卯", "未"}): "木",
    frozenset({"寅", "午", "戌"}): "火",
    frozenset({"巳", "酉", "丑"}): "金",
}

# 生旺墓绝：五行 → [长生, 帝旺, 墓, 绝]（土与水同宫）
_SHENGWANG: dict[str, list[str]] = {
    "木": ["亥", "卯", "未", "申"],
    "火": ["寅", "午", "戌", "亥"],
    "金": ["巳", "酉", "丑", "寅"],
    "水": ["申", "子", "辰", "巳"],
    "土": ["申", "子", "辰", "巳"],
}
_SW_INDEX = {"长生": 0, "帝旺": 1, "墓": 2, "绝": 3}


def _valid(zhi: str) -> bool:
    return zhi in DIZHI_WUXING


# ── 公开接口 ──────────────────────────────────────────

def check_sheng(a: str, b: str) -> bool:
    """A 生 B？有方向。子水生寅木 → True"""
    if not _valid(a) or not _valid(b):
        return False
    return _SHENG.get(DIZHI_WUXING[a]) == DIZHI_WUXING[b]


def check_ke(a: str, b: str) -> bool:
    """A 克 B？有方向。子水克午火 → True"""
    if not _valid(a) or not _valid(b):
        return False
    return _KE.get(DIZHI_WUXING[a]) == DIZHI_WUXING[b]


def check_he(a: str, b: str) -> bool:
    """六合？6 组，无顺序"""
    if not _valid(a) or not _valid(b) or a == b:
        return False
    return frozenset({a, b}) in _HE


def check_chong(a: str, b: str) -> bool:
    """六冲？6 组，无顺序"""
    if not _valid(a) or not _valid(b) or a == b:
        return False
    return frozenset({a, b}) in _CHONG


def check_banhe(a: str, b: str) -> bool:
    """半合？8 组，无顺序"""
    if not _valid(a) or not _valid(b) or a == b:
        return False
    return frozenset({a, b}) in _BANHE


def check_sanhe(a: str, b: str, c: str) -> str:
    """三合局？返回五行字（水/木/火/金），不形成返回 ''"""
    if not all(_valid(x) for x in (a, b, c)):
        return ""
    if a == b or b == c or a == c:
        return ""
    return _SANHE.get(frozenset({a, b, c}), "")


def check_shengwang(dizhi: str, target: str, sw_type: str) -> bool:
    """生旺墓绝判断。sw_type: '长生'/'帝旺'/'墓'/'绝'"""
    if not _valid(dizhi) or not _valid(target):
        return False
    if sw_type not in _SW_INDEX:
        return False
    wuxing = DIZHI_WUXING[dizhi]
    idx = _SW_INDEX[sw_type]
    return target == _SHENGWANG[wuxing][idx]
