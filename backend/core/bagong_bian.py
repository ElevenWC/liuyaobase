"""B8 八宫变化：从本卦依次施加七种变化。上爻(第6位)永不参与。

index 0=初爻, index 5=上爻。
"""
from backend.core.enums import CODE_TO_NAME

# 七变步骤: (名称, 翻转索引列表)
_STEPS: list[tuple[str, list[int]]] = [
    ("一世", [0]),           # 初爻
    ("二世", [1]),           # 二爻(承接一世)
    ("三世", [2]),           # 三爻(承接二世)
    ("四世", [3]),           # 四爻(承接三世)
    ("五世", [4]),           # 五爻(承接四世)
    ("游魂", [3]),           # 四爻(承接五世, flips 四爻 back)
    ("归魂", [0, 1, 2]),     # 初二三爻(承接游魂, flips all three)
]


def check_bagong_relation(ben_code: str, zhi_code: str) -> str:
    """判断之卦是本卦的哪种八宫变化 → '一世'/'二世'/.../'归魂'/'' """
    if ben_code == zhi_code:
        return ""

    g: list[int] = [int(c) for c in ben_code]
    for name, indices in _STEPS:
        for i in indices:
            g[i] = 1 - g[i]
        if "".join(str(b) for b in g) == zhi_code:
            return name
    return ""


def calc_bagong_bian(code: str) -> list[dict]:
    """返回八宫七变列表（含卦名）

    calc_bagong_bian("111111") → [
        {"type": "一世", "code": "011111", "name": "天风姤"},
        ...共7个
    ]
    """
    result: list[dict] = []
    g: list[int] = [int(c) for c in code]

    for name, indices in _STEPS:
        for i in indices:
            g[i] = 1 - g[i]
        current_code = "".join(str(b) for b in g)
        result.append({
            "type": name,
            "code": current_code,
            "name": CODE_TO_NAME.get(current_code, ""),
        })

    return result
