"""
六爻卦例分析系统 - 神煞计算模块

本模块提供神煞的计算功能，包括干禄、驿马、羊刃、桃花。

神煞规则:
- 干禄(按日干): 甲→寅、乙→卯、丙戊→巳、丁己→午、庚→申、辛→酉、壬→亥、癸→子
- 驿马(按日支): 申子辰→寅、亥卯未→巳、寅午戌→申、巳酉丑→亥
- 羊刃(按日干): 甲→卯、乙→寅、丙戊→午、丁己→巳、庚→酉、辛→申、壬→子、癸→亥
- 桃花(按日支): 申子辰→酉、亥卯未→子、寅午戌→卯、巳酉丑→午

神煞传播: 若地支A是神煞，则与A相冲、相合的地支也"带神煞"
"""
from typing import Dict, List, Optional, Set

from backend.core.enums import Tiangan, Dizhi, ShenSha


# =============================================================================
# 神煞映射表（从enums.py导入以保持一致性）
# =============================================================================

# 干禄映射表 (按日干)
GANLU_MAP: Dict[Tiangan, Dizhi] = {
    Tiangan.JIA: Dizhi.YIN,     # 甲禄在寅
    Tiangan.YI: Dizhi.MAO,      # 乙禄在卯
    Tiangan.BING: Dizhi.SI,     # 丙禄在巳
    Tiangan.DING: Dizhi.WU,     # 丁禄在午
    Tiangan.WU: Dizhi.SI,       # 戊禄在巳
    Tiangan.JI: Dizhi.WU,       # 己禄在午
    Tiangan.GENG: Dizhi.SHEN,   # 庚禄在申
    Tiangan.XIN: Dizhi.YOU,     # 辛禄在酉
    Tiangan.REN: Dizhi.HAI,     # 壬禄在亥
    Tiangan.GUI: Dizhi.ZI,      # 癸禄在子
}


# 驿马映射表 (按日支)
YIMA_MAP: Dict[Dizhi, Dizhi] = {
    Dizhi.SHEN: Dizhi.YIN,      # 申子辰日，驿马在寅
    Dizhi.ZI: Dizhi.YIN,
    Dizhi.CHEN: Dizhi.YIN,
    Dizhi.HAI: Dizhi.SI,        # 亥卯未日，驿马在巳
    Dizhi.MAO: Dizhi.SI,
    Dizhi.WEI: Dizhi.SI,
    Dizhi.YIN: Dizhi.SHEN,      # 寅午戌日，驿马在申
    Dizhi.WU: Dizhi.SHEN,
    Dizhi.XU: Dizhi.SHEN,
    Dizhi.SI: Dizhi.HAI,        # 巳酉丑日，驿马在亥
    Dizhi.YOU: Dizhi.HAI,
    Dizhi.CHOU: Dizhi.HAI,
}


# 羊刃映射表 (按日干)
YANGREN_MAP: Dict[Tiangan, Dizhi] = {
    Tiangan.JIA: Dizhi.MAO,     # 甲羊刃在卯
    Tiangan.YI: Dizhi.YIN,      # 乙羊刃在寅
    Tiangan.BING: Dizhi.WU,     # 丙羊刃在午
    Tiangan.DING: Dizhi.SI,     # 丁羊刃在巳
    Tiangan.WU: Dizhi.WU,       # 戊羊刃在午
    Tiangan.JI: Dizhi.SI,       # 己羊刃在巳
    Tiangan.GENG: Dizhi.YOU,    # 庚羊刃在酉
    Tiangan.XIN: Dizhi.SHEN,    # 辛羊刃在申
    Tiangan.REN: Dizhi.ZI,      # 壬羊刃在子
    Tiangan.GUI: Dizhi.HAI,     # 癸羊刃在亥
}


# 桃花映射表 (按日支)
TAOHUA_MAP: Dict[Dizhi, Dizhi] = {
    Dizhi.SHEN: Dizhi.YOU,      # 申子辰日，桃花在酉
    Dizhi.ZI: Dizhi.YOU,
    Dizhi.CHEN: Dizhi.YOU,
    Dizhi.HAI: Dizhi.ZI,        # 亥卯未日，桃花在子
    Dizhi.MAO: Dizhi.ZI,
    Dizhi.WEI: Dizhi.ZI,
    Dizhi.YIN: Dizhi.MAO,       # 寅午戌日，桃花在卯
    Dizhi.WU: Dizhi.MAO,
    Dizhi.XU: Dizhi.MAO,
    Dizhi.SI: Dizhi.WU,         # 巳酉丑日，桃花在午
    Dizhi.YOU: Dizhi.WU,
    Dizhi.CHOU: Dizhi.WU,
}


# =============================================================================
# 核心获取函数
# =============================================================================

def get_ganlu(tiangan: Tiangan) -> Dizhi:
    """
    获取干禄地支

    Args:
        tiangan: 日干

    Returns:
        干禄对应的地支

    Example:
        >>> get_ganlu(Tiangan.JIA)
        <Dizhi.YIN: '寅'>
        >>> get_ganlu(Tiangan.BING)
        <Dizhi.SI: '巳'>
    """
    return GANLU_MAP[tiangan]


def get_yima(dizhi: Dizhi) -> Dizhi:
    """
    获取驿马地支

    Args:
        dizhi: 日支

    Returns:
        驿马对应的地支

    Example:
        >>> get_yima(Dizhi.ZI)
        <Dizhi.YIN: '寅'>
        >>> get_yima(Dizhi.HAI)
        <Dizhi.SI: '巳'>
    """
    return YIMA_MAP[dizhi]


def get_yangren(tiangan: Tiangan) -> Dizhi:
    """
    获取羊刃地支

    Args:
        tiangan: 日干

    Returns:
        羊刃对应的地支

    Example:
        >>> get_yangren(Tiangan.JIA)
        <Dizhi.MAO: '卯'>
        >>> get_yangren(Tiangan.BING)
        <Dizhi.WU: '午'>
    """
    return YANGREN_MAP[tiangan]


def get_taohua(dizhi: Dizhi) -> Dizhi:
    """
    获取桃花地支

    Args:
        dizhi: 日支

    Returns:
        桃花对应的地支

    Example:
        >>> get_taohua(Dizhi.ZI)
        <Dizhi.YOU: '酉'>
        >>> get_taohua(Dizhi.HAI)
        <Dizhi.ZI: '子'>
    """
    return TAOHUA_MAP[dizhi]


# =============================================================================
# 神煞传播函数
# =============================================================================

def get_shensha_with_chonghe(shensha_dizhi: Dizhi) -> List[Dizhi]:
    """
    获取带神煞的地支列表（包含相冲、相合的地支）

    神煞传播规则: 若地支A是神煞，则与A相冲、相合的地支也"带神煞"

    Args:
        shensha_dizhi: 神煞地支

    Returns:
        包含神煞地支及其相冲、相合地支的列表

    Example:
        >>> result = get_shensha_with_chonghe(Dizhi.ZI)
        >>> Dizhi.ZI in result  # 子本身
        True
        >>> Dizhi.CHOU in result  # 子丑合
        True
        >>> Dizhi.WU in result  # 子午冲
        True
    """
    result = [shensha_dizhi]

    # 获取相合的地支
    he_dizhi = shensha_dizhi.get_he()
    if he_dizhi:
        result.append(he_dizhi)

    # 获取相冲的地支
    chong_dizhi = shensha_dizhi.get_chong()
    if chong_dizhi:
        result.append(chong_dizhi)

    return result


# =============================================================================
# 综合神煞计算函数
# =============================================================================

def calculate_all_shensha(tiangan: Tiangan, dizhi: Dizhi) -> Dict[ShenSha, List[Dizhi]]:
    """
    计算所有神煞及其传播地支

    Args:
        tiangan: 日干
        dizhi: 日支

    Returns:
        神煞字典，格式:
        {
            ShenSha.GAN_LU: [干禄地支, 相合地支, 相冲地支],
            ShenSha.YI_MA: [驿马地支, 相合地支, 相冲地支],
            ShenSha.YANG_REN: [羊刃地支, 相合地支, 相冲地支],
            ShenSha.TAO_HUA: [桃花地支, 相合地支, 相冲地支],
        }

    Example:
        >>> result = calculate_all_shensha(Tiangan.JIA, Dizhi.WU)
        >>> result[ShenSha.GAN_LU]  # 甲禄在寅
        [<Dizhi.YIN: '寅'>, <Dizhi.HAI: '亥'>, <Dizhi.SHEN: '申'>]
    """
    result = {}

    # 计算干禄及其传播
    ganlu = get_ganlu(tiangan)
    result[ShenSha.GAN_LU] = get_shensha_with_chonghe(ganlu)

    # 计算驿马及其传播
    yima = get_yima(dizhi)
    result[ShenSha.YI_MA] = get_shensha_with_chonghe(yima)

    # 计算羊刃及其传播
    yangren = get_yangren(tiangan)
    result[ShenSha.YANG_REN] = get_shensha_with_chonghe(yangren)

    # 计算桃花及其传播
    taohua = get_taohua(dizhi)
    result[ShenSha.TAO_HUA] = get_shensha_with_chonghe(taohua)

    return result


def get_shensha_type_for_dizhi(dizhi: Dizhi, tiangan: Tiangan, day_dizhi: Dizhi) -> Dict[ShenSha, str]:
    """
    判断某地支的神煞类型（是本神煞还是带神煞）

    Args:
        dizhi: 要判断的地支
        tiangan: 日干
        day_dizhi: 日支

    Returns:
        神煞类型字典，格式:
        {
            ShenSha.GAN_LU: "是干禄" / "带干禄" / None,
            ShenSha.YI_MA: "是驿马" / "带驿马" / None,
            ...
        }

    Example:
        >>> result = get_shensha_type_for_dizhi(Dizhi.YIN, Tiangan.JIA, Dizhi.WU)
        >>> result[ShenSha.GAN_LU]
        '是干禄'
    """
    result = {}

    # 干禄判断
    ganlu = get_ganlu(tiangan)
    if dizhi == ganlu:
        result[ShenSha.GAN_LU] = "是干禄"
    elif dizhi in get_shensha_with_chonghe(ganlu):
        result[ShenSha.GAN_LU] = "带干禄"
    else:
        result[ShenSha.GAN_LU] = None

    # 驿马判断
    yima = get_yima(day_dizhi)
    if dizhi == yima:
        result[ShenSha.YI_MA] = "是驿马"
    elif dizhi in get_shensha_with_chonghe(yima):
        result[ShenSha.YI_MA] = "带驿马"
    else:
        result[ShenSha.YI_MA] = None

    # 羊刃判断
    yangren = get_yangren(tiangan)
    if dizhi == yangren:
        result[ShenSha.YANG_REN] = "是羊刃"
    elif dizhi in get_shensha_with_chonghe(yangren):
        result[ShenSha.YANG_REN] = "带羊刃"
    else:
        result[ShenSha.YANG_REN] = None

    # 桃花判断
    taohua = get_taohua(day_dizhi)
    if dizhi == taohua:
        result[ShenSha.TAO_HUA] = "是桃花"
    elif dizhi in get_shensha_with_chonghe(taohua):
        result[ShenSha.TAO_HUA] = "带桃花"
    else:
        result[ShenSha.TAO_HUA] = None

    return result


# =============================================================================
# 卦例神煞计算函数
# =============================================================================

def calculate_shensha_for_guali(guali) -> Dict:
    """
    为卦例计算神煞

    Args:
        guali: Guali对象

    Returns:
        神煞信息字典，格式:
        {
            "ganlu": {
                "dizhi": "寅",
                "is_in_gua": True/False,  # 干禄地支是否在卦中
                "yaos": [1, 3],           # 带干禄的爻位列表
            },
            "yima": {...},
            "yangren": {...},
            "taohua": {...},
        }

    Example:
        >>> guali = Guali(ben_gua=ZhongGua.QIAN_WEI_TIAN, ganzhi_day="甲午")
        >>> guali.calculate_all()
        >>> shensha = calculate_shensha_for_guali(guali)
    """
    result = {}

    # 如果没有日干日支，返回空结果
    if guali.day_tiangan is None or guali.day_dizhi is None:
        return {
            "ganlu": {"dizhi": None, "is_in_gua": False, "yaos": []},
            "yima": {"dizhi": None, "is_in_gua": False, "yaos": []},
            "yangren": {"dizhi": None, "is_in_gua": False, "yaos": []},
            "taohua": {"dizhi": None, "is_in_gua": False, "yaos": []},
        }

    tiangan = guali.day_tiangan
    day_dizhi = guali.day_dizhi

    # 获取所有神煞及其传播地支
    all_shensha = calculate_all_shensha(tiangan, day_dizhi)

    # 计算干禄
    ganlu_list = all_shensha[ShenSha.GAN_LU]
    ganlu_dizhi = get_ganlu(tiangan)
    ganlu_yaos = []
    for yao in guali.yaos:
        if yao.dizhi in ganlu_list:
            ganlu_yaos.append({
                "position": yao.position,
                "dizhi": yao.dizhi.value if yao.dizhi else None,
                "type": "是干禄" if yao.dizhi == ganlu_dizhi else "带干禄"
            })
    result["ganlu"] = {
        "dizhi": ganlu_dizhi.value,
        "is_in_gua": len(ganlu_yaos) > 0,
        "yaos": ganlu_yaos
    }

    # 计算驿马
    yima_list = all_shensha[ShenSha.YI_MA]
    yima_dizhi = get_yima(day_dizhi)
    yima_yaos = []
    for yao in guali.yaos:
        if yao.dizhi in yima_list:
            yima_yaos.append({
                "position": yao.position,
                "dizhi": yao.dizhi.value if yao.dizhi else None,
                "type": "是驿马" if yao.dizhi == yima_dizhi else "带驿马"
            })
    result["yima"] = {
        "dizhi": yima_dizhi.value,
        "is_in_gua": len(yima_yaos) > 0,
        "yaos": yima_yaos
    }

    # 计算羊刃
    yangren_list = all_shensha[ShenSha.YANG_REN]
    yangren_dizhi = get_yangren(tiangan)
    yangren_yaos = []
    for yao in guali.yaos:
        if yao.dizhi in yangren_list:
            yangren_yaos.append({
                "position": yao.position,
                "dizhi": yao.dizhi.value if yao.dizhi else None,
                "type": "是羊刃" if yao.dizhi == yangren_dizhi else "带羊刃"
            })
    result["yangren"] = {
        "dizhi": yangren_dizhi.value,
        "is_in_gua": len(yangren_yaos) > 0,
        "yaos": yangren_yaos
    }

    # 计算桃花
    taohua_list = all_shensha[ShenSha.TAO_HUA]
    taohua_dizhi = get_taohua(day_dizhi)
    taohua_yaos = []
    for yao in guali.yaos:
        if yao.dizhi in taohua_list:
            taohua_yaos.append({
                "position": yao.position,
                "dizhi": yao.dizhi.value if yao.dizhi else None,
                "type": "是桃花" if yao.dizhi == taohua_dizhi else "带桃花"
            })
    result["taohua"] = {
        "dizhi": taohua_dizhi.value,
        "is_in_gua": len(taohua_yaos) > 0,
        "yaos": taohua_yaos
    }

    return result


# =============================================================================
# 辅助函数
# =============================================================================

def print_shensha_table() -> None:
    """
    打印神煞对照表（调试用）
    """
    print("神煞对照表")
    print("=" * 50)

    print("\n干禄（按日干）:")
    print("-" * 30)
    for tiangan, dizhi in GANLU_MAP.items():
        print(f"  {tiangan.value}日 → {dizhi.value}")

    print("\n驿马（按日支）:")
    print("-" * 30)
    print("  申子辰日 → 寅")
    print("  亥卯未日 → 巳")
    print("  寅午戌日 → 申")
    print("  巳酉丑日 → 亥")

    print("\n羊刃（按日干）:")
    print("-" * 30)
    for tiangan, dizhi in YANGREN_MAP.items():
        print(f"  {tiangan.value}日 → {dizhi.value}")

    print("\n桃花（按日支）:")
    print("-" * 30)
    print("  申子辰日 → 酉")
    print("  亥卯未日 → 子")
    print("  寅午戌日 → 卯")
    print("  巳酉丑日 → 午")


if __name__ == "__main__":
    print("=== 神煞计算模块测试 ===")
    print()
    print_shensha_table()

    print("\n=== 功能测试 ===")

    # 测试干禄
    print(f"\n甲日干禄: {get_ganlu(Tiangan.JIA).value}")
    print(f"丙日干禄: {get_ganlu(Tiangan.BING).value}")
    print(f"戊日干禄: {get_ganlu(Tiangan.WU).value}")

    # 测试驿马
    print(f"\n子日驿马: {get_yima(Dizhi.ZI).value}")
    print(f"亥日驿马: {get_yima(Dizhi.HAI).value}")

    # 测试羊刃
    print(f"\n甲日羊刃: {get_yangren(Tiangan.JIA).value}")
    print(f"乙日羊刃: {get_yangren(Tiangan.YI).value}")

    # 测试桃花
    print(f"\n子日桃花: {get_taohua(Dizhi.ZI).value}")
    print(f"亥日桃花: {get_taohua(Dizhi.HAI).value}")

    # 测试神煞传播
    print(f"\n子作为神煞时的传播: {[d.value for d in get_shensha_with_chonghe(Dizhi.ZI)]}")
