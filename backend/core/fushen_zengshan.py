"""B4 增删伏神：本卦缺失六亲 → 从本宫首卦借伏神。

飞神 = 本卦同爻位；伏神 = 本宫首卦中缺失六亲的爻。
"""
from backend.core.enums import CODE_TO_PALACE, LIU_QIN, PALACE_TO_BASE_CODE, PALACE_WUXING
from backend.core.najia import get_dizhi
from backend.core.liuqin import calc_liuqin


def get_fushen(code: str) -> list[dict]:
    """返回增删伏神列表（0~2 条）。

    [{"yao_index": 2, "missing_liuqin": "妻财",
      "fushen_dizhi": "寅",  "fushen_liuqin": "妻财",
      "feishen_dizhi": "亥", "feishen_liuqin": "子孙"}]
    """
    palace = CODE_TO_PALACE[code]
    element = PALACE_WUXING[palace]
    base_code = PALACE_TO_BASE_CODE[palace]

    ben_dizhi = get_dizhi(code)
    base_dizhi = get_dizhi(base_code)

    # 本卦 6 爻六亲
    ben_liuqin = [calc_liuqin(element, d) for d in ben_dizhi]
    # 本宫首卦 6 爻六亲
    base_liuqin = [calc_liuqin(element, d) for d in base_dizhi]

    # 找出缺失的六亲
    present = set(ben_liuqin)
    missing = [q for q in LIU_QIN if q not in present]

    result: list[dict] = []
    for mq in missing:
        # 在本宫首卦中找到该六亲的爻位
        for i in range(6):
            if base_liuqin[i] == mq:
                yao_index = i + 1
                result.append({
                    "yao_index": yao_index,
                    "missing_liuqin": mq,
                    "fushen_dizhi": base_dizhi[i],
                    "fushen_liuqin": base_liuqin[i],
                    "feishen_dizhi": ben_dizhi[i],
                    "feishen_liuqin": ben_liuqin[i],
                })
                break

    return result
