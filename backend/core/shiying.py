"""
六爻卦例分析系统 - 世应定位模块

本模块提供世应定位功能，根据宫位确定世爻和应爻的位置。

世应定位规则:
- 本宫: 世上/应三
- 一世: 世初/应四
- 二世: 世二/应五
- 三世: 世三/应上
- 四世: 世四/应初
- 五世: 世五/应二
- 游魂: 世四/应初
- 归魂: 世三/应上
"""
from typing import Tuple, Dict, Optional

from backend.core.enums import ZhongGua


# =============================================================================
# 世应映射表
# =============================================================================

# 宫位到世应爻位的映射表
# 格式: {宫位: (世爻位, 应爻位)}
# 爻位从1到6，分别对应初爻、二爻、三爻、四爻、五爻、上爻
SHI_YING_MAP: Dict[str, Tuple[int, int]] = {
    "本宫": (6, 3),  # 世在上爻，应在三爻
    "一世": (1, 4),  # 世在初爻，应在四爻
    "二世": (2, 5),  # 世在二爻，应在五爻
    "三世": (3, 6),  # 世在三爻，应在上爻
    "四世": (4, 1),  # 世在四爻，应在初爻
    "五世": (5, 2),  # 世在五爻，应在二爻
    "游魂": (4, 1),  # 世在四爻，应在初爻
    "归魂": (3, 6),  # 世在三爻，应在上爻
}


# =============================================================================
# 核心函数
# =============================================================================

def get_shiying_by_gongwei(gongwei_index: str) -> Tuple[int, int]:
    """
    根据宫位获取世爻和应爻的爻位

    Args:
        gongwei_index: 宫位 (本宫/一世/二世/三世/四世/五世/游魂/归魂)

    Returns:
        (世爻位, 应爻位) 元组，爻位从1到6
        如果找不到对应宫位，返回(0, 0)

    Example:
        >>> get_shiying_by_gongwei("本宫")
        (6, 3)
        >>> get_shiying_by_gongwei("一世")
        (1, 4)
    """
    return SHI_YING_MAP.get(gongwei_index, (0, 0))


def get_shi_position(gongwei_index: str) -> int:
    """
    根据宫位获取世爻位置

    Args:
        gongwei_index: 宫位

    Returns:
        世爻位置 (1-6)，如果找不到返回0

    Example:
        >>> get_shi_position("本宫")
        6
    """
    shi, _ = get_shiying_by_gongwei(gongwei_index)
    return shi


def get_ying_position(gongwei_index: str) -> int:
    """
    根据宫位获取应爻位置

    Args:
        gongwei_index: 宫位

    Returns:
        应爻位置 (1-6)，如果找不到返回0

    Example:
        >>> get_ying_position("本宫")
        3
    """
    _, ying = get_shiying_by_gongwei(gongwei_index)
    return ying


def validate_gongwei_index(gongwei_index: str) -> bool:
    """
    验证宫位是否有效

    Args:
        gongwei_index: 宫位

    Returns:
        如果宫位有效返回True，否则返回False
    """
    return gongwei_index in SHI_YING_MAP


# =============================================================================
# Guali类集成函数
# =============================================================================

def set_shiying_for_guali(guali) -> None:
    """
    为卦例设置世应爻

    根据卦宫的宫位设置世爻和应爻。
    此函数会直接修改guali对象的yaos列表中各爻的is_world和is_response属性。

    Args:
        guali: Guali对象

    Example:
        >>> from backend.core.models import Guali
        >>> from backend.core.enums import ZhongGua
        >>> guali = Guali(ben_gua=ZhongGua.QIAN_WEI_TIAN)
        >>> set_shiying_for_guali(guali)
        >>> guali.yaos[5].is_world
        True
    """
    if guali.ben_gua is None:
        return

    gongwei_index = guali.ben_gua.gongwei_index
    shi_pos, ying_pos = get_shiying_by_gongwei(gongwei_index)

    for yao in guali.yaos:
        yao.is_world = (yao.position == shi_pos)
        yao.is_response = (yao.position == ying_pos)


# =============================================================================
# 辅助函数
# =============================================================================

def get_shiying_info(gongwei_index: str) -> str:
    """
    获取宫位的世应信息描述

    Args:
        gongwei_index: 宫位

    Returns:
        世应信息描述字符串

    Example:
        >>> get_shiying_info("本宫")
        '世在上爻，应在三爻'
    """
    shi, ying = get_shiying_by_gongwei(gongwei_index)
    if shi == 0:
        return "未知宫位"

    position_names = {
        1: "初爻", 2: "二爻", 3: "三爻",
        4: "四爻", 5: "五爻", 6: "上爻"
    }

    return f"世在{position_names[shi]}，应在{position_names[ying]}"


def print_shiying_table():
    """
    打印世应对照表

    用于调试和验证。
    """
    print("世应对照表")
    print("=" * 40)
    print(f"{'宫位':<8} {'世爻':<8} {'应爻':<8}")
    print("-" * 40)

    for gongwei, (shi, ying) in SHI_YING_MAP.items():
        print(f"{gongwei:<8} {shi}爻{'   ':<5} {ying}爻")


if __name__ == "__main__":
    print("=== 世应定位模块测试 ===")
    print()

    # 打印世应对照表
    print_shiying_table()

    print()
    print("=== 详细测试 ===")

    # 测试所有宫位
    for gongwei in SHI_YING_MAP:
        info = get_shiying_info(gongwei)
        print(f"  {gongwei}: {info}")
