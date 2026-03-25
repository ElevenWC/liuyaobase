"""
六爻卦例分析系统 - 五行生克辅助模块

本模块提供五行生克判断的辅助函数，用于六亲计算。

六亲计算规则：
- 爻地支五行生卦宫五行 → 父母
- 爻地支五行克卦宫五行 → 官鬼
- 卦宫五行生爻地支五行 → 子孙
- 卦宫五行克爻地支五行 → 妻财
- 卦宫五行 = 爻地支五行 → 兄弟
"""
from typing import Optional

from backend.core.enums import Wuxing, LiuQin


# =============================================================================
# 五行生克判断辅助函数
# =============================================================================

def wuxing_sheng(a: Wuxing, b: Wuxing) -> bool:
    """
    判断五行a是否生五行b

    相生关系: 金生水 → 水生木 → 木生火 → 火生土 → 土生金

    Args:
        a: 五行a
        b: 五行b

    Returns:
        如果a生b返回True，否则返回False

    Example:
        >>> wuxing_sheng(Wuxing.JIN, Wuxing.SHUI)
        True  # 金生水
        >>> wuxing_sheng(Wuxing.SHUI, Wuxing.JIN)
        False  # 水不生金
    """
    return a.generates(b)


def wuxing_ke(a: Wuxing, b: Wuxing) -> bool:
    """
    判断五行a是否克五行b

    相克关系: 金克木 → 木克土 → 土克水 → 水克火 → 火克金

    Args:
        a: 五行a
        b: 五行b

    Returns:
        如果a克b返回True，否则返回False

    Example:
        >>> wuxing_ke(Wuxing.JIN, Wuxing.MU)
        True  # 金克木
        >>> wuxing_ke(Wuxing.MU, Wuxing.JIN)
        False  # 木不克金
    """
    return a.overcomes(b)


def wuxing_sheng_by(a: Wuxing, b: Wuxing) -> bool:
    """
    判断五行a是否被五行b所生

    即判断b是否生a

    Args:
        a: 五行a
        b: 五行b

    Returns:
        如果b生a返回True，否则返回False
    """
    return b.generates(a)


def wuxing_ke_by(a: Wuxing, b: Wuxing) -> bool:
    """
    判断五行a是否被五行b所克

    即判断b是否克a

    Args:
        a: 五行a
        b: 五行b

    Returns:
        如果b克a返回True，否则返回False
    """
    return b.overcomes(a)


# =============================================================================
# 六亲计算函数
# =============================================================================

def calculate_liuqin(gongwuxing: Wuxing, yaowuxing: Wuxing) -> LiuQin:
    """
    根据卦宫五行和爻地支五行计算六亲

    六亲计算规则:
    - 卦宫五行 = 爻地支五行 → 兄弟
    - 卦宫五行生爻地支五行 → 子孙
    - 卦宫五行克爻地支五行 → 妻财
    - 爻地支五行生卦宫五行 → 父母
    - 爻地支五行克卦宫五行 → 官鬼

    Args:
        gongwuxing: 卦宫五行
        yaowuxing: 爻地支五行

    Returns:
        对应的六亲

    Example:
        >>> # 爻地支五行生卦宫五行：父母
        >>> calculate_liuqin(Wuxing.JIN, Wuxing.SHUI)
        <LiuQin.FU_MU: '父母'>  # 水生金（爻生卦宫）
        >>> # 爻地支五行克卦宫五行：官鬼
        >>> calculate_liuqin(Wuxing.SHUI, Wuxing.HUO)
        <LiuQin.GUAN_GUI: '官鬼'>  # 火克水（爻克卦宫）
        >>> # 卦宫五行生爻地支五行：子孙
        >>> calculate_liuqin(Wuxing.SHUI, Wuxing.MU)
        <LiuQin.ZI_SUN: '子孙'>  # 水生木（卦宫生爻）
        >>> # 卦宫五行克爻地支五行：妻财
        >>> calculate_liuqin(Wuxing.MU, Wuxing.TU)
        <LiuQin.QI_CAI: '妻财'>  # 木克土（卦宫克爻）
        >>> # 卦宫五行与爻地支五行相同：兄弟
        >>> calculate_liuqin(Wuxing.MU, Wuxing.MU)
        <LiuQin.XIONG_DI: '兄弟'>
    """
    return LiuQin.calculate(gongwuxing, yaowuxing)


def get_liuqin_by_relation(gongwuxing: Wuxing, yaowuxing: Wuxing) -> str:
    """
    获取卦宫五行与爻五行的关系描述

    Args:
        gongwuxing: 卦宫五行
        yaowuxing: 爻地支五行

    Returns:
        关系描述字符串
    """
    if gongwuxing == yaowuxing:
        return "同"
    elif gongwuxing.generates(yaowuxing):
        return "生"
    elif gongwuxing.overcomes(yaowuxing):
        return "克"
    elif yaowuxing.generates(gongwuxing):
        return "被生"
    elif yaowuxing.overcomes(gongwuxing):
        return "被克"
    else:
        return "未知"


# =============================================================================
# 五行关系详细分析
# =============================================================================

def analyze_wuxing_relation(a: Wuxing, b: Wuxing) -> dict:
    """
    分析两个五行之间的所有关系

    Args:
        a: 五行a
        b: 五行b

    Returns:
        包含所有关系信息的字典
    """
    result = {
        "a": a.value,
        "b": b.value,
        "a_sheng_b": a.generates(b),   # a生b
        "a_ke_b": a.overcomes(b),       # a克b
        "b_sheng_a": b.generates(a),   # b生a
        "b_ke_a": b.overcomes(a),       # b克a
        "same": a == b,                 # 相同
    }

    # 确定主要关系
    if a == b:
        result["relation"] = "同"
    elif a.generates(b):
        result["relation"] = "生"
    elif a.overcomes(b):
        result["relation"] = "克"
    elif b.generates(a):
        result["relation"] = "被生"
    elif b.overcomes(a):
        result["relation"] = "被克"
    else:
        result["relation"] = "无"

    return result


if __name__ == "__main__":
    # 测试五行生克关系
    print("=== 五行生克测试 ===")
    print(f"金生水: {wuxing_sheng(Wuxing.JIN, Wuxing.SHUI)}")  # True
    print(f"水生木: {wuxing_sheng(Wuxing.SHUI, Wuxing.MU)}")   # True
    print(f"金克木: {wuxing_ke(Wuxing.JIN, Wuxing.MU)}")       # True
    print(f"水克火: {wuxing_ke(Wuxing.SHUI, Wuxing.HUO)}")     # True

    print("\n=== 六亲计算测试 ===")
    # 乾宫属金
    gongwuxing = Wuxing.JIN

    # 测试各爻位六亲
    test_cases = [
        (Wuxing.SHUI, "子水"),   # 金生水 → 子孙
        (Wuxing.MU, "寅木"),     # 金克木 → 妻财
        (Wuxing.TU, "辰土"),     # 土生金 → 父母
        (Wuxing.HUO, "巳火"),    # 火克金 → 官鬼
        (Wuxing.JIN, "申金"),    # 金=金 → 兄弟
    ]

    for yaowuxing, desc in test_cases:
        liuqin = calculate_liuqin(gongwuxing, yaowuxing)
        print(f"{desc} ({yaowuxing.value}): {liuqin.value}")
