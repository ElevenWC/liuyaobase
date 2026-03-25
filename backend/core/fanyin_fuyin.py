"""
六爻卦例分析系统 - 反吟伏吟计算模块

本模块提供反吟伏吟的判断功能。

反吟伏吟规则:
1. 易冒反吟: 乾巽互变、坎离互变、艮坤互变、震兑互变
2. 爻变反吟: 坤巽互变
3. 伏吟: 乾震互变

反吟表示事情反复，伏吟表示事情停滞。
"""
from typing import Dict, List, Optional, Set, Tuple

from backend.core.enums import DanGua, ZhongGua


# =============================================================================
# 易冒反吟映射表
# =============================================================================

# 易冒反吟: 乾巽互变、坎离互变、艮坤互变、震兑互变
# 规则: 相对180度的单卦互为易冒反吟
YIMAO_FANYIN_PAIRS: Set[Tuple[DanGua, DanGua]] = {
    (DanGua.QIAN, DanGua.XUN),   # 乾巽互变
    (DanGua.XUN, DanGua.QIAN),
    (DanGua.KAN, DanGua.LI),     # 坎离互变
    (DanGua.LI, DanGua.KAN),
    (DanGua.GEN, DanGua.KUN),    # 艮坤互变
    (DanGua.KUN, DanGua.GEN),
    (DanGua.ZHEN, DanGua.DUI),   # 震兑互变
    (DanGua.DUI, DanGua.ZHEN),
}

# 易冒反吟映射字典（单向）
YIMAO_FANYIN_MAP: Dict[DanGua, DanGua] = {
    DanGua.QIAN: DanGua.XUN,
    DanGua.XUN: DanGua.QIAN,
    DanGua.KAN: DanGua.LI,
    DanGua.LI: DanGua.KAN,
    DanGua.GEN: DanGua.KUN,
    DanGua.KUN: DanGua.GEN,
    DanGua.ZHEN: DanGua.DUI,
    DanGua.DUI: DanGua.ZHEN,
}


# =============================================================================
# 爻变反吟映射表
# =============================================================================

# 爻变反吟: 坤巽互变
YAOBIAN_FANYIN_PAIRS: Set[Tuple[DanGua, DanGua]] = {
    (DanGua.KUN, DanGua.XUN),
    (DanGua.XUN, DanGua.KUN),
}

# 爻变反吟映射字典
YAOBIAN_FANYIN_MAP: Dict[DanGua, DanGua] = {
    DanGua.KUN: DanGua.XUN,
    DanGua.XUN: DanGua.KUN,
}


# =============================================================================
# 伏吟映射表
# =============================================================================

# 伏吟: 乾震互变
FUYIN_PAIRS: Set[Tuple[DanGua, DanGua]] = {
    (DanGua.QIAN, DanGua.ZHEN),
    (DanGua.ZHEN, DanGua.QIAN),
}

# 伏吟映射字典
FUYIN_MAP: Dict[DanGua, DanGua] = {
    DanGua.QIAN: DanGua.ZHEN,
    DanGua.ZHEN: DanGua.QIAN,
}


# =============================================================================
# 核心判断函数
# =============================================================================

def is_yimao_fanyin(dan_gua1: DanGua, dan_gua2: DanGua) -> bool:
    """
    判断两个单卦是否为易冒反吟关系

    Args:
        dan_gua1: 第一个单卦
        dan_gua2: 第二个单卦

    Returns:
        如果是易冒反吟关系返回True，否则返回False

    Example:
        >>> is_yimao_fanyin(DanGua.QIAN, DanGua.XUN)
        True
        >>> is_yimao_fanyin(DanGua.KAN, DanGua.LI)
        True
        >>> is_yimao_fanyin(DanGua.QIAN, DanGua.KUN)
        False
    """
    return (dan_gua1, dan_gua2) in YIMAO_FANYIN_PAIRS


def is_yaobian_fanyin(dan_gua1: DanGua, dan_gua2: DanGua) -> bool:
    """
    判断两个单卦是否为爻变反吟关系

    Args:
        dan_gua1: 第一个单卦
        dan_gua2: 第二个单卦

    Returns:
        如果是爻变反吟关系返回True，否则返回False

    Example:
        >>> is_yaobian_fanyin(DanGua.KUN, DanGua.XUN)
        True
        >>> is_yaobian_fanyin(DanGua.XUN, DanGua.KUN)
        True
        >>> is_yaobian_fanyin(DanGua.QIAN, DanGua.XUN)
        False
    """
    return (dan_gua1, dan_gua2) in YAOBIAN_FANYIN_PAIRS


def is_fuyin(dan_gua1: DanGua, dan_gua2: DanGua) -> bool:
    """
    判断两个单卦是否为伏吟关系

    Args:
        dan_gua1: 第一个单卦
        dan_gua2: 第二个单卦

    Returns:
        如果是伏吟关系返回True，否则返回False

    Example:
        >>> is_fuyin(DanGua.QIAN, DanGua.ZHEN)
        True
        >>> is_fuyin(DanGua.ZHEN, DanGua.QIAN)
        True
        >>> is_fuyin(DanGua.QIAN, DanGua.XUN)
        False
    """
    return (dan_gua1, dan_gua2) in FUYIN_PAIRS


def get_yimao_fanyin_pair(dan_gua: DanGua) -> Optional[DanGua]:
    """
    获取单卦的易冒反吟对卦

    Args:
        dan_gua: 单卦

    Returns:
        对应的易冒反吟卦，如果没有返回None
    """
    return YIMAO_FANYIN_MAP.get(dan_gua)


def get_yaobian_fanyin_pair(dan_gua: DanGua) -> Optional[DanGua]:
    """
    获取单卦的爻变反吟对卦

    Args:
        dan_gua: 单卦

    Returns:
        对应的爻变反吟卦，如果没有返回None
    """
    return YAOBIAN_FANYIN_MAP.get(dan_gua)


def get_fuyin_pair(dan_gua: DanGua) -> Optional[DanGua]:
    """
    获取单卦的伏吟对卦

    Args:
        dan_gua: 单卦

    Returns:
        对应的伏吟卦，如果没有返回None
    """
    return FUYIN_MAP.get(dan_gua)


# =============================================================================
# 卦例计算函数
# =============================================================================

def calculate_fanyin_fuyin_for_guali(guali) -> Dict:
    """
    为卦例计算反吟伏吟状态

    比较本卦和之卦的内卦、外卦，判断是否存在反吟伏吟关系。

    Args:
        guali: Guali对象

    Returns:
        反吟伏吟信息字典，格式:
        {
            "has_fanyin": bool,       # 是否有反吟
            "has_fuyin": bool,        # 是否有伏吟
            "neigua": [str, ...],     # 内卦的反吟伏吟类型列表
            "waigua": [str, ...],     # 外卦的反吟伏吟类型列表
            "details": [              # 详细信息
                {
                    "position": "内卦" / "外卦",
                    "type": "易冒反吟" / "爻变反吟" / "伏吟",
                    "from": "乾",
                    "to": "巽"
                },
                ...
            ]
        }

    Example:
        >>> guali = Guali(ben_gua=ZhongGua.HUO_TIAN_DA_YOU, zhi_gua=ZhongGua.HUO_FENG_DING)
        >>> result = calculate_fanyin_fuyin_for_guali(guali)
    """
    result = {
        "has_fanyin": False,
        "has_fuyin": False,
        "neigua": [],
        "waigua": [],
        "details": []
    }

    # 如果没有之卦，则不存在反吟伏吟
    if guali.zhi_gua is None:
        return result

    # 获取本卦和之卦的内卦、外卦
    ben_neigua = guali.ben_gua.neigua
    ben_waigua = guali.ben_gua.waigua
    zhi_neigua = guali.zhi_gua.neigua
    zhi_waigua = guali.zhi_gua.waigua

    # 检查内卦
    if ben_neigua != zhi_neigua:
        if is_yimao_fanyin(ben_neigua, zhi_neigua):
            result["has_fanyin"] = True
            result["neigua"].append("易冒反吟")
            result["details"].append({
                "position": "内卦",
                "type": "易冒反吟",
                "from": ben_neigua.gua_name,
                "to": zhi_neigua.gua_name
            })
        elif is_yaobian_fanyin(ben_neigua, zhi_neigua):
            result["has_fanyin"] = True
            result["neigua"].append("爻变反吟")
            result["details"].append({
                "position": "内卦",
                "type": "爻变反吟",
                "from": ben_neigua.gua_name,
                "to": zhi_neigua.gua_name
            })
        elif is_fuyin(ben_neigua, zhi_neigua):
            result["has_fuyin"] = True
            result["neigua"].append("伏吟")
            result["details"].append({
                "position": "内卦",
                "type": "伏吟",
                "from": ben_neigua.gua_name,
                "to": zhi_neigua.gua_name
            })

    # 检查外卦
    if ben_waigua != zhi_waigua:
        if is_yimao_fanyin(ben_waigua, zhi_waigua):
            result["has_fanyin"] = True
            result["waigua"].append("易冒反吟")
            result["details"].append({
                "position": "外卦",
                "type": "易冒反吟",
                "from": ben_waigua.gua_name,
                "to": zhi_waigua.gua_name
            })
        elif is_yaobian_fanyin(ben_waigua, zhi_waigua):
            result["has_fanyin"] = True
            result["waigua"].append("爻变反吟")
            result["details"].append({
                "position": "外卦",
                "type": "爻变反吟",
                "from": ben_waigua.gua_name,
                "to": zhi_waigua.gua_name
            })
        elif is_fuyin(ben_waigua, zhi_waigua):
            result["has_fuyin"] = True
            result["waigua"].append("伏吟")
            result["details"].append({
                "position": "外卦",
                "type": "伏吟",
                "from": ben_waigua.gua_name,
                "to": zhi_waigua.gua_name
            })

    return result


# =============================================================================
# 辅助函数
# =============================================================================

def print_fanyin_fuyin_table() -> None:
    """
    打印反吟伏吟对照表（调试用）
    """
    print("反吟伏吟对照表")
    print("=" * 50)

    print("\n易冒反吟:")
    print("-" * 30)
    for gua1, gua2 in YIMAO_FANYIN_MAP.items():
        print(f"  {gua1.gua_name} ↔ {gua2.gua_name}")

    print("\n爻变反吟:")
    print("-" * 30)
    for gua1, gua2 in YAOBIAN_FANYIN_MAP.items():
        print(f"  {gua1.gua_name} ↔ {gua2.gua_name}")

    print("\n伏吟:")
    print("-" * 30)
    for gua1, gua2 in FUYIN_MAP.items():
        print(f"  {gua1.gua_name} ↔ {gua2.gua_name}")


if __name__ == "__main__":
    print("=== 反吟伏吟计算模块测试 ===")
    print()
    print_fanyin_fuyin_table()

    print("\n=== 功能测试 ===")

    # 测试易冒反吟
    print(f"\n乾巽易冒反吟: {is_yimao_fanyin(DanGua.QIAN, DanGua.XUN)}")
    print(f"坎离易冒反吟: {is_yimao_fanyin(DanGua.KAN, DanGua.LI)}")
    print(f"乾坤易冒反吟: {is_yimao_fanyin(DanGua.QIAN, DanGua.KUN)}")

    # 测试爻变反吟
    print(f"\n坤巽爻变反吟: {is_yaobian_fanyin(DanGua.KUN, DanGua.XUN)}")
    print(f"乾巽爻变反吟: {is_yaobian_fanyin(DanGua.QIAN, DanGua.XUN)}")

    # 测试伏吟
    print(f"\n乾震伏吟: {is_fuyin(DanGua.QIAN, DanGua.ZHEN)}")
    print(f"乾巽伏吟: {is_fuyin(DanGua.QIAN, DanGua.XUN)}")
