"""
六爻卦例分析系统 - 纳甲装卦模块

本模块实现纳甲装卦功能，即根据单卦为各爻配置地支。

纳甲装卦规则：
根据单卦的不同，各爻位对应固定的地支：
- 内卦（初爻、二爻、三爻）根据内卦单卦确定
- 外卦（四爻、五爻、上爻）根据外卦单卦确定
"""
from typing import Tuple, Optional, Dict

from backend.core.enums import DanGua, Dizhi, ZhongGua


# =============================================================================
# 纳甲装卦映射表
# =============================================================================

# 单卦内卦地支映射表 (初爻, 二爻, 三爻)
NAMA_DIZHI_NEIGUA: Dict[DanGua, Tuple[Dizhi, Dizhi, Dizhi]] = {
    DanGua.QIAN: (Dizhi.ZI, Dizhi.YIN, Dizhi.CHEN),    # 乾卦（内卦）：子、寅、辰
    DanGua.KAN:  (Dizhi.YIN, Dizhi.CHEN, Dizhi.WU),    # 坎卦（内卦）：寅、辰、午
    DanGua.GEN:  (Dizhi.CHEN, Dizhi.WU, Dizhi.SHEN),   # 艮卦（内卦）：辰、午、申
    DanGua.ZHEN: (Dizhi.ZI, Dizhi.YIN, Dizhi.CHEN),    # 震卦（内卦）：子、寅、辰
    DanGua.XUN:  (Dizhi.CHOU, Dizhi.HAI, Dizhi.YOU),   # 巽卦（内卦）：丑、亥、酉
    DanGua.LI:   (Dizhi.MAO, Dizhi.CHOU, Dizhi.HAI),   # 离卦（内卦）：卯、丑、亥
    DanGua.KUN:  (Dizhi.WEI, Dizhi.SI, Dizhi.MAO),     # 坤卦（内卦）：未、巳、卯
    DanGua.DUI:  (Dizhi.SI, Dizhi.MAO, Dizhi.CHOU),    # 兑卦（内卦）：巳、卯、丑
}

# 单卦外卦地支映射表 (四爻, 五爻, 上爻)
NAMA_DIZHI_WAIGUA: Dict[DanGua, Tuple[Dizhi, Dizhi, Dizhi]] = {
    DanGua.QIAN: (Dizhi.WU, Dizhi.SHEN, Dizhi.XU),     # 乾卦（外卦）：午、申、戌
    DanGua.KAN:  (Dizhi.SHEN, Dizhi.XU, Dizhi.ZI),     # 坎卦（外卦）：申、戌、子
    DanGua.GEN:  (Dizhi.XU, Dizhi.ZI, Dizhi.YIN),      # 艮卦（外卦）：戌、子、寅
    DanGua.ZHEN: (Dizhi.WU, Dizhi.SHEN, Dizhi.XU),     # 震卦（外卦）：午、申、戌
    DanGua.XUN:  (Dizhi.WEI, Dizhi.SI, Dizhi.MAO),     # 巽卦（外卦）：未、巳、卯
    DanGua.LI:   (Dizhi.YOU, Dizhi.WEI, Dizhi.SI),     # 离卦（外卦）：酉、未、巳
    DanGua.KUN:  (Dizhi.CHOU, Dizhi.HAI, Dizhi.YOU),   # 坤卦（外卦）：丑、亥、酉
    DanGua.DUI:  (Dizhi.HAI, Dizhi.YOU, Dizhi.WEI),    # 兑卦（外卦）：亥、酉、未
}


# =============================================================================
# 核心函数
# =============================================================================

def get_dizhi_from_dan_gua(dan_gua: DanGua, position: int) -> Optional[Dizhi]:
    """
    根据单卦和爻位获取地支

    Args:
        dan_gua: 单卦枚举
        position: 爻位 (1-6)
            - 1-3: 内卦（初爻、二爻、三爻）
            - 4-6: 外卦（四爻、五爻、上爻）

    Returns:
        对应的地支枚举

    Example:
        >>> get_dizhi_from_dan_gua(DanGua.QIAN, 1)
        <Dizhi.ZI: '子'>
        >>> get_dizhi_from_dan_gua(DanGua.QIAN, 4)
        <Dizhi.WU: '午'>
    """
    if position < 1 or position > 6:
        raise ValueError(f"爻位必须在1-6之间，当前值: {position}")

    if position <= 3:
        # 内卦（初爻、二爻、三爻）
        dizhi_tuple = NAMA_DIZHI_NEIGUA.get(dan_gua)
        if dizhi_tuple:
            return dizhi_tuple[position - 1]
    else:
        # 外卦（四爻、五爻、上爻）
        dizhi_tuple = NAMA_DIZHI_WAIGUA.get(dan_gua)
        if dizhi_tuple:
            return dizhi_tuple[position - 4]

    return None


def get_dizhi_list_from_dan_gua(dan_gua: DanGua, is_neigua: bool) -> Tuple[Dizhi, Dizhi, Dizhi]:
    """
    获取单卦的三个地支

    Args:
        dan_gua: 单卦枚举
        is_neigua: True表示内卦，False表示外卦

    Returns:
        三个地支的元组

    Example:
        >>> get_dizhi_list_from_dan_gua(DanGua.QIAN, True)
        (<Dizhi.ZI: '子'>, <Dizhi.YIN: '寅'>, <Dizhi.CHEN: '辰'>)
    """
    if is_neigua:
        return NAMA_DIZHI_NEIGUA[dan_gua]
    else:
        return NAMA_DIZHI_WAIGUA[dan_gua]


def get_all_dizhi_from_zhong_gua(zhong_gua: ZhongGua) -> list:
    """
    获取重卦六个爻的地支列表

    Args:
        zhong_gua: 重卦枚举

    Returns:
        六个地支的列表，从初爻到上爻

    Example:
        >>> gua = ZhongGua.QIAN_WEI_TIAN
        >>> get_all_dizhi_from_zhong_gua(gua)
        [<Dizhi.ZI: '子'>, <Dizhi.YIN: '寅'>, <Dizhi.CHEN: '辰'>,
         <Dizhi.WU: '午'>, <Dizhi.SHEN: '申'>, <Dizhi.XU: '戌'>]
    """
    neigua = zhong_gua.neigua
    waigua = zhong_gua.waigua

    # 获取内卦三个地支
    neigua_dizhi = NAMA_DIZHI_NEIGUA[neigua]

    # 获取外卦三个地支
    waigua_dizhi = NAMA_DIZHI_WAIGUA[waigua]

    # 合并为六个爻的地支列表
    return list(neigua_dizhi) + list(waigua_dizhi)


# =============================================================================
# Guali类集成函数
# =============================================================================

def load_dizhi_to_guali(guali) -> None:
    """
    为卦例的六个爻装地支

    根据本卦的内卦和外卦为六个爻设置地支。
    此函数会直接修改guali对象的yaos列表中各爻的dizhi属性。

    Args:
        guali: Guali对象

    Example:
        >>> from backend.core.models import Guali
        >>> guali = Guali(ben_gua=ZhongGua.QIAN_WEI_TIAN)
        >>> load_dizhi_to_guali(guali)
        >>> guali.yaos[0].dizhi
        <Dizhi.ZI: '子'>
    """
    if guali.ben_gua is None:
        return

    # 获取本卦的内卦和外卦
    neigua = guali.ben_gua.neigua
    waigua = guali.ben_gua.waigua

    # 获取内卦和外卦的地支
    neigua_dizhi = NAMA_DIZHI_NEIGUA[neigua]
    waigua_dizhi = NAMA_DIZHI_WAIGUA[waigua]

    # 为六个爻设置地支
    for i, yao in enumerate(guali.yaos):
        if i < 3:
            # 初爻、二爻、三爻 - 内卦
            yao.dizhi = neigua_dizhi[i]
        else:
            # 四爻、五爻、上爻 - 外卦
            yao.dizhi = waigua_dizhi[i - 3]


def load_dizhi_to_bian_yao(guali) -> None:
    """
    为变爻装地支

    当有之卦时，需要为之卦中的变爻设置地支。
    变爻的地支与之卦对应爻位的地支相同。

    注意：此函数通常不需要单独调用，因为爻的地支是固定的。
    无论爻是动爻、静爻还是变爻，其地支都不变。

    Args:
        guali: Guali对象
    """
    # 爻的地支是固定的，不需要特殊处理
    # 此函数保留用于未来可能的扩展
    pass


# =============================================================================
# 验证函数
# =============================================================================

def validate_nama_mapping() -> bool:
    """
    验证纳甲装卦映射表的完整性

    检查所有八个单卦都有完整的内外卦映射。

    Returns:
        如果映射表完整返回True，否则返回False
    """
    for gua in DanGua:
        if gua not in NAMA_DIZHI_NEIGUA:
            print(f"缺少内卦映射: {gua.gua_name}")
            return False
        if gua not in NAMA_DIZHI_WAIGUA:
            print(f"缺少外卦映射: {gua.gua_name}")
            return False

    return True


def print_nama_table():
    """
    打印纳甲装卦映射表

    用于调试和验证。
    """
    print("纳甲装卦映射表")
    print("=" * 60)
    print(f"{'单卦':<6} {'内卦(初二三)':<20} {'外卦(四五上)':<20}")
    print("-" * 60)

    for gua in DanGua:
        neigua = NAMA_DIZHI_NEIGUA[gua]
        waigua = NAMA_DIZHI_WAIGUA[gua]

        neigua_str = f"{neigua[0].value}、{neigua[1].value}、{neigua[2].value}"
        waigua_str = f"{waigua[0].value}、{waigua[1].value}、{waigua[2].value}"

        print(f"{gua.gua_name:<6} {neigua_str:<20} {waigua_str:<20}")


if __name__ == "__main__":
    # 验证映射表
    if validate_nama_mapping():
        print("纳甲装卦映射表验证通过")
        print()
        print_nama_table()
    else:
        print("纳甲装卦映射表验证失败")
