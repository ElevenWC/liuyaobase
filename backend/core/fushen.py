"""
六爻卦例分析系统 - 伏神计算模块

本模块提供伏神计算功能，用于查找卦例中缺失的六亲。

伏神规则:
1. 检查本卦六亲是否齐全
2. 若缺某六亲，查同宫本宫卦
3. 本宫卦中对应六亲的爻为伏神
4. 本卦同爻位的爻为飞神

伏神和飞神的关系:
- 飞神生伏神: 谓之得长生
- 飞神克伏神: 谓之受克
- 伏神生飞神: 谓之泄气
- 伏神克飞神: 谓之出暴
"""
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

from backend.core.enums import LiuQin, ZhongGua, Wuxing, Dizhi


# =============================================================================
# 数据结构定义
# =============================================================================

@dataclass
class FuShenInfo:
    """伏神信息数据类"""
    liuqin: LiuQin          # 缺失的六亲
    fushen_position: int     # 伏神所在爻位 (来自本宫卦)
    fushen_dizhi: Dizhi      # 伏神地支
    fushen_wuxing: Wuxing    # 伏神五行
    feishen_position: int    # 飞神所在爻位 (本卦同位爻)
    feishen_dizhi: Dizhi     # 飞神地支
    feishen_wuxing: Wuxing   # 飞神五行
    feishen_liuqin: LiuQin   # 飞神六亲
    relation: str            # 飞神与伏神的关系


# =============================================================================
# 本宫卦映射表
# =============================================================================

# 卦宫到本宫卦的映射
GONGWEI_TO_BENGONG: Dict[str, ZhongGua] = {
    "乾宫": ZhongGua.QIAN_WEI_TIAN,
    "坎宫": ZhongGua.KAN_WEI_SHUI,
    "艮宫": ZhongGua.GEN_WEI_SHAN,
    "震宫": ZhongGua.ZHEN_WEI_LEI,
    "巽宫": ZhongGua.XUN_WEI_FENG,
    "离宫": ZhongGua.LI_WEI_HUO,
    "坤宫": ZhongGua.KUN_WEI_DI,
    "兑宫": ZhongGua.DUI_WEI_ZE,
}


# =============================================================================
# 核心函数
# =============================================================================

def check_liuqin_complete(yaos: list) -> List[LiuQin]:
    """
    检查六个爻是否包含所有六亲

    Args:
        yaos: 六个爻的列表

    Returns:
        缺少的六亲列表，如果六亲齐全返回空列表

    Example:
        >>> yaos = [
        ...     Yao(position=1, liuqin=LiuQin.FU_MU),
        ...     Yao(position=2, liuqin=LiuQin.GUAN_GUI),
        ...     Yao(position=3, liuqin=LiuQin.ZI_SUN),
        ...     Yao(position=4, liuqin=LiuQin.QI_CAI),
        ...     Yao(position=5, liuqin=LiuQin.XIONG_DI),
        ...     Yao(position=6, liuqin=LiuQin.FU_MU)
        ... ]
        >>> missing = check_liuqin_complete(yaos)
        >>> len(missing) == 0  # 六亲齐全
        True
    """
    # 获取所有六亲
    all_liuqin = set(LiuQin)

    # 获取已存在的六亲
    existing_liuqin = set()
    for yao in yaos:
        if yao.liuqin is not None:
            existing_liuqin.add(yao.liuqin)

    # 计算缺失的六亲
    missing = all_liuqin - existing_liuqin
    return list(missing)


def get_ben_gong_gua(gongwei: str) -> Optional[ZhongGua]:
    """
    根据卦宫获取本宫卦

    Args:
        gongwei: 卦宫名称，如"乾宫"

    Returns:
        对应的本宫卦枚举，如果找不到返回None

    Example:
        >>> get_ben_gong_gua("乾宫")
        <ZhongGua.QIAN_WEI_TIAN: ...>
        >>> get_ben_gong_gua("震宫")
        <ZhongGua.ZHEN_WEI_LEI: ...>
    """
    return GONGWEI_TO_BENGONG.get(gongwei)


def find_yao_by_liuqin(yaos: list, liuqin: LiuQin) -> Optional[dict]:
    """
    在爻列表中查找具有指定六亲的爻

    Args:
        yaos: 爻列表
        liuqin: 要查找的六亲

    Returns:
        找到的爻信息字典，包含position、dizhi、wuxing等
        如果找不到返回None

    Example:
        >>> yao_info = find_yao_by_liuqin(yaos, LiuQin.QI_CAI)
        >>> yao_info["position"]
        3
    """
    for yao in yaos:
        if yao.liuqin == liuqin:
            return {
                "position": yao.position,
                "dizhi": yao.dizhi,
                "wuxing": yao.wuxing,
                "liuqin": yao.liuqin
            }
    return None


def calculate_feishen_fushen_relation(feishen_wuxing: Wuxing, fushen_wuxing: Wuxing) -> str:
    """
    计算飞神与伏神的关系

    Args:
        feishen_wuxing: 飞神五行
        fushen_wuxing: 伏神五行

    Returns:
        关系描述字符串
    """
    if feishen_wuxing == fushen_wuxing:
        return "比和"

    # 飞神生伏神
    if feishen_wuxing.generates(fushen_wuxing):
        return "飞生伏(得长生)"

    # 飞神克伏神
    if feishen_wuxing.overcomes(fushen_wuxing):
        return "飞克伏(受克)"

    # 伏神生飞神
    if fushen_wuxing.generates(feishen_wuxing):
        return "伏生飞(泄气)"

    # 伏神克飞神
    if fushen_wuxing.overcomes(feishen_wuxing):
        return "伏克飞(出暴)"

    return "无关系"


def find_fushen(guali, missing_liuqin: List[LiuQin]) -> List[FuShenInfo]:
    """
    查找伏神信息

    从本宫卦中查找缺失六亲对应的爻作为伏神。

    Args:
        guali: Guali对象
        missing_liuqin: 缺失的六亲列表

    Returns:
        伏神信息列表

    Example:
        >>> guali = Guali(ben_gua=ZhongGua.TIAN_FENG_GOU)
        >>> load_dizhi_to_guali(guali)
        >>> guali.set_liuqin()
        >>> missing = check_liuqin_complete(guali.yaos)
        >>> fushen_list = find_fushen(guali, missing)
    """
    if not missing_liuqin:
        return []

    # 获取本宫卦
    ben_gong_gua = get_ben_gong_gua(guali.gongwei)
    if ben_gong_gua is None:
        return []

    # 创建本宫卦的Guali对象并计算六亲
    from backend.core.models import Guali
    from backend.core.nama import load_dizhi_to_guali

    ben_gong_guali = Guali(ben_gua=ben_gong_gua)
    load_dizhi_to_guali(ben_gong_guali)
    ben_gong_guali.set_liuqin()

    fushen_list = []

    for liuqin in missing_liuqin:
        # 在本宫卦中查找该六亲对应的爻
        fushen_yao = find_yao_by_liuqin(ben_gong_guali.yaos, liuqin)
        if fushen_yao is None:
            continue

        position = fushen_yao["position"]

        # 在本卦中获取同爻位的飞神
        feishen_yao = guali.get_yao_by_position(position)
        if feishen_yao is None:
            continue

        # 计算飞神与伏神的关系
        relation = calculate_feishen_fushen_relation(
            feishen_yao.wuxing,
            fushen_yao["wuxing"]
        )

        fushen_info = FuShenInfo(
            liuqin=liuqin,
            fushen_position=position,
            fushen_dizhi=fushen_yao["dizhi"],
            fushen_wuxing=fushen_yao["wuxing"],
            feishen_position=position,
            feishen_dizhi=feishen_yao.dizhi,
            feishen_wuxing=feishen_yao.wuxing,
            feishen_liuqin=feishen_yao.liuqin,
            relation=relation
        )
        fushen_list.append(fushen_info)

    return fushen_list


# =============================================================================
# Guali类集成函数
# =============================================================================

def calculate_fushen_for_guali(guali) -> Dict:
    """
    为卦例计算伏神

    Args:
        guali: Guali对象

    Returns:
        伏神信息字典，格式:
        {
            "has_fushen": bool,  # 是否有伏神
            "missing_liuqin": [...],  # 缺失的六亲列表
            "fushen_list": [...],  # 伏神信息列表
        }

    Example:
        >>> guali = Guali(ben_gua=ZhongGua.TIAN_FENG_GOU)
        >>> guali.calculate_all()
        >>> fushen_info = calculate_fushen_for_guali(guali)
    """
    # 检查六亲是否齐全
    missing_liuqin = check_liuqin_complete(guali.yaos)

    if not missing_liuqin:
        return {
            "has_fushen": False,
            "missing_liuqin": [],
            "fushen_list": []
        }

    # 查找伏神
    fushen_list = find_fushen(guali, missing_liuqin)

    return {
        "has_fushen": True,
        "missing_liuqin": [lq.value for lq in missing_liuqin],
        "fushen_list": [
            {
                "liuqin": fs.liuqin.value,
                "fushen_position": fs.fushen_position,
                "fushen_dizhi": fs.fushen_dizhi.value if fs.fushen_dizhi else None,
                "fushen_wuxing": fs.fushen_wuxing.value if fs.fushen_wuxing else None,
                "feishen_position": fs.feishen_position,
                "feishen_dizhi": fs.feishen_dizhi.value if fs.feishen_dizhi else None,
                "feishen_wuxing": fs.feishen_wuxing.value if fs.feishen_wuxing else None,
                "feishen_liuqin": fs.feishen_liuqin.value if fs.feishen_liuqin else None,
                "relation": fs.relation
            }
            for fs in fushen_list
        ]
    }


# =============================================================================
# 辅助函数
# =============================================================================

def print_fushen_info(fushen_info: Dict) -> None:
    """
    打印伏神信息

    Args:
        fushen_info: 伏神信息字典
    """
    if not fushen_info["has_fushen"]:
        print("此卦六亲齐全，无伏神")
        return

    print("伏神信息:")
    print(f"  缺失六亲: {', '.join(fushen_info['missing_liuqin'])}")
    print()

    for fs in fushen_info["fushen_list"]:
        print(f"  【{fs['liuqin']}】")
        print(f"    伏神: {fs['fushen_position']}爻 {fs['fushen_dizhi']}({fs['fushen_wuxing']})")
        print(f"    飞神: {fs['feishen_position']}爻 {fs['feishen_dizhi']}({fs['feishen_wuxing']}) - {fs['feishen_liuqin']}")
        print(f"    关系: {fs['relation']}")
        print()


if __name__ == "__main__":
    print("=== 伏神计算模块测试 ===")
    print()

    from backend.core.models import Guali
    from backend.core.nama import load_dizhi_to_guali

    # 测试天风姤（乾宫一世卦）
    print("测试卦例: 天风姤（乾宫一世）")
    print("-" * 40)

    guali = Guali(ben_gua=ZhongGua.TIAN_FENG_GOU)
    load_dizhi_to_guali(guali)
    guali.set_liuqin()

    # 检查六亲
    print("六亲分布:")
    for yao in guali.yaos:
        print(f"  {yao.position_name}: {yao.dizhi.value if yao.dizhi else '?'} - {yao.liuqin.value if yao.liuqin else '?'}")

    # 检查缺失的六亲
    missing = check_liuqin_complete(guali.yaos)
    print(f"\n缺失的六亲: {[m.value for m in missing]}")

    # 计算伏神
    fushen_info = calculate_fushen_for_guali(guali)
    print()
    print_fushen_info(fushen_info)
