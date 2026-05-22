"""B3 六神排列：根据日干确定初爻到上爻的六神分布。

纯查表——六神固定顺序（青龙→朱雀→勾陈→螣蛇→白虎→玄武），日干决定起点。
"""
from backend.core.enums import LIU_SHEN

# 日干 → 初爻六神（即起点索引）
_START: dict[str, int] = {
    "甲": 0, "乙": 0,        # 甲乙 → 青龙起
    "丙": 1, "丁": 1,        # 丙丁 → 朱雀起
    "戊": 2,                 # 戊   → 勾陈起
    "己": 3,                 # 己   → 螣蛇起
    "庚": 4, "辛": 4,        # 庚辛 → 白虎起
    "壬": 5, "癸": 5,        # 壬癸 → 玄武起
}


def get_liushen(day_gan: str) -> list[str]:
    """日干 → 初爻到上爻的六神列表（6 个元素）

    get_liushen("甲") → ["青龙","朱雀","勾陈","螣蛇","白虎","玄武"]
    """
    if day_gan not in _START:
        raise ValueError(f"无效日干: {day_gan}")
    start = _START[day_gan]
    return [LIU_SHEN[(start + i) % 6] for i in range(6)]
