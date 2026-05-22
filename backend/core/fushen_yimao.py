"""B4 易冒伏神：64卦每爻都有伏神，共384条。4种卦类型规则不同。"""
from backend.core.enums import (
    CODE_TO_PALACE, CODE_TO_PALACE_TYPE, OPPOSITE_GUA,
    PALACE_TO_BASE_CODE, PALACE_WUXING,
)
from backend.core.najia import get_dizhi
from backend.core.liuqin import calc_liuqin


def _get_opposite_base(palace: str) -> str:
    """卦宫 → 对宫本宫卦代码"""
    gua = palace[0]  # "乾宫" → "乾"
    opp_gua = OPPOSITE_GUA[gua]
    return PALACE_TO_BASE_CODE[f"{opp_gua}宫"]


def _get_wushi_code(base_code: str) -> str:
    """本宫首卦 → 五世卦代码"""
    g = [int(c) for c in base_code]
    for idx in [0, 1, 2, 3, 4]:  # 一世→二世→三世→四世→五世
        g[idx] = 1 - g[idx]
    return "".join(str(b) for b in g)


def get_fushen(code: str, yao_index: int) -> dict:
    """指定卦指定爻位的易冒伏神 → {fushen_dizhi, fushen_liuqin}"""
    palace = CODE_TO_PALACE[code]
    element = PALACE_WUXING[palace]
    ptype = CODE_TO_PALACE_TYPE[code]
    base_code = PALACE_TO_BASE_CODE[palace]
    i = yao_index - 1  # 0-based

    if ptype == "本宫卦":
        source_code = _get_opposite_base(palace)
    elif ptype in ("一世卦", "二世卦", "三世卦", "四世卦", "五世卦"):
        source_code = base_code
    elif ptype == "游魂卦":
        if i < 3:  # 内卦
            source_code = _get_opposite_base(palace)
        else:      # 外卦
            source_code = _get_wushi_code(base_code)
    elif ptype == "归魂卦":
        if i < 3:  # 内卦
            source_code = _get_opposite_base(palace)
        else:      # 外卦
            source_code = base_code
    else:
        raise ValueError(f"未知宫位类型: {ptype}")

    source_dizhi = get_dizhi(source_code)
    dizhi = source_dizhi[i]
    liuqin = calc_liuqin(element, dizhi)

    return {"fushen_dizhi": dizhi, "fushen_liuqin": liuqin, "yao_index": yao_index}


def get_all_fushen(code: str) -> list[dict]:
    """返回该卦全部 6 爻的易冒伏神"""
    return [get_fushen(code, i) for i in range(1, 7)]
