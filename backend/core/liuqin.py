"""B3 六亲计算：根据卦宫五行和爻地支五行确定六亲属性。

五种调用场景（本卦/变爻/之卦/易冒伏神/增删伏神）共用同一套规则。
"""
from backend.core.enums import DIZHI_WUXING

# 生克关系：元素A对元素B的关系
_SHENG_MAP: dict[str, str] = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
_KE_MAP: dict[str, str] = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}


def calc_liuqin(gua_element: str, yao_dizhi: str) -> str:
    """卦宫五行 + 爻地支 → 六亲

    calc_liuqin("火", "子") → "官鬼"  （子水克火 → 爻克宫 → 官鬼）
    calc_liuqin("火", "午") → "兄弟"  （午火=火 → 宫=爻 → 兄弟）
    calc_liuqin("火", "卯") → "父母"  （卯木生火 → 爻生宫 → 父母）
    """
    yao_wx = DIZHI_WUXING[yao_dizhi]

    if yao_wx == gua_element:
        return "兄弟"
    if _SHENG_MAP.get(yao_wx) == gua_element:
        return "父母"   # 爻生宫
    if _KE_MAP.get(yao_wx) == gua_element:
        return "官鬼"   # 爻克宫
    if _SHENG_MAP.get(gua_element) == yao_wx:
        return "子孙"   # 宫生爻
    if _KE_MAP.get(gua_element) == yao_wx:
        return "妻财"   # 宫克爻

    # 理论上不会到这里
    raise ValueError(f"无法计算六亲: gua_element={gua_element}, dizhi={yao_dizhi}")


def get_liuqin_list(gua_element: str, dizhi_list: list[str]) -> list[str]:
    """批量计算 6 个爻的六亲"""
    return [calc_liuqin(gua_element, d) for d in dizhi_list]
