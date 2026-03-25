"""
六爻卦例分析系统 - 时间转换模块

本模块提供公历与干支时间的转换功能，使用lunar-python库实现。

主要功能：
- 公历转年柱干支
- 公历转月柱干支
- 公历转日柱干支
- 旬空计算
- 完整时间转换
- 日干日支提取
"""
from typing import Tuple, Dict, Optional
from datetime import date

try:
    from lunar_python import Solar, Lunar
    LUNAR_AVAILABLE = True
except ImportError:
    try:
        from lunar import Solar, Lunar
        LUNAR_AVAILABLE = True
    except ImportError:
        LUNAR_AVAILABLE = False
        Solar = None
        Lunar = None

from backend.core.enums import Tiangan, Dizhi


# =============================================================================
# 基础转换函数
# =============================================================================

def solar_to_ganzhi_year(year: int) -> str:
    """
    公历年份转年柱干支

    使用年中日期（7月1日）来确保获取该年主要部分的干支，
    避免因农历新年日期差异导致的问题。

    Args:
        year: 公历年份

    Returns:
        年柱干支字符串，如"甲辰"

    Example:
        >>> solar_to_ganzhi_year(2024)
        '甲辰'
        >>> solar_to_ganzhi_year(2025)
        '乙巳'
    """
    if not LUNAR_AVAILABLE:
        raise ImportError("lunar-python库未安装，请运行: pip install lunar-python")

    # 使用lunar-python进行转换
    # 使用年中日期（7月1日）获取年柱，确保在农历新年后
    solar = Solar.fromYmd(year, 7, 1)
    lunar = solar.getLunar()
    return lunar.getYearInGanZhi()


def solar_to_ganzhi_month(year: int, month: int) -> str:
    """
    公历年月转月柱干支

    Args:
        year: 公历年份
        month: 公历月份 (1-12)

    Returns:
        月柱干支字符串，如"丙寅"

    Example:
        >>> solar_to_ganzhi_month(2024, 2)
        '丙寅'
    """
    if not LUNAR_AVAILABLE:
        raise ImportError("lunar-python库未安装，请运行: pip install lunar-python")

    # 使用lunar-python进行转换
    # 选择月中日期来获取月柱
    solar = Solar.fromYmd(year, month, 15)
    lunar = solar.getLunar()
    return lunar.getMonthInGanZhi()


def solar_to_ganzhi_day(year: int, month: int, day: int) -> str:
    """
    公历年月日转日柱干支

    Args:
        year: 公历年份
        month: 公历月份 (1-12)
        day: 公历日期 (1-31)

    Returns:
        日柱干支字符串，如"甲午"

    Example:
        >>> solar_to_ganzhi_day(2024, 2, 12)
        '甲午'
    """
    if not LUNAR_AVAILABLE:
        raise ImportError("lunar-python库未安装，请运行: pip install lunar-python")

    # 使用lunar-python进行转换
    solar = Solar.fromYmd(year, month, day)
    lunar = solar.getLunar()
    return lunar.getDayInGanZhi()


def get_xunkong(year: int, month: int, day: int) -> str:
    """
    获取旬空

    旬空是指当前日柱所在的旬中，空亡的两个地支。

    Args:
        year: 公历年份
        month: 公历月份 (1-12)
        day: 公历日期 (1-31)

    Returns:
        旬空字符串，如"辰巳空"

    Example:
        >>> get_xunkong(2024, 2, 12)
        '辰巳'
    """
    if not LUNAR_AVAILABLE:
        raise ImportError("lunar-python库未安装，请运行: pip install lunar-python")

    # 使用lunar-python进行转换
    solar = Solar.fromYmd(year, month, day)
    lunar = solar.getLunar()

    # 获取值日空亡（旬空）
    # lunar-python的getDayXunKong()方法返回空亡地支
    xunkong = lunar.getDayXunKong()
    return xunkong


def solar_to_ganzhi_full(year: int, month: int, day: int) -> Dict[str, str]:
    """
    完整的公历转干支转换

    Args:
        year: 公历年份
        month: 公历月份 (1-12)
        day: 公历日期 (1-31)

    Returns:
        包含年柱、月柱、日柱、旬空的字典:
        {
            "year": "甲辰",
            "month": "丙寅",
            "day": "甲午",
            "xunkong": "辰巳"
        }

    Example:
        >>> result = solar_to_ganzhi_full(2024, 2, 12)
        >>> result["year"]
        '甲辰'
        >>> result["day"]
        '甲午'
    """
    if not LUNAR_AVAILABLE:
        raise ImportError("lunar-python库未安装，请运行: pip install lunar-python")

    # 一次性获取所有干支信息
    solar = Solar.fromYmd(year, month, day)
    lunar = solar.getLunar()

    return {
        "year": lunar.getYearInGanZhi(),
        "month": lunar.getMonthInGanZhi(),
        "day": lunar.getDayInGanZhi(),
        "xunkong": lunar.getDayXunKong()
    }


# =============================================================================
# 提取函数
# =============================================================================

def extract_tiangan_dizhi_from_ganzhi(ganzhi_str: str) -> Tuple[str, str]:
    """
    从干支字符串中提取天干和地支

    Args:
        ganzhi_str: 干支字符串，如"甲午"

    Returns:
        (天干, 地支) 元组，如("甲", "午")

    Example:
        >>> extract_tiangan_dizhi_from_ganzhi("甲午")
        ('甲', '午')
        >>> extract_tiangan_dizhi_from_ganzhi("乙巳")
        ('乙', '巳')
    """
    if not ganzhi_str or len(ganzhi_str) < 2:
        raise ValueError(f"无效的干支字符串: {ganzhi_str}")

    tiangan = ganzhi_str[0]
    dizhi = ganzhi_str[1]

    return tiangan, dizhi


def extract_tiangan_enum_from_ganzhi(ganzhi_str: str) -> Optional[Tiangan]:
    """
    从干支字符串中提取天干枚举

    Args:
        ganzhi_str: 干支字符串，如"甲午"

    Returns:
        天干枚举，如Tiangan.JIA

    Example:
        >>> extract_tiangan_enum_from_ganzhi("甲午")
        <Tiangan.JIA: '甲'>
    """
    tiangan_char, _ = extract_tiangan_dizhi_from_ganzhi(ganzhi_str)
    return Tiangan.from_char(tiangan_char)


def extract_dizhi_enum_from_ganzhi(ganzhi_str: str) -> Optional[Dizhi]:
    """
    从干支字符串中提取地支枚举

    Args:
        ganzhi_str: 干支字符串，如"甲午"

    Returns:
        地支枚举，如Dizhi.WU

    Example:
        >>> extract_dizhi_enum_from_ganzhi("甲午")
        <Dizhi.WU: '午'>
    """
    _, dizhi_char = extract_tiangan_dizhi_from_ganzhi(ganzhi_str)
    return Dizhi.from_char(dizhi_char)


# =============================================================================
# 便捷函数
# =============================================================================

def get_day_tiangan(year: int, month: int, day: int) -> Optional[Tiangan]:
    """
    获取指定日期的日干

    Args:
        year: 公历年份
        month: 公历月份
        day: 公历日期

    Returns:
        日干枚举
    """
    ganzhi_day = solar_to_ganzhi_day(year, month, day)
    return extract_tiangan_enum_from_ganzhi(ganzhi_day)


def get_day_dizhi(year: int, month: int, day: int) -> Optional[Dizhi]:
    """
    获取指定日期的日支

    Args:
        year: 公历年份
        month: 公历月份
        day: 公历日期

    Returns:
        日支枚举
    """
    ganzhi_day = solar_to_ganzhi_day(year, month, day)
    return extract_dizhi_enum_from_ganzhi(ganzhi_day)


def convert_date_to_ganzhi(solar_date: date) -> Dict[str, str]:
    """
    将datetime.date对象转换为干支

    Args:
        solar_date: 公历日期对象

    Returns:
        包含年柱、月柱、日柱、旬空的字典
    """
    return solar_to_ganzhi_full(
        solar_date.year,
        solar_date.month,
        solar_date.day
    )


# =============================================================================
# 验证函数
# =============================================================================

def validate_ganzhi(ganzhi_str: str) -> bool:
    """
    验证干支字符串是否有效

    Args:
        ganzhi_str: 干支字符串

    Returns:
        如果是有效的干支返回True，否则返回False
    """
    if not ganzhi_str or len(ganzhi_str) != 2:
        return False

    tiangan_char = ganzhi_str[0]
    dizhi_char = ganzhi_str[1]

    tiangan = Tiangan.from_char(tiangan_char)
    dizhi = Dizhi.from_char(dizhi_char)

    return tiangan is not None and dizhi is not None


def check_lunar_available() -> bool:
    """
    检查lunar-python库是否可用

    Returns:
        如果可用返回True，否则返回False
    """
    return LUNAR_AVAILABLE
