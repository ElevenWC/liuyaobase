"""B5 神煞计算+传播（是/带）。输出 32 组状态。"""
from backend.core.dizhi_relation import check_he, check_chong

# ── 干禄（日干） ──────────────────────────────────────
_GAN_LU: dict[str, str] = {
    "甲": "寅", "乙": "卯",
    "丙": "巳", "戊": "巳",
    "丁": "午", "己": "午",
    "庚": "申", "辛": "酉",
    "壬": "亥", "癸": "子",
}

# ── 羊刃（日干） ──────────────────────────────────────
_YANG_REN: dict[str, str] = {
    "甲": "卯", "乙": "寅",
    "丙": "午", "戊": "午",
    "丁": "巳", "己": "巳",
    "庚": "酉", "辛": "申",
    "壬": "子", "癸": "亥",
}

# ── 驿马/桃花（日支 → 三合局 → 值） ──────────────────
_SANHE_JU = {
    "申": "申子辰", "子": "申子辰", "辰": "申子辰",
    "亥": "亥卯未", "卯": "亥卯未", "未": "亥卯未",
    "寅": "寅午戌", "午": "寅午戌", "戌": "寅午戌",
    "巳": "巳酉丑", "酉": "巳酉丑", "丑": "巳酉丑",
}
_YI_MA: dict[str, str] = {"申子辰": "寅", "亥卯未": "巳", "寅午戌": "申", "巳酉丑": "亥"}
_TAO_HUA: dict[str, str] = {"申子辰": "酉", "亥卯未": "子", "寅午戌": "卯", "巳酉丑": "午"}
_ZAI_SHA: dict[str, str] = {"申子辰": "午", "亥卯未": "酉", "寅午戌": "子", "巳酉丑": "卯"}
_JIE_SHA: dict[str, str] = {"申子辰": "巳", "巳酉丑": "寅", "寅午戌": "亥", "亥卯未": "申"}


def get_shensha_dizhi(day_gan: str, day_zhi: str) -> dict:
    """日干+日支 → 4 神煞地支值"""
    ju = _SANHE_JU.get(day_zhi, "")
    return {
        "gan_lu": _GAN_LU.get(day_gan, ""),
        "yi_ma": _YI_MA.get(ju, ""),
        "yang_ren": _YANG_REN.get(day_gan, ""),
        "tao_hua": _TAO_HUA.get(ju, ""),
        "zai_sha": _ZAI_SHA.get(ju, ""),
        "jie_sha": _JIE_SHA.get(ju, ""),
    }


def _check_and_propagate(shensha_zhi: str, dizhi_list: list[str]) -> tuple[str, str]:
    """对一组地支列表，判断'是'和'带'的爻位（返回逗号分隔字符串）"""
    is_yao: list[str] = []
    dai_yao: list[str] = []
    for i, d in enumerate(dizhi_list):
        if not d:
            continue
        y = str(i + 1)
        if d == shensha_zhi:
            is_yao.append(y)
        elif check_chong(d, shensha_zhi) or check_he(d, shensha_zhi):
            dai_yao.append(y)
    return (",".join(is_yao), ",".join(dai_yao))


def calc_shensha_status(
    day_gan: str,
    day_zhi: str,
    ben_dizhi: list[str],
    zhi_dizhi: list[str],
    yimao_dizhi: list[str],
    zengshan_dizhi: list[str],
) -> dict:
    """计算全部 32 组神煞状态。空值用空字符串。"""
    ss = get_shensha_dizhi(day_gan, day_zhi)
    result: dict = {}

    for name, shensha_zhi in ss.items():
        # 本卦
        is_str, dai_str = _check_and_propagate(shensha_zhi, ben_dizhi)
        result[f"ben_is_{name}"] = is_str
        result[f"ben_dai_{name}"] = dai_str
        # 之卦
        is_str, dai_str = _check_and_propagate(shensha_zhi, zhi_dizhi)
        result[f"zhi_is_{name}"] = is_str
        result[f"zhi_dai_{name}"] = dai_str
        # 易冒伏神
        is_str, dai_str = _check_and_propagate(shensha_zhi, yimao_dizhi)
        result[f"yimao_is_{name}"] = is_str
        result[f"yimao_dai_{name}"] = dai_str
        # 增删伏神（长度 0~2，不足 6 爻）
        is_str, dai_str = _check_and_propagate(shensha_zhi, zengshan_dizhi)
        result[f"zengshan_is_{name}"] = is_str
        result[f"zengshan_dai_{name}"] = dai_str

    return result
