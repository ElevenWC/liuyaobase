"""
六爻卦例分析系统 - 生旺墓绝计算模块

本模块提供生旺墓绝的计算功能。

生旺墓绝规则:
- 寅卯(木): 长生亥、帝旺卯、墓未、绝申
- 巳午(火): 长生寅、帝旺午、墓戌、绝亥
- 申酉(金): 长生巳、帝旺酉、墓丑、绝寅
- 亥子(水): 长生申、帝旺子、墓辰、绝巳
- 丑辰未戌(土): 长生申、帝旺子、墓辰、绝巳（与水相同）

作用范围: 动爻-变爻、飞神-伏神、爻支-日支
"""
from typing import Dict, List, Optional

from backend.core.enums import Dizhi, Wuxing


# =============================================================================
# 生旺墓绝映射表
# =============================================================================

# 以地支五行为key的生旺墓绝映射
# 格式: {五行: {"长生": 地支, "帝旺": 地支, "墓": 地支, "绝": 地支}}
SHENGWANG_MUJUE_MAP: Dict[Wuxing, Dict[str, Dizhi]] = {
    Wuxing.MU: {
        "长生": Dizhi.HAI,   # 木长生在亥
        "帝旺": Dizhi.MAO,   # 木帝旺在卯
        "墓": Dizhi.WEI,     # 木墓在未
        "绝": Dizhi.SHEN,    # 木绝在申
    },
    Wuxing.HUO: {
        "长生": Dizhi.YIN,   # 火长生在寅
        "帝旺": Dizhi.WU,    # 火帝旺在午
        "墓": Dizhi.XU,      # 火墓在戌
        "绝": Dizhi.HAI,     # 火绝在亥
    },
    Wuxing.JIN: {
        "长生": Dizhi.SI,    # 金长生在巳
        "帝旺": Dizhi.YOU,   # 金帝旺在酉
        "墓": Dizhi.CHOU,    # 金墓在丑
        "绝": Dizhi.YIN,     # 金绝在寅
    },
    Wuxing.SHUI: {
        "长生": Dizhi.SHEN,  # 水长生在申
        "帝旺": Dizhi.ZI,    # 水帝旺在子
        "墓": Dizhi.CHEN,    # 水墓在辰
        "绝": Dizhi.SI,      # 水绝在巳
    },
    Wuxing.TU: {
        # 土的生旺墓绝与水相同
        "长生": Dizhi.SHEN,  # 土长生在申
        "帝旺": Dizhi.ZI,    # 土帝旺在子
        "墓": Dizhi.CHEN,    # 土墓在辰
        "绝": Dizhi.SI,      # 土绝在巳
    },
}

# 反向映射：从地支到生旺墓绝状态
# 格式: {(五行, 地支): "长生"|"帝旺"|"墓"|"绝"|None}
DIZHI_STATE_MAP: Dict[tuple, Optional[str]] = {}

for wuxing, states in SHENGWANG_MUJUE_MAP.items():
    for state_name, dizhi in states.items():
        DIZHI_STATE_MAP[(wuxing, dizhi)] = state_name


# =============================================================================
# 核心查询函数
# =============================================================================

def get_changsheng(wuxing: Wuxing) -> Dizhi:
    """
    获取某五行的长生地支

    Args:
        wuxing: 五行

    Returns:
        长生地支

    Example:
        >>> get_changsheng(Wuxing.MU)
        <Dizhi.HAI: '亥'>
        >>> get_changsheng(Wuxing.HUO)
        <Dizhi.YIN: '寅'>
    """
    return SHENGWANG_MUJUE_MAP[wuxing]["长生"]


def get_diwang(wuxing: Wuxing) -> Dizhi:
    """
    获取某五行的帝旺地支

    Args:
        wuxing: 五行

    Returns:
        帝旺地支

    Example:
        >>> get_diwang(Wuxing.MU)
        <Dizhi.MAO: '卯'>
    """
    return SHENGWANG_MUJUE_MAP[wuxing]["帝旺"]


def get_mu(wuxing: Wuxing) -> Dizhi:
    """
    获取某五行的墓地支

    Args:
        wuxing: 五行

    Returns:
        墓地支

    Example:
        >>> get_mu(Wuxing.MU)
        <Dizhi.WEI: '未'>
    """
    return SHENGWANG_MUJUE_MAP[wuxing]["墓"]


def get_jue(wuxing: Wuxing) -> Dizhi:
    """
    获取某五行的绝地支

    Args:
        wuxing: 五行

    Returns:
        绝地支

    Example:
        >>> get_jue(Wuxing.MU)
        <Dizhi.SHEN: '申'>
    """
    return SHENGWANG_MUJUE_MAP[wuxing]["绝"]


def get_all_states(wuxing: Wuxing) -> Dict[str, Dizhi]:
    """
    获取某五行的所有生旺墓绝地支

    Args:
        wuxing: 五行

    Returns:
        生旺墓绝字典 {"长生": 地支, "帝旺": 地支, "墓": 地支, "绝": 地支}

    Example:
        >>> get_all_states(Wuxing.MU)
        {'长生': <Dizhi.HAI: '亥'>, '帝旺': <Dizhi.MAO: '卯'>, '墓': <Dizhi.WEI: '未'>, '绝': <Dizhi.SHEN: '申'>}
    """
    return SHENGWANG_MUJUE_MAP[wuxing].copy()


def get_shengwang_mujue_state(yao_wuxing: Wuxing, target_dizhi: Dizhi) -> Optional[str]:
    """
    判断某地支相对于某五行的生旺墓绝状态

    Args:
        yao_wuxing: 爻的五行（或要判断的主体五行）
        target_dizhi: 目标地支（要判断的地支）

    Returns:
        "长生"、"帝旺"、"墓"、"绝" 或 None（如果不在生旺墓绝中）

    Example:
        >>> get_shengwang_mujue_state(Wuxing.MU, Dizhi.HAI)
        '长生'
        >>> get_shengwang_mujue_state(Wuxing.MU, Dizhi.MAO)
        '帝旺'
        >>> get_shengwang_mujue_state(Wuxing.MU, Dizhi.WEI)
        '墓'
        >>> get_shengwang_mujue_state(Wuxing.MU, Dizhi.SHEN)
        '绝'
        >>> get_shengwang_mujue_state(Wuxing.MU, Dizhi.ZI)
        None
    """
    return DIZHI_STATE_MAP.get((yao_wuxing, target_dizhi))


def is_changsheng(yao_wuxing: Wuxing, target_dizhi: Dizhi) -> bool:
    """
    判断某地支是否为某五行的长生

    Args:
        yao_wuxing: 爻的五行
        target_dizhi: 目标地支

    Returns:
        如果是长生返回True，否则返回False
    """
    return get_changsheng(yao_wuxing) == target_dizhi


def is_diwang(yao_wuxing: Wuxing, target_dizhi: Dizhi) -> bool:
    """
    判断某地支是否为某五行的帝旺

    Args:
        yao_wuxing: 爻的五行
        target_dizhi: 目标地支

    Returns:
        如果是帝旺返回True，否则返回False
    """
    return get_diwang(yao_wuxing) == target_dizhi


def is_mu(yao_wuxing: Wuxing, target_dizhi: Dizhi) -> bool:
    """
    判断某地支是否为某五行的墓

    Args:
        yao_wuxing: 爻的五行
        target_dizhi: 目标地支

    Returns:
        如果是墓返回True，否则返回False
    """
    return get_mu(yao_wuxing) == target_dizhi


def is_jue(yao_wuxing: Wuxing, target_dizhi: Dizhi) -> bool:
    """
    判断某地支是否为某五行的绝

    Args:
        yao_wuxing: 爻的五行
        target_dizhi: 目标地支

    Returns:
        如果是绝返回True，否则返回False
    """
    return get_jue(yao_wuxing) == target_dizhi


# =============================================================================
# 卦例计算函数
# =============================================================================

def calculate_yao_shengwang_mujue(yao_wuxing: Wuxing, compare_dizhi: Dizhi) -> Dict:
    """
    计算爻与对比地支的生旺墓绝关系

    常用于判断：
    - 动爻与变爻的关系
    - 飞神与伏神的关系
    - 爻支与日支的关系

    Args:
        yao_wuxing: 爻的五行
        compare_dizhi: 对比的地支（如日支、变爻地支等）

    Returns:
        生旺墓绝信息字典，格式:
        {
            "yao_wuxing": "木",
            "compare_dizhi": "亥",
            "state": "长生" / "帝旺" / "墓" / "绝" / None,
            "description": "亥为木之长生" / "无生旺墓绝关系"
        }

    Example:
        >>> result = calculate_yao_shengwang_mujue(Wuxing.MU, Dizhi.HAI)
        >>> result["state"]
        '长生'
    """
    state = get_shengwang_mujue_state(yao_wuxing, compare_dizhi)

    if state:
        state_names = {
            "长生": "长生",
            "帝旺": "帝旺",
            "墓": "墓",
            "绝": "绝"
        }
        description = f"{compare_dizhi.value}为{yao_wuxing.value}之{state_names[state]}"
    else:
        description = "无生旺墓绝关系"

    return {
        "yao_wuxing": yao_wuxing.value,
        "compare_dizhi": compare_dizhi.value,
        "state": state,
        "description": description
    }


def calculate_shengwang_mujue_for_guali(guali) -> Dict:
    """
    为卦例计算所有爻与日支的生旺墓绝关系

    Args:
        guali: Guali对象

    Returns:
        生旺墓绝信息字典，格式:
        {
            "day_dizhi": "午",
            "yaos": [
                {
                    "position": 1,
                    "yao_dizhi": "子",
                    "yao_wuxing": "水",
                    "state": "帝旺",
                    "description": "子为水之帝旺"
                },
                ...
            ]
        }

    Example:
        >>> guali = Guali(ben_gua=ZhongGua.QIAN_WEI_TIAN, ganzhi_day="甲午")
        >>> guali.calculate_all()
        >>> result = calculate_shengwang_mujue_for_guali(guali)
    """
    result = {
        "day_dizhi": None,
        "yaos": []
    }

    # 如果没有日支，返回空结果
    if guali.day_dizhi is None:
        return result

    day_dizhi = guali.day_dizhi
    result["day_dizhi"] = day_dizhi.value

    # 计算每个爻与日支的生旺墓绝关系
    for yao in guali.yaos:
        if yao.wuxing is None or yao.dizhi is None:
            continue

        state_info = calculate_yao_shengwang_mujue(yao.wuxing, day_dizhi)
        result["yaos"].append({
            "position": yao.position,
            "yao_dizhi": yao.dizhi.value,
            "yao_wuxing": yao.wuxing.value,
            "state": state_info["state"],
            "description": state_info["description"]
        })

    return result


def calculate_dongyao_shengwang_mujue(guali) -> List[Dict]:
    """
    计算动爻与变爻的生旺墓绝关系

    Args:
        guali: Guali对象

    Returns:
        动爻生旺墓绝信息列表，格式:
        [
            {
                "position": 1,
                "ben_dizhi": "子",
                "bian_dizhi": "丑",
                "yao_wuxing": "水",
                "state": "墓" / None,
                "description": "丑为水之墓"
            },
            ...
        ]
    """
    result = []

    # 如果没有之卦，没有动爻
    if not guali.has_zhi_gua:
        return result

    for yao in guali.moving_yaos:
        if yao.wuxing is None or yao.dizhi is None:
            continue

        # 获取变爻地支
        bian_yao = guali.zhi_gua
        if bian_yao is None:
            continue

        # 计算变爻位置对应的变卦地支
        from backend.core.nama import get_dizhi_from_dan_gua
        bian_dizhi = get_dizhi_from_dan_gua(
            bian_yao.neigua if yao.position <= 3 else bian_yao.waigua,
            yao.position
        )

        if bian_dizhi is None:
            continue

        state_info = calculate_yao_shengwang_mujue(yao.wuxing, bian_dizhi)
        result.append({
            "position": yao.position,
            "ben_dizhi": yao.dizhi.value,
            "bian_dizhi": bian_dizhi.value,
            "yao_wuxing": yao.wuxing.value,
            "state": state_info["state"],
            "description": state_info["description"]
        })

    return result


# =============================================================================
# 辅助函数
# =============================================================================

def print_shengwang_mujue_table() -> None:
    """
    打印生旺墓绝对照表（调试用）
    """
    print("生旺墓绝对照表")
    print("=" * 50)
    print(f"{'五行':<6} {'长生':<4} {'帝旺':<4} {'墓':<4} {'绝':<4}")
    print("-" * 30)

    for wuxing in [Wuxing.MU, Wuxing.HUO, Wuxing.JIN, Wuxing.SHUI, Wuxing.TU]:
        states = SHENGWANG_MUJUE_MAP[wuxing]
        print(f"{wuxing.value:<6} {states['长生'].value:<4} {states['帝旺'].value:<4} {states['墓'].value:<4} {states['绝'].value:<4}")


if __name__ == "__main__":
    print("=== 生旺墓绝计算模块测试 ===")
    print()
    print_shengwang_mujue_table()

    print("\n=== 功能测试 ===")

    # 测试木的生旺墓绝
    print(f"\n木的长生: {get_changsheng(Wuxing.MU).value}")
    print(f"木的帝旺: {get_diwang(Wuxing.MU).value}")
    print(f"木的墓: {get_mu(Wuxing.MU).value}")
    print(f"木的绝: {get_jue(Wuxing.MU).value}")

    # 测试状态判断
    print(f"\n亥对木的状态: {get_shengwang_mujue_state(Wuxing.MU, Dizhi.HAI)}")
    print(f"卯对木的状态: {get_shengwang_mujue_state(Wuxing.MU, Dizhi.MAO)}")
    print(f"未对木的状态: {get_shengwang_mujue_state(Wuxing.MU, Dizhi.WEI)}")
    print(f"申对木的状态: {get_shengwang_mujue_state(Wuxing.MU, Dizhi.SHEN)}")
    print(f"子对木的状态: {get_shengwang_mujue_state(Wuxing.MU, Dizhi.ZI)}")

    # 测试布尔判断
    print(f"\n亥是否为木的长生: {is_changsheng(Wuxing.MU, Dizhi.HAI)}")
    print(f"卯是否为木的帝旺: {is_diwang(Wuxing.MU, Dizhi.MAO)}")
    print(f"子是否为木的长生: {is_changsheng(Wuxing.MU, Dizhi.ZI)}")

    # 测试爻与日支关系计算
    print("\n爻与日支关系:")
    result = calculate_yao_shengwang_mujue(Wuxing.MU, Dizhi.HAI)
    print(f"  {result['description']}")
