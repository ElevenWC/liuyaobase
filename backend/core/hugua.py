"""B7 互卦计算：从原卦中取二三四爻为内卦、三四五爻为外卦。"""


def calc_hugua(code: str) -> str:
    """原卦6位代码 → 互卦6位代码

    calc_hugua("110010") → "100001"（水泽节→山雷颐）
    """
    # 互卦内卦 = 第2,3,4位（index 1,2,3）
    inner = code[1] + code[2] + code[3]
    # 互卦外卦 = 第3,4,5位（index 2,3,4）
    outer = code[2] + code[3] + code[4]
    return inner + outer
