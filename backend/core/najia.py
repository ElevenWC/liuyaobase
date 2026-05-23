"""B2 纳甲装卦：为 64 卦的每一爻配置地支和天干。固定规则，384 条。

代码 index 0=初爻, index 5=上爻。内卦=前3位, 外卦=后3位。
"""
from backend.core.enums import CODE_TO_GUA, GUA_TIANGAN, NAN_KUN_RELATED

# ── 纳甲地支表 ────────────────────────────────────────
# 8个单卦 → {位置: [初爻, 二爻, 三爻, 四爻, 五爻, 上爻]}
_NAJIA_DIZHI: dict[str, list[str]] = {
    "111": ["子", "寅", "辰", "午", "申", "戌"],  # 乾
    "010": ["寅", "辰", "午", "申", "戌", "子"],  # 坎
    "001": ["辰", "午", "申", "戌", "子", "寅"],  # 艮
    "100": ["子", "寅", "辰", "午", "申", "戌"],  # 震（与乾同）
    "011": ["丑", "亥", "酉", "未", "巳", "卯"],  # 巽
    "101": ["卯", "丑", "亥", "酉", "未", "巳"],  # 离
    "000": ["未", "巳", "卯", "丑", "亥", "酉"],  # 坤
    "110": ["巳", "卯", "丑", "亥", "酉", "未"],  # 兑
}

# 乾坤双天干: (内卦夏至, 内卦冬至, 外卦夏至, 外卦冬至)
# 冬至→夏至(阳遁): 乾内甲乾外壬 / 坤内乙坤外癸
# 夏至→冬至(阴遁): 乾内壬乾外甲 / 坤内癸坤外乙
_QIAN_TIANGAN = ("壬", "甲", "甲", "壬")
_KUN_TIANGAN = ("癸", "乙", "乙", "癸")


def get_neigua_code(code: str) -> str:
    """提取内卦代码（前3位）"""
    return code[:3]


def get_waigua_code(code: str) -> str:
    """提取外卦代码（后3位）"""
    return code[3:]


def get_dizhi(code: str) -> list[str]:
    """返回 6 个地支，初爻→上爻"""
    inner = get_neigua_code(code)
    outer = get_waigua_code(code)
    # 内卦前3爻(初二三) + 外卦后3爻(四五上)
    return _NAJIA_DIZHI[inner][:3] + _NAJIA_DIZHI[outer][3:]


def get_yao_info(code: str) -> list[dict]:
    """返回 6 爻的纳甲信息（初爻→上爻）"""
    inner = get_neigua_code(code)
    outer = get_waigua_code(code)
    inner_gua = CODE_TO_GUA[inner]
    outer_gua = CODE_TO_GUA[outer]
    dizhi_list = get_dizhi(code)

    is_nan_kun = code in NAN_KUN_RELATED

    result: list[dict] = []
    for i in range(6):
        idx = i + 1  # 爻位 1-6
        info: dict = {"yao_index": idx, "dizhi": dizhi_list[i]}

        if i < 3:
            gua_code = inner
            gua_name = inner_gua
        else:
            gua_code = outer
            gua_name = outer_gua

        if is_nan_kun:
            info["tiangan"] = None
            if gua_code == "111":  # 乾
                info["tiangan_summer"] = _QIAN_TIANGAN[0] if i < 3 else _QIAN_TIANGAN[2]
                info["tiangan_winter"] = _QIAN_TIANGAN[1] if i < 3 else _QIAN_TIANGAN[3]
            elif gua_code == "000":  # 坤
                info["tiangan_summer"] = _KUN_TIANGAN[0] if i < 3 else _KUN_TIANGAN[2]
                info["tiangan_winter"] = _KUN_TIANGAN[1] if i < 3 else _KUN_TIANGAN[3]
            else:
                # 乾坤相关但该爻不在乾坤的卦上，用普通天干
                info["tiangan"] = GUA_TIANGAN.get(gua_name)
                info["tiangan_summer"] = None
                info["tiangan_winter"] = None
        else:
            info["tiangan"] = GUA_TIANGAN.get(gua_name)
            info["tiangan_summer"] = None
            info["tiangan_winter"] = None

        result.append(info)

    return result
