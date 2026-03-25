"""
六爻卦例分析系统 - 六神计算模块

本模块提供六神计算功能，根据日干确定各爻位的六神。

六神排列规则 (按日干):
- 甲乙日: 初青龙、二朱雀、三勾陈、四螣蛇、五白虎、上玄武
- 丙丁日: 初朱雀、二勾陈、三螣蛇、四白虎、五玄武、上青龙
- 戊日: 初勾陈、二螣蛇、三白虎、四玄武、五青龙、上朱雀
- 己日: 初螣蛇、二白虎、三玄武、四青龙、五朱雀、上勾陈
- 庚辛日: 初白虎、二玄武、三青龙、四朱雀、五勾陈、上螣蛇
- 壬癸日: 初玄武、二青龙、三朱雀、四勾陈、五螣蛇、上白虎
"""
from typing import List, Tuple, Dict, Optional

from backend.core.enums import Tiangan, LiuShen


# =============================================================================
# 六神映射表
# =============================================================================

# 六神基础顺序: 青龙、朱雀、勾陈、螣蛇、白虎、玄武
LIUSHEN_ORDER: List[LiuShen] = [
    LiuShen.QING_LONG,
    LiuShen.ZHU_QUE,
    LiuShen.GOU_CHEN,
    LiuShen.TENG_SHE,
    LiuShen.BAI_HU,
    LiuShen.XUAN_WU
]

# 日干到起始六神的映射表
# 甲乙从青龙开始，丙丁从朱雀开始，依此类推
TIANGAN_LIUSHEN_OFFSET: Dict[Tiangan, int] = {
    Tiangan.JIA: 0,   # 甲日从青龙开始
    Tiangan.YI: 0,    # 乙日从青龙开始
    Tiangan.BING: 1,  # 丙日从朱雀开始
    Tiangan.DING: 1,  # 丁日从朱雀开始
    Tiangan.WU: 2,    # 戊日从勾陈开始
    Tiangan.JI: 3,    # 己日从螣蛇开始
    Tiangan.GENG: 4,  # 庚日从白虎开始
    Tiangan.XIN: 4,   # 辛日从白虎开始
    Tiangan.REN: 5,   # 壬日从玄武开始
    Tiangan.GUI: 5,   # 癸日从玄武开始
}

# 完整的日干到六神序列的映射表
# 每个日干对应六个爻位的六神顺序
LIUSHEN_MAP: Dict[Tuple[Tiangan, ...], Tuple[LiuShen, ...]] = {
    (Tiangan.JIA, Tiangan.YI): (
        LiuShen.QING_LONG, LiuShen.ZHU_QUE, LiuShen.GOU_CHEN,
        LiuShen.TENG_SHE, LiuShen.BAI_HU, LiuShen.XUAN_WU
    ),
    (Tiangan.BING, Tiangan.DING): (
        LiuShen.ZHU_QUE, LiuShen.GOU_CHEN, LiuShen.TENG_SHE,
        LiuShen.BAI_HU, LiuShen.XUAN_WU, LiuShen.QING_LONG
    ),
    (Tiangan.WU,): (
        LiuShen.GOU_CHEN, LiuShen.TENG_SHE, LiuShen.BAI_HU,
        LiuShen.XUAN_WU, LiuShen.QING_LONG, LiuShen.ZHU_QUE
    ),
    (Tiangan.JI,): (
        LiuShen.TENG_SHE, LiuShen.BAI_HU, LiuShen.XUAN_WU,
        LiuShen.QING_LONG, LiuShen.ZHU_QUE, LiuShen.GOU_CHEN
    ),
    (Tiangan.GENG, Tiangan.XIN): (
        LiuShen.BAI_HU, LiuShen.XUAN_WU, LiuShen.QING_LONG,
        LiuShen.ZHU_QUE, LiuShen.GOU_CHEN, LiuShen.TENG_SHE
    ),
    (Tiangan.REN, Tiangan.GUI): (
        LiuShen.XUAN_WU, LiuShen.QING_LONG, LiuShen.ZHU_QUE,
        LiuShen.GOU_CHEN, LiuShen.TENG_SHE, LiuShen.BAI_HU
    ),
}


# =============================================================================
# 六神计算函数
# =============================================================================

def get_liushen_by_tiangan(tiangan: Tiangan) -> List[LiuShen]:
    """
    根据日干获取六个爻位的六神列表

    Args:
        tiangan: 日干枚举

    Returns:
        六个六神的列表，按爻位从初爻到上爻排列

    Example:
        >>> # 甲乙日：初爻青龙、二爻朱雀、三爻勾陈、四爻螣蛇、五爻白虎、上爻玄武
        >>> result = get_liushen_by_tiangan(Tiangan.JIA)
        >>> result[0] == LiuShen.QING_LONG  # 初爻青龙
        True
        >>> result[5] == LiuShen.XUAN_WU    # 上爻玄武
        True
    """
    offset = TIANGAN_LIUSHEN_OFFSET.get(tiangan, 0)
    result = []
    for i in range(6):
        index = (offset + i) % 6
        result.append(LIUSHEN_ORDER[index])
    return result


def get_liushen_by_tiangan_and_position(tiangan: Tiangan, position: int) -> LiuShen:
    """
    根据日干和爻位获取对应的六神

    Args:
        tiangan: 日干枚举
        position: 爻位 (1-6: 初爻到上爻)

    Returns:
        对应的六神

    Raises:
        ValueError: 如果爻位不在1-6范围内

    Example:
        >>> # 甲日初爻青龙
        >>> get_liushen_by_tiangan_and_position(Tiangan.JIA, 1)
        <LiuShen.QING_LONG: '青龙'>
        >>> # 甲日上爻玄武
        >>> get_liushen_by_tiangan_and_position(Tiangan.JIA, 6)
        <LiuShen.XUAN_WU: '玄武'>
        >>> # 丙日初爻朱雀
        >>> get_liushen_by_tiangan_and_position(Tiangan.BING, 1)
        <LiuShen.ZHU_QUE: '朱雀'>
    """
    if position < 1 or position > 6:
        raise ValueError(f"爻位必须在1-6之间，当前值: {position}")

    offset = TIANGAN_LIUSHEN_OFFSET.get(tiangan, 0)
    index = (offset + position - 1) % 6
    return LIUSHEN_ORDER[index]


def get_liushen_by_tiangan_char(tiangan_char: str) -> List[LiuShen]:
    """
    根据日干字符获取六个爻位的六神列表

    Args:
        tiangan_char: 日干字符（如"甲"、"乙"等）

    Returns:
        六个六神的列表，按爻位从初爻到上爻排列

    Raises:
        ValueError: 如果日干字符无效

    Example:
        >>> result = get_liushen_by_tiangan_char("甲")
        >>> result[0] == LiuShen.QING_LONG
        True
    """
    tiangan = Tiangan.from_char(tiangan_char)
    if tiangan is None:
        raise ValueError(f"无效的日干字符: {tiangan_char}")
    return get_liushen_by_tiangan(tiangan)


# =============================================================================
# 六神属性函数
# =============================================================================

def get_liushen_element(liushen: LiuShen) -> str:
    """
    获取六神对应的五行属性

    六神五行:
    - 青龙: 木
    - 朱雀: 火
    - 勾陈: 土
    - 螣蛇: 土
    - 白虎: 金
    - 玄武: 水

    Args:
        liushen: 六神枚举

    Returns:
        五行名称字符串
    """
    elements = {
        LiuShen.QING_LONG: "木",
        LiuShen.ZHU_QUE: "火",
        LiuShen.GOU_CHEN: "土",
        LiuShen.TENG_SHE: "土",
        LiuShen.BAI_HU: "金",
        LiuShen.XUAN_WU: "水",
    }
    return elements.get(liushen, "未知")


def get_liushen_meaning(liushen: LiuShen) -> str:
    """
    获取六神的基本含义

    Args:
        liushen: 六神枚举

    Returns:
        六神含义描述字符串
    """
    meanings = {
        LiuShen.QING_LONG: "喜庆、吉祥、仁慈",
        LiuShen.ZHU_QUE: "文书、口舌、是非",
        LiuShen.GOU_CHEN: "田土、迟滞、勾连",
        LiuShen.TENG_SHE: "惊恐、怪异、虚惊",
        LiuShen.BAI_HU: "凶险、血光、刚猛",
        LiuShen.XUAN_WU: "暗昧、隐私、暧昧",
    }
    return meanings.get(liushen, "未知")


def print_liushen_table():
    """
    打印六神对照表

    用于调试和验证。
    """
    print("六神对照表")
    print("=" * 70)
    print(f"{'日干':<10} {'初爻':<8} {'二爻':<8} {'三爻':<8} {'四爻':<8} {'五爻':<8} {'上爻':<8}")
    print("-" * 70)

    tiangan_groups = [
        ("甲乙", [Tiangan.JIA, Tiangan.YI]),
        ("丙丁", [Tiangan.BING, Tiangan.DING]),
        ("戊", [Tiangan.WU]),
        ("己", [Tiangan.JI]),
        ("庚辛", [Tiangan.GENG, Tiangan.XIN]),
        ("壬癸", [Tiangan.REN, Tiangan.GUI]),
    ]

    for group_name, tiangans in tiangan_groups:
        liushen_list = get_liushen_by_tiangan(tiangans[0])
        row = [group_name] + [ls.value for ls in liushen_list]
        print(f"{row[0]:<10} {row[1]:<8} {row[2]:<8} {row[3]:<8} {row[4]:<8} {row[5]:<8} {row[6]:<8}")


if __name__ == "__main__":
    print("=== 六神计算模块测试 ===\n")

    # 打印六神对照表
    print_liushen_table()

    print("\n=== 详细测试 ===")

    # 测试甲日
    print("\n甲日六神:")
    liushen_list = get_liushen_by_tiangan(Tiangan.JIA)
    for i, ls in enumerate(liushen_list, 1):
        print(f"  {i}爻: {ls.value}")

    # 测试庚日
    print("\n庚日六神:")
    liushen_list = get_liushen_by_tiangan(Tiangan.GENG)
    for i, ls in enumerate(liushen_list, 1):
        print(f"  {i}爻: {ls.value}")

    # 测试六神属性
    print("\n六神属性:")
    for ls in LiuShen:
        element = get_liushen_element(ls)
        meaning = get_liushen_meaning(ls)
        print(f"  {ls.value}: {element} - {meaning}")
