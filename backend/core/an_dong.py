"""B3.5 暗动判断：日支冲本卦静爻 → 该爻标记为暗动。与动爻互斥。"""

# 六冲 6 组（无序）
_CHONG_PAIRS = frozenset({
    frozenset({"子", "午"}), frozenset({"丑", "未"}),
    frozenset({"寅", "申"}), frozenset({"卯", "酉"}),
    frozenset({"辰", "戌"}), frozenset({"巳", "亥"}),
})


def check_an_dong(ben_dizhi: str, is_dong: bool, day_zhi: str) -> bool:
    """判断本卦爻是否暗动。

    条件: is_dong=False 且 ben_dizhi 与 day_zhi 相冲。
    暗动仅适用于本卦静爻——变爻和之卦无暗动概念。
    """
    if is_dong:
        return False
    if ben_dizhi == day_zhi:
        return False
    return frozenset({ben_dizhi, day_zhi}) in _CHONG_PAIRS
