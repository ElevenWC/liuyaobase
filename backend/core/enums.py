"""
六爻卦例分析系统 - 核心枚举定义

本模块定义六爻预测学中所有核心元素的枚举类型，包括：
- 五行 (Wuxing): 木、火、土、金、水
- 天干 (Tiangan): 甲、乙、丙、丁、戊、己、庚、辛、壬、癸
- 地支 (Dizhi): 子、丑、寅、卯、辰、巳、午、未、申、酉、戌、亥
- 单卦 (DanGua): 乾、兑、离、震、巽、坎、艮、坤
- 重卦 (ZhongGua): 六十四卦
- 六亲 (LiuQin): 父母、官鬼、子孙、妻财、兄弟
- 六神 (LiuShen): 青龙、朱雀、勾陈、螣蛇、白虎、玄武
- 神煞 (ShenSha): 干禄、驿马、羊刃、桃花
"""
from enum import Enum, unique
from typing import Optional, List, Tuple, Dict


# =============================================================================
# 五行系统
# =============================================================================

@unique
class Wuxing(Enum):
    """五行枚举"""
    MU = "木"
    HUO = "火"
    TU = "土"
    JIN = "金"
    SHUI = "水"

    def generates(self, other: 'Wuxing') -> bool:
        """
        判断当前五行是否生另一五行

        相生关系: 金生水 → 水生木 → 木生火 → 火生土 → 土生金

        Args:
            other: 另一个五行

        Returns:
            bool: 如果当前五行生other返回True，否则返回False
        """
        return other == WUXING_SHENG.get(self)

    def overcomes(self, other: 'Wuxing') -> bool:
        """
        判断当前五行是否克另一五行

        相克关系: 金克木 → 木克土 → 土克水 → 水克火 → 火克金

        Args:
            other: 另一个五行

        Returns:
            bool: 如果当前五行克other返回True，否则返回False
        """
        return other == WUXING_KE.get(self)

    def get_sheng(self) -> Optional['Wuxing']:
        """获取当前五行所生的五行"""
        return WUXING_SHENG.get(self)

    def get_ke(self) -> Optional['Wuxing']:
        """获取当前五行所克的五行"""
        return WUXING_KE.get(self)

    def get_by_sheng(self) -> Optional['Wuxing']:
        """获取生当前五行的五行"""
        return WUXING_SHENG_REVERSE.get(self)

    def get_by_ke(self) -> Optional['Wuxing']:
        """获取克当前五行的五行"""
        return WUXING_KE_REVERSE.get(self)


# 五行相生映射表: 金生水、水生木、木生火、火生土、土生金
WUXING_SHENG: Dict[Wuxing, Wuxing] = {
    Wuxing.JIN: Wuxing.SHUI,
    Wuxing.SHUI: Wuxing.MU,
    Wuxing.MU: Wuxing.HUO,
    Wuxing.HUO: Wuxing.TU,
    Wuxing.TU: Wuxing.JIN,
}

# 五行相生逆向映射（被生）
WUXING_SHENG_REVERSE: Dict[Wuxing, Wuxing] = {v: k for k, v in WUXING_SHENG.items()}

# 五行相克映射表: 金克木、木克土、土克水、水克火、火克金
WUXING_KE: Dict[Wuxing, Wuxing] = {
    Wuxing.JIN: Wuxing.MU,
    Wuxing.MU: Wuxing.TU,
    Wuxing.TU: Wuxing.SHUI,
    Wuxing.SHUI: Wuxing.HUO,
    Wuxing.HUO: Wuxing.JIN,
}

# 五行相克逆向映射（被克）
WUXING_KE_REVERSE: Dict[Wuxing, Wuxing] = {v: k for k, v in WUXING_KE.items()}


# =============================================================================
# 天干系统
# =============================================================================

@unique
class Tiangan(Enum):
    """天干枚举"""
    JIA = "甲"
    YI = "乙"
    BING = "丙"
    DING = "丁"
    WU = "戊"
    JI = "己"
    GENG = "庚"
    XIN = "辛"
    REN = "壬"
    GUI = "癸"

    @property
    def wuxing(self) -> Wuxing:
        """
        获取天干对应的五行

        天干五行:
        - 甲乙 → 木
        - 丙丁 → 火
        - 戊己 → 土
        - 庚辛 → 金
        - 壬癸 → 水
        """
        TIANGAN_WUXING = {
            Tiangan.JIA: Wuxing.MU,
            Tiangan.YI: Wuxing.MU,
            Tiangan.BING: Wuxing.HUO,
            Tiangan.DING: Wuxing.HUO,
            Tiangan.WU: Wuxing.TU,
            Tiangan.JI: Wuxing.TU,
            Tiangan.GENG: Wuxing.JIN,
            Tiangan.XIN: Wuxing.JIN,
            Tiangan.REN: Wuxing.SHUI,
            Tiangan.GUI: Wuxing.SHUI,
        }
        return TIANGAN_WUXING[self]

    @classmethod
    def from_char(cls, char: str) -> Optional['Tiangan']:
        """从字符获取天干枚举"""
        for t in cls:
            if t.value == char:
                return t
        return None


# =============================================================================
# 地支系统
# =============================================================================

@unique
class Dizhi(Enum):
    """地支枚举"""
    ZI = "子"
    CHOU = "丑"
    YIN = "寅"
    MAO = "卯"
    CHEN = "辰"
    SI = "巳"
    WU = "午"
    WEI = "未"
    SHEN = "申"
    YOU = "酉"
    XU = "戌"
    HAI = "亥"

    @property
    def wuxing(self) -> Wuxing:
        """
        获取地支对应的五行

        地支五行:
        - 亥子 → 水
        - 寅卯 → 木
        - 巳午 → 火
        - 申酉 → 金
        - 丑未辰戌 → 土
        """
        DIZHI_WUXING = {
            Dizhi.ZI: Wuxing.SHUI,
            Dizhi.CHOU: Wuxing.TU,
            Dizhi.YIN: Wuxing.MU,
            Dizhi.MAO: Wuxing.MU,
            Dizhi.CHEN: Wuxing.TU,
            Dizhi.SI: Wuxing.HUO,
            Dizhi.WU: Wuxing.HUO,
            Dizhi.WEI: Wuxing.TU,
            Dizhi.SHEN: Wuxing.JIN,
            Dizhi.YOU: Wuxing.JIN,
            Dizhi.XU: Wuxing.TU,
            Dizhi.HAI: Wuxing.SHUI,
        }
        return DIZHI_WUXING[self]

    def is_he(self, other: 'Dizhi') -> bool:
        """
        判断与另一地支是否相合

        地支相合: 子丑合、寅亥合、卯戌合、辰酉合、巳申合、午未合
        """
        return DIZHI_HE.get(self) == other

    def is_chong(self, other: 'Dizhi') -> bool:
        """
        判断与另一地支是否相冲

        地支相冲: 子午冲、丑未冲、寅申冲、卯酉冲、辰戌冲、巳亥冲
        """
        return DIZHI_CHONG.get(self) == other

    def get_he(self) -> Optional['Dizhi']:
        """获取相合的地支"""
        return DIZHI_HE.get(self)

    def get_chong(self) -> Optional['Dizhi']:
        """获取相冲的地支"""
        return DIZHI_CHONG.get(self)

    def is_sanhe(self, other1: 'Dizhi', other2: 'Dizhi') -> bool:
        """
        判断三个地支是否构成三合局

        三合局:
        - 申子辰合水局
        - 亥卯未合木局
        - 寅午戌合火局
        - 巳酉丑合金局
        """
        trio = {self, other1, other2}
        for sanhe_set in DIZHI_SANHE.values():
            if trio == sanhe_set:
                return True
        return False

    def get_sanhe_wuxing(self, others: List['Dizhi']) -> Optional[Wuxing]:
        """
        获取三合局的五行属性

        Args:
            others: 另外两个地支

        Returns:
            如果构成三合局返回对应的五行，否则返回None
        """
        trio = {self}
        for o in others:
            trio.add(o)

        for wuxing, sanhe_set in DIZHI_SANHE.items():
            if trio == sanhe_set:
                return wuxing
        return None

    @classmethod
    def from_char(cls, char: str) -> Optional['Dizhi']:
        """从字符获取地支枚举"""
        for d in cls:
            if d.value == char:
                return d
        return None


# 地支相合映射表
DIZHI_HE: Dict[Dizhi, Dizhi] = {
    Dizhi.ZI: Dizhi.CHOU,
    Dizhi.CHOU: Dizhi.ZI,
    Dizhi.YIN: Dizhi.HAI,
    Dizhi.HAI: Dizhi.YIN,
    Dizhi.MAO: Dizhi.XU,
    Dizhi.XU: Dizhi.MAO,
    Dizhi.CHEN: Dizhi.YOU,
    Dizhi.YOU: Dizhi.CHEN,
    Dizhi.SI: Dizhi.SHEN,
    Dizhi.SHEN: Dizhi.SI,
    Dizhi.WU: Dizhi.WEI,
    Dizhi.WEI: Dizhi.WU,
}

# 地支相冲映射表
DIZHI_CHONG: Dict[Dizhi, Dizhi] = {
    Dizhi.ZI: Dizhi.WU,
    Dizhi.WU: Dizhi.ZI,
    Dizhi.CHOU: Dizhi.WEI,
    Dizhi.WEI: Dizhi.CHOU,
    Dizhi.YIN: Dizhi.SHEN,
    Dizhi.SHEN: Dizhi.YIN,
    Dizhi.MAO: Dizhi.YOU,
    Dizhi.YOU: Dizhi.MAO,
    Dizhi.CHEN: Dizhi.XU,
    Dizhi.XU: Dizhi.CHEN,
    Dizhi.SI: Dizhi.HAI,
    Dizhi.HAI: Dizhi.SI,
}

# 地支三合局映射表
DIZHI_SANHE: Dict[Wuxing, set] = {
    Wuxing.SHUI: {Dizhi.SHEN, Dizhi.ZI, Dizhi.CHEN},  # 申子辰合水局
    Wuxing.MU: {Dizhi.HAI, Dizhi.MAO, Dizhi.WEI},     # 亥卯未合木局
    Wuxing.HUO: {Dizhi.YIN, Dizhi.WU, Dizhi.XU},      # 寅午戌合火局
    Wuxing.JIN: {Dizhi.SI, Dizhi.YOU, Dizhi.CHOU},    # 巳酉丑合金局
}


# =============================================================================
# 单卦系统
# =============================================================================

@unique
class DanGua(Enum):
    """
    八单卦枚举

    单卦代码 (3位二进制，阳爻=1，阴爻=0):
    - 乾: 111 (阳阳阳)
    - 兑: 110 (阳阳阴)
    - 离: 101 (阳阴阳)
    - 震: 100 (阳阴阴)
    - 巽: 011 (阴阳阳)
    - 坎: 010 (阴阳阴)
    - 艮: 001 (阴阴阳)
    - 坤: 000 (阴阴阴)
    """
    QIAN = ("乾", 0b111)   # 乾三连
    DUI = ("兑", 0b110)   # 兑上缺
    LI = ("离", 0b101)    # 离中虚
    ZHEN = ("震", 0b100)  # 震仰盂
    XUN = ("巽", 0b011)   # 巽下断
    KAN = ("坎", 0b010)   # 坎中满
    GEN = ("艮", 0b001)   # 艮覆碗
    KUN = ("坤", 0b000)   # 坤六断

    def __init__(self, name: str, code: int):
        self._name = name
        self._code = code

    @property
    def gua_name(self) -> str:
        """获取卦名"""
        return self._name

    @property
    def code(self) -> int:
        """获取单卦代码 (3位二进制对应的整数)"""
        return self._code

    @property
    def wuxing(self) -> Wuxing:
        """
        获取单卦对应的五行

        单卦五行:
        - 坎 → 水
        - 震、巽 → 木
        - 离 → 火
        - 乾、兑 → 金
        - 坤、艮 → 土
        """
        DANGUA_WUXING = {
            DanGua.QIAN: Wuxing.JIN,
            DanGua.DUI: Wuxing.JIN,
            DanGua.LI: Wuxing.HUO,
            DanGua.ZHEN: Wuxing.MU,
            DanGua.XUN: Wuxing.MU,
            DanGua.KAN: Wuxing.SHUI,
            DanGua.GEN: Wuxing.TU,
            DanGua.KUN: Wuxing.TU,
        }
        return DANGUA_WUXING[self]

    @classmethod
    def from_code(cls, code: int) -> Optional['DanGua']:
        """从代码获取单卦枚举"""
        for gua in cls:
            if gua.code == code:
                return gua
        return None

    @classmethod
    def from_name(cls, name: str) -> Optional['DanGua']:
        """从卦名获取单卦枚举"""
        for gua in cls:
            if gua.gua_name == name:
                return gua
        return None


# =============================================================================
# 重卦系统
# =============================================================================

class ZhongGua(Enum):
    """
    六十四重卦枚举

    重卦代码 (6位二进制):
    - 前3位为内卦代码
    - 后3位为外卦代码

    八宫卦序:
    - 乾宫(金): 乾为天、天风姤、天山遁、天地否、风地观、山地剥、火地晋、火天大有
    - 坎宫(水): 坎为水、水泽节、水雷屯、水火既济、泽火革、雷火丰、地火明夷、地水师
    - 艮宫(土): 艮为山、山火贲、山天大畜、山泽损、火泽睽、天泽履、风泽中孚、风山渐
    - 震宫(木): 震为雷、雷地豫、雷水解、雷风恒、地风升、水风井、泽风大过、泽雷随
    - 巽宫(木): 巽为风、风天小畜、风火家人、风雷益、天雷无妄、火雷噬嗑、山雷颐、山风蛊
    - 离宫(火): 离为火、火山旅、火风鼎、火水未济、山水蒙、风水涣、天水讼、天火同人
    - 坤宫(土): 坤为地、地雷复、地泽临、地天泰、雷天大壮、泽天夬、水天需、水地比
    - 兑宫(金): 兑为泽、泽水困、泽地萃、泽山咸、水山蹇、地山谦、雷山小过、雷泽归妹
    """

    # 乾宫(金)
    QIAN_WEI_TIAN = ("乾为天", 0b111111, DanGua.QIAN, DanGua.QIAN, "乾宫", "本宫", Wuxing.JIN)
    TIAN_FENG_GOU = ("天风姤", 0b011111, DanGua.XUN, DanGua.QIAN, "乾宫", "一世", Wuxing.JIN)
    TIAN_SHAN_DUN = ("天山遁", 0b001111, DanGua.GEN, DanGua.QIAN, "乾宫", "二世", Wuxing.JIN)
    TIAN_DI_FOU = ("天地否", 0b000111, DanGua.KUN, DanGua.QIAN, "乾宫", "三世", Wuxing.JIN)
    FENG_DI_GUAN = ("风地观", 0b000011, DanGua.KUN, DanGua.XUN, "乾宫", "四世", Wuxing.JIN)
    SHAN_DI_BO = ("山地剥", 0b000001, DanGua.KUN, DanGua.GEN, "乾宫", "五世", Wuxing.JIN)
    HUO_DI_JIN = ("火地晋", 0b000101, DanGua.KUN, DanGua.LI, "乾宫", "游魂", Wuxing.JIN)
    HUO_TIAN_DA_YOU = ("火天大有", 0b111101, DanGua.QIAN, DanGua.LI, "乾宫", "归魂", Wuxing.JIN)

    # 坎宫(水)
    KAN_WEI_SHUI = ("坎为水", 0b010010, DanGua.KAN, DanGua.KAN, "坎宫", "本宫", Wuxing.SHUI)
    SHUI_ZE_JIE = ("水泽节", 0b110010, DanGua.DUI, DanGua.KAN, "坎宫", "一世", Wuxing.SHUI)
    SHUI_LEI_TUN = ("水雷屯", 0b100010, DanGua.ZHEN, DanGua.KAN, "坎宫", "二世", Wuxing.SHUI)
    SHUI_HUO_JI_JI = ("水火既济", 0b101010, DanGua.LI, DanGua.KAN, "坎宫", "三世", Wuxing.SHUI)
    ZE_HUO_GE = ("泽火革", 0b101110, DanGua.LI, DanGua.DUI, "坎宫", "四世", Wuxing.SHUI)
    LEI_HUO_FENG = ("雷火丰", 0b101100, DanGua.LI, DanGua.ZHEN, "坎宫", "五世", Wuxing.SHUI)
    DI_HUO_MING_YI = ("地火明夷", 0b101000, DanGua.LI, DanGua.KUN, "坎宫", "游魂", Wuxing.SHUI)
    DI_SHUI_SHI = ("地水师", 0b010000, DanGua.KAN, DanGua.KUN, "坎宫", "归魂", Wuxing.SHUI)

    # 艮宫(土)
    GEN_WEI_SHAN = ("艮为山", 0b001001, DanGua.GEN, DanGua.GEN, "艮宫", "本宫", Wuxing.TU)
    SHAN_HUO_BEN = ("山火贲", 0b101001, DanGua.LI, DanGua.GEN, "艮宫", "一世", Wuxing.TU)
    SHAN_TIAN_DA_XU = ("山天大畜", 0b111001, DanGua.QIAN, DanGua.GEN, "艮宫", "二世", Wuxing.TU)
    SHAN_ZE_SUN = ("山泽损", 0b110001, DanGua.DUI, DanGua.GEN, "艮宫", "三世", Wuxing.TU)
    HUO_ZE_KUI = ("火泽睽", 0b110101, DanGua.DUI, DanGua.LI, "艮宫", "四世", Wuxing.TU)
    TIAN_ZE_LV = ("天泽履", 0b110111, DanGua.DUI, DanGua.QIAN, "艮宫", "五世", Wuxing.TU)
    FENG_ZE_ZHONG_FU = ("风泽中孚", 0b110011, DanGua.DUI, DanGua.XUN, "艮宫", "游魂", Wuxing.TU)
    FENG_SHAN_JIAN = ("风山渐", 0b001011, DanGua.GEN, DanGua.XUN, "艮宫", "归魂", Wuxing.TU)

    # 震宫(木)
    ZHEN_WEI_LEI = ("震为雷", 0b100100, DanGua.ZHEN, DanGua.ZHEN, "震宫", "本宫", Wuxing.MU)
    LEI_DI_YU = ("雷地豫", 0b000100, DanGua.KUN, DanGua.ZHEN, "震宫", "一世", Wuxing.MU)
    LEI_SHUI_JIE = ("雷水解", 0b010100, DanGua.KAN, DanGua.ZHEN, "震宫", "二世", Wuxing.MU)
    LEI_FENG_HENG = ("雷风恒", 0b011100, DanGua.XUN, DanGua.ZHEN, "震宫", "三世", Wuxing.MU)
    DI_FENG_SHENG = ("地风升", 0b011000, DanGua.XUN, DanGua.KUN, "震宫", "四世", Wuxing.MU)
    SHUI_FENG_JING = ("水风井", 0b011010, DanGua.XUN, DanGua.KAN, "震宫", "五世", Wuxing.MU)
    ZE_FENG_DA_GUO = ("泽风大过", 0b011110, DanGua.XUN, DanGua.DUI, "震宫", "游魂", Wuxing.MU)
    ZE_LEI_SUI = ("泽雷随", 0b100110, DanGua.ZHEN, DanGua.DUI, "震宫", "归魂", Wuxing.MU)

    # 巽宫(木)
    XUN_WEI_FENG = ("巽为风", 0b011011, DanGua.XUN, DanGua.XUN, "巽宫", "本宫", Wuxing.MU)
    FENG_TIAN_XIAO_XU = ("风天小畜", 0b111011, DanGua.QIAN, DanGua.XUN, "巽宫", "一世", Wuxing.MU)
    FENG_HUO_JIA_REN = ("风火家人", 0b101011, DanGua.LI, DanGua.XUN, "巽宫", "二世", Wuxing.MU)
    FENG_LEI_YI = ("风雷益", 0b100011, DanGua.ZHEN, DanGua.XUN, "巽宫", "三世", Wuxing.MU)
    TIAN_LEI_WU_WANG = ("天雷无妄", 0b100111, DanGua.ZHEN, DanGua.QIAN, "巽宫", "四世", Wuxing.MU)
    HUO_LEI_SHI_KE = ("火雷噬嗑", 0b100101, DanGua.ZHEN, DanGua.LI, "巽宫", "五世", Wuxing.MU)
    SHAN_LEI_YI = ("山雷颐", 0b100001, DanGua.ZHEN, DanGua.GEN, "巽宫", "游魂", Wuxing.MU)
    SHAN_FENG_GU = ("山风蛊", 0b011001, DanGua.XUN, DanGua.GEN, "巽宫", "归魂", Wuxing.MU)

    # 离宫(火)
    LI_WEI_HUO = ("离为火", 0b101101, DanGua.LI, DanGua.LI, "离宫", "本宫", Wuxing.HUO)
    HUO_SHAN_LV = ("火山旅", 0b001101, DanGua.GEN, DanGua.LI, "离宫", "一世", Wuxing.HUO)
    HUO_FENG_DING = ("火风鼎", 0b011101, DanGua.XUN, DanGua.LI, "离宫", "二世", Wuxing.HUO)
    HUO_SHUI_WEI_JI = ("火水未济", 0b010101, DanGua.KAN, DanGua.LI, "离宫", "三世", Wuxing.HUO)
    SHAN_SHUI_MENG = ("山水蒙", 0b010001, DanGua.KAN, DanGua.GEN, "离宫", "四世", Wuxing.HUO)
    FENG_SHUI_HUAN = ("风水涣", 0b010011, DanGua.KAN, DanGua.XUN, "离宫", "五世", Wuxing.HUO)
    TIAN_SHUI_SONG = ("天水讼", 0b010111, DanGua.KAN, DanGua.QIAN, "离宫", "游魂", Wuxing.HUO)
    TIAN_HUO_TONG_REN = ("天火同人", 0b101111, DanGua.LI, DanGua.QIAN, "离宫", "归魂", Wuxing.HUO)

    # 坤宫(土)
    KUN_WEI_DI = ("坤为地", 0b000000, DanGua.KUN, DanGua.KUN, "坤宫", "本宫", Wuxing.TU)
    DI_LEI_FU = ("地雷复", 0b100000, DanGua.ZHEN, DanGua.KUN, "坤宫", "一世", Wuxing.TU)
    DI_ZE_LIN = ("地泽临", 0b110000, DanGua.DUI, DanGua.KUN, "坤宫", "二世", Wuxing.TU)
    DI_TIAN_TAI = ("地天泰", 0b111000, DanGua.QIAN, DanGua.KUN, "坤宫", "三世", Wuxing.TU)
    LEI_TIAN_DA_ZHUANG = ("雷天大壮", 0b111100, DanGua.QIAN, DanGua.ZHEN, "坤宫", "四世", Wuxing.TU)
    ZE_TIAN_GUAI = ("泽天夬", 0b111110, DanGua.QIAN, DanGua.DUI, "坤宫", "五世", Wuxing.TU)
    SHUI_TIAN_XU = ("水天需", 0b111010, DanGua.QIAN, DanGua.KAN, "坤宫", "游魂", Wuxing.TU)
    SHUI_DI_BI = ("水地比", 0b000010, DanGua.KUN, DanGua.KAN, "坤宫", "归魂", Wuxing.TU)

    # 兑宫(金)
    DUI_WEI_ZE = ("兑为泽", 0b110110, DanGua.DUI, DanGua.DUI, "兑宫", "本宫", Wuxing.JIN)
    ZE_SHUI_KUN = ("泽水困", 0b010110, DanGua.KAN, DanGua.DUI, "兑宫", "一世", Wuxing.JIN)
    ZE_DI_CUI = ("泽地萃", 0b000110, DanGua.KUN, DanGua.DUI, "兑宫", "二世", Wuxing.JIN)
    ZE_SHAN_XIAN = ("泽山咸", 0b001110, DanGua.GEN, DanGua.DUI, "兑宫", "三世", Wuxing.JIN)
    SHUI_SHAN_JIAN = ("水山蹇", 0b001010, DanGua.GEN, DanGua.KAN, "兑宫", "四世", Wuxing.JIN)
    DI_SHAN_QIAN = ("地山谦", 0b001000, DanGua.GEN, DanGua.KUN, "兑宫", "五世", Wuxing.JIN)
    LEI_SHAN_XIAO_GUO = ("雷山小过", 0b001100, DanGua.GEN, DanGua.ZHEN, "兑宫", "游魂", Wuxing.JIN)
    LEI_ZE_GUI_MEI = ("雷泽归妹", 0b110100, DanGua.DUI, DanGua.ZHEN, "兑宫", "归魂", Wuxing.JIN)

    def __init__(self, name: str, code: int, neigua: DanGua, waigua: DanGua,
                 gongwei: str, gongwei_index: str, gongwuxing: Wuxing):
        self._name = name
        self._code = code
        self._neigua = neigua
        self._waigua = waigua
        self._gongwei = gongwei
        self._gongwei_index = gongwei_index
        self._gongwuxing = gongwuxing

    @property
    def gua_name(self) -> str:
        """获取卦名"""
        return self._name

    @property
    def code(self) -> int:
        """获取重卦代码 (6位二进制对应的整数)"""
        return self._code

    @property
    def neigua(self) -> DanGua:
        """获取内卦"""
        return self._neigua

    @property
    def waigua(self) -> DanGua:
        """获取外卦"""
        return self._waigua

    @property
    def gongwei(self) -> str:
        """获取卦宫"""
        return self._gongwei

    @property
    def gongwei_index(self) -> str:
        """获取宫位 (本宫/一世/二世/三世/四世/五世/游魂/归魂)"""
        return self._gongwei_index

    @property
    def gongwuxing(self) -> Wuxing:
        """获取卦宫五行"""
        return self._gongwuxing

    @property
    def is_liuchong(self) -> bool:
        """
        判断是否为六冲卦

        六冲卦(10个): 乾为天、震为雷、坎为水、艮为山、坤为地、巽为风、离为火、兑为泽、雷天大壮、天雷无妄
        """
        liuchong_guas = {
            self.QIAN_WEI_TIAN, self.ZHEN_WEI_LEI, self.KAN_WEI_SHUI,
            self.GEN_WEI_SHAN, self.KUN_WEI_DI, self.XUN_WEI_FENG,
            self.LI_WEI_HUO, self.DUI_WEI_ZE,
            self.LEI_TIAN_DA_ZHUANG, self.TIAN_LEI_WU_WANG
        }
        return self in liuchong_guas

    @property
    def is_liuhe(self) -> bool:
        """
        判断是否为六合卦

        六合卦(8个): 天地否、水雷屯、火山旅、泽火革、地天泰、雷水解、山火贲、风泽中孚
        """
        liuhe_guas = {
            self.TIAN_DI_FOU, self.SHUI_LEI_TUN, self.HUO_SHAN_LV,
            self.ZE_HUO_GE, self.DI_TIAN_TAI, self.LEI_SHUI_JIE,
            self.SHAN_HUO_BEN, self.FENG_ZE_ZHONG_FU
        }
        return self in liuhe_guas

    @classmethod
    def from_code(cls, code: int) -> Optional['ZhongGua']:
        """从代码获取重卦枚举"""
        for gua in cls:
            if gua.code == code:
                return gua
        return None

    @classmethod
    def from_name(cls, name: str) -> Optional['ZhongGua']:
        """从卦名获取重卦枚举"""
        for gua in cls:
            if gua.gua_name == name:
                return gua
        return None

    @staticmethod
    def parse_code_to_neigua_waigua(code: int) -> Tuple[DanGua, DanGua]:
        """
        从重卦代码解析出内卦和外卦

        重卦代码结构：
        - 高3位(bit3-5)：内卦代码
        - 低3位(bit0-2)：外卦代码

        例如：乾为天(111111) = 内卦乾(111) + 外卦乾(111)

        Args:
            code: 重卦代码 (6位二进制对应的整数)

        Returns:
            (内卦, 外卦) 元组
        """
        # 高3位为内卦，低3位为外卦
        neigua_code = (code >> 3) & 0b111  # 取高3位作为内卦
        waigua_code = code & 0b111  # 取低3位作为外卦

        neigua = DanGua.from_code(neigua_code)
        waigua = DanGua.from_code(waigua_code)

        return neigua, waigua


# =============================================================================
# 六亲系统
# =============================================================================

@unique
class LiuQin(Enum):
    """
    六亲枚举

    六亲根据卦宫五行与爻地支五行的生克关系确定:
    - 爻地支五行生卦宫五行 → 父母
    - 爻地支五行克卦宫五行 → 官鬼
    - 卦宫五行生爻地支五行 → 子孙
    - 卦宫五行克爻地支五行 → 妻财
    - 卦宫五行 = 爻地支五行 → 兄弟
    """
    FU_MU = "父母"
    GUAN_GUI = "官鬼"
    ZI_SUN = "子孙"
    QI_CAI = "妻财"
    XIONG_DI = "兄弟"

    @classmethod
    def calculate(cls, gongwuxing: Wuxing, yaowuxing: Wuxing) -> 'LiuQin':
        """
        根据卦宫五行和爻地支五行计算六亲

        Args:
            gongwuxing: 卦宫五行
            yaowuxing: 爻地支五行

        Returns:
            对应的六亲
        """
        if gongwuxing == yaowuxing:
            return cls.XIONG_DI  # 兄弟
        elif gongwuxing.generates(yaowuxing):
            return cls.ZI_SUN   # 子孙
        elif gongwuxing.overcomes(yaowuxing):
            return cls.QI_CAI   # 妻财
        elif yaowuxing.generates(gongwuxing):
            return cls.FU_MU    # 父母
        elif yaowuxing.overcomes(gongwuxing):
            return cls.GUAN_GUI # 官鬼
        else:
            raise ValueError(f"无法计算六亲: 卦宫五行={gongwuxing}, 爻五行={yaowuxing}")


# =============================================================================
# 六神系统
# =============================================================================

@unique
class LiuShen(Enum):
    """六神枚举"""
    QING_LONG = "青龙"
    ZHU_QUE = "朱雀"
    GOU_CHEN = "勾陈"
    TENG_SHE = "螣蛇"
    BAI_HU = "白虎"
    XUAN_WU = "玄武"

    @classmethod
    def get_by_tiangan_and_position(cls, tiangan: Tiangan, position: int) -> 'LiuShen':
        """
        根据日干和爻位获取六神

        六神排列规则 (按日干):
        - 甲乙日: 初青龙、二朱雀、三勾陈、四螣蛇、五白虎、上玄武
        - 丙丁日: 初朱雀、二勾陈、三螣蛇、四白虎、五玄武、上青龙
        - 戊日: 初勾陈、二螣蛇、三白虎、四玄武、五青龙、上朱雀
        - 己日: 初螣蛇、二白虎、三玄武、四青龙、五朱雀、上勾陈
        - 庚辛日: 初白虎、二玄武、三青龙、四朱雀、五勾陈、上螣蛇
        - 壬癸日: 初玄武、二青龙、三朱雀、四勾陈、五螣蛇、上白虎

        Args:
            tiangan: 日干
            position: 爻位 (1-6: 初爻到上爻)

        Returns:
            对应的六神
        """
        # 六神顺序: 青龙、朱雀、勾陈、螣蛇、白虎、玄武
        base_order = [
            cls.QING_LONG, cls.ZHU_QUE, cls.GOU_CHEN,
            cls.TENG_SHE, cls.BAI_HU, cls.XUAN_WU
        ]

        # 根据日干确定起始偏移
        offset_map = {
            Tiangan.JIA: 0, Tiangan.YI: 0,      # 甲乙日从青龙开始
            Tiangan.BING: 1, Tiangan.DING: 1,   # 丙丁日从朱雀开始
            Tiangan.WU: 2,                       # 戊日从勾陈开始
            Tiangan.JI: 3,                       # 己日从螣蛇开始
            Tiangan.GENG: 4, Tiangan.XIN: 4,    # 庚辛日从白虎开始
            Tiangan.REN: 5, Tiangan.GUI: 5,     # 壬癸日从玄武开始
        }

        offset = offset_map.get(tiangan, 0)
        index = (offset + position - 1) % 6
        return base_order[index]


# =============================================================================
# 神煞系统
# =============================================================================

@unique
class ShenSha(Enum):
    """神煞枚举"""
    GAN_LU = "干禄"
    YI_MA = "驿马"
    YANG_REN = "羊刃"
    TAO_HUA = "桃花"


# 干禄映射表 (按日干)
GANLU_MAP: Dict[Tiangan, Dizhi] = {
    Tiangan.JIA: Dizhi.YIN,
    Tiangan.YI: Dizhi.MAO,
    Tiangan.BING: Dizhi.SI,
    Tiangan.DING: Dizhi.WU,
    Tiangan.WU: Dizhi.SI,
    Tiangan.JI: Dizhi.WU,
    Tiangan.GENG: Dizhi.SHEN,
    Tiangan.XIN: Dizhi.YOU,
    Tiangan.REN: Dizhi.HAI,
    Tiangan.GUI: Dizhi.ZI,
}


# 驿马映射表 (按日支)
YIMA_MAP: Dict[Dizhi, Dizhi] = {
    Dizhi.SHEN: Dizhi.YIN,
    Dizhi.ZI: Dizhi.YIN,
    Dizhi.CHEN: Dizhi.YIN,   # 申子辰日，驿马在寅
    Dizhi.HAI: Dizhi.SI,
    Dizhi.MAO: Dizhi.SI,
    Dizhi.WEI: Dizhi.SI,     # 亥卯未日，驿马在巳
    Dizhi.YIN: Dizhi.SHEN,
    Dizhi.WU: Dizhi.SHEN,
    Dizhi.XU: Dizhi.SHEN,    # 寅午戌日，驿马在申
    Dizhi.SI: Dizhi.HAI,
    Dizhi.YOU: Dizhi.HAI,
    Dizhi.CHOU: Dizhi.HAI,   # 巳酉丑日，驿马在亥
}


# 羊刃映射表 (按日干)
YANGREN_MAP: Dict[Tiangan, Dizhi] = {
    Tiangan.JIA: Dizhi.MAO,
    Tiangan.YI: Dizhi.YIN,
    Tiangan.BING: Dizhi.WU,
    Tiangan.DING: Dizhi.SI,
    Tiangan.WU: Dizhi.WU,
    Tiangan.JI: Dizhi.SI,
    Tiangan.GENG: Dizhi.YOU,
    Tiangan.XIN: Dizhi.SHEN,
    Tiangan.REN: Dizhi.ZI,
    Tiangan.GUI: Dizhi.HAI,
}


# 桃花映射表 (按日支)
TAOHUA_MAP: Dict[Dizhi, Dizhi] = {
    Dizhi.SHEN: Dizhi.YOU,
    Dizhi.ZI: Dizhi.YOU,
    Dizhi.CHEN: Dizhi.YOU,   # 申子辰日，桃花在酉
    Dizhi.HAI: Dizhi.ZI,
    Dizhi.MAO: Dizhi.ZI,
    Dizhi.WEI: Dizhi.ZI,     # 亥卯未日，桃花在子
    Dizhi.YIN: Dizhi.MAO,
    Dizhi.WU: Dizhi.MAO,
    Dizhi.XU: Dizhi.MAO,     # 寅午戌日，桃花在卯
    Dizhi.SI: Dizhi.WU,
    Dizhi.YOU: Dizhi.WU,
    Dizhi.CHOU: Dizhi.WU,    # 巳酉丑日，桃花在午
}


def get_ganlu(tiangan: Tiangan) -> Dizhi:
    """获取干禄地支"""
    return GANLU_MAP[tiangan]


def get_yima(dizhi: Dizhi) -> Dizhi:
    """获取驿马地支"""
    return YIMA_MAP[dizhi]


def get_yangren(tiangan: Tiangan) -> Dizhi:
    """获取羊刃地支"""
    return YANGREN_MAP[tiangan]


def get_taohua(dizhi: Dizhi) -> Dizhi:
    """获取桃花地支"""
    return TAOHUA_MAP[dizhi]


def get_shensha_with_chonghe(dizhi: Dizhi) -> List[Dizhi]:
    """
    获取带神煞的地支列表（包含相冲、相合的地支）

    神煞传播规则: 若地支A是神煞，则与A相冲、相合的地支也"带神煞"

    Args:
        dizhi: 神煞地支

    Returns:
        包含该地支及其相冲、相合地支的列表
    """
    result = [dizhi]

    # 添加相合的地支
    he = dizhi.get_he()
    if he:
        result.append(he)

    # 添加相冲的地支
    chong = dizhi.get_chong()
    if chong:
        result.append(chong)

    return result


# =============================================================================
# 世应定位
# =============================================================================

# 宫位到世应爻位的映射表
SHI_YING_MAP: Dict[str, Tuple[int, int]] = {
    "本宫": (6, 3),  # 世在上爻，应在三爻
    "一世": (1, 4),  # 世在初爻，应在四爻
    "二世": (2, 5),  # 世在二爻，应在五爻
    "三世": (3, 6),  # 世在三爻，应在上爻
    "四世": (4, 1),  # 世在四爻，应在初爻
    "五世": (5, 2),  # 世在五爻，应在二爻
    "游魂": (4, 1),  # 世在四爻，应在初爻
    "归魂": (3, 6),  # 世在三爻，应在上爻
}


def get_shiying_by_gongwei(gongwei_index: str) -> Tuple[int, int]:
    """
    根据宫位获取世爻和应爻的爻位

    Args:
        gongwei_index: 宫位 (本宫/一世/二世/三世/四世/五世/游魂/归魂)

    Returns:
        (世爻位, 应爻位) 元组，爻位从1到6
    """
    return SHI_YING_MAP.get(gongwei_index, (0, 0))
