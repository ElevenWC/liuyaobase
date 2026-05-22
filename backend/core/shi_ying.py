"""B4 世应定位：根据宫位类型确定世爻和应爻位置。世应相隔两爻。

本卦和之卦使用相同的定位规则。
"""

# 宫位类型 → (世爻位置, 应爻位置)  1=初爻, 6=上爻
_SHI_YING: dict[str, tuple[int, int]] = {
    "本宫": (6, 3),
    "一世": (1, 4),
    "二世": (2, 5),
    "三世": (3, 6),
    "四世": (4, 1),
    "五世": (5, 2),
    "游魂": (4, 1),
    "归魂": (3, 6),
}


def get_shi_ying(palace_type: str) -> tuple[int, int]:
    """宫位类型 → (世爻位置, 应爻位置)

    get_shi_ying("一世") → (1, 4)  # 世在初爻, 应在四爻
    """
    if palace_type not in _SHI_YING:
        raise ValueError(f"无效宫位类型: {palace_type}")
    return _SHI_YING[palace_type]


def get_shi_ying_labels(palace_type: str) -> list[str]:
    """宫位类型 → 6爻世应标签列表（初爻→上爻）

    get_shi_ying_labels("一世") → ["世", "", "", "应", "", ""]
    """
    shi, ying = get_shi_ying(palace_type)
    labels = [""] * 6
    labels[shi - 1] = "世"
    labels[ying - 1] = "应"
    return labels
