"""
六爻卦例分析系统 - 核心枚举测试

测试所有枚举类的定义和方法
"""
import pytest
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.core.enums import (
    Wuxing, WUXING_SHENG, WUXING_KE,
    Tiangan, Dizhi, DIZHI_HE, DIZHI_CHONG, DIZHI_SANHE,
    DanGua, ZhongGua, LiuQin, LiuShen, ShenSha,
    GANLU_MAP, YIMA_MAP, YANGREN_MAP, TAOHUA_MAP,
    get_ganlu, get_yima, get_yangren, get_taohua,
    get_shensha_with_chonghe, get_shiying_by_gongwei, SHI_YING_MAP
)


# =============================================================================
# 任务 1.1 - 五行枚举测试
# =============================================================================

class TestWuxing:
    """五行枚举测试"""

    def test_wuxing_values(self):
        """测试五行枚举值"""
        assert Wuxing.MU.value == "木"
        assert Wuxing.HUO.value == "火"
        assert Wuxing.TU.value == "土"
        assert Wuxing.JIN.value == "金"
        assert Wuxing.SHUI.value == "水"

    def test_wuxing_generates(self):
        """测试五行相生关系"""
        # 金生水
        assert Wuxing.JIN.generates(Wuxing.SHUI) == True
        assert Wuxing.JIN.generates(Wuxing.MU) == False

        # 水生木
        assert Wuxing.SHUI.generates(Wuxing.MU) == True
        assert Wuxing.SHUI.generates(Wuxing.HUO) == False

        # 木生火
        assert Wuxing.MU.generates(Wuxing.HUO) == True
        assert Wuxing.MU.generates(Wuxing.TU) == False

        # 火生土
        assert Wuxing.HUO.generates(Wuxing.TU) == True
        assert Wuxing.HUO.generates(Wuxing.JIN) == False

        # 土生金
        assert Wuxing.TU.generates(Wuxing.JIN) == True
        assert Wuxing.TU.generates(Wuxing.SHUI) == False

    def test_wuxing_overcomes(self):
        """测试五行相克关系"""
        # 金克木
        assert Wuxing.JIN.overcomes(Wuxing.MU) == True
        assert Wuxing.JIN.overcomes(Wuxing.SHUI) == False

        # 木克土
        assert Wuxing.MU.overcomes(Wuxing.TU) == True
        assert Wuxing.MU.overcomes(Wuxing.HUO) == False

        # 土克水
        assert Wuxing.TU.overcomes(Wuxing.SHUI) == True
        assert Wuxing.TU.overcomes(Wuxing.JIN) == False

        # 水克火
        assert Wuxing.SHUI.overcomes(Wuxing.HUO) == True
        assert Wuxing.SHUI.overcomes(Wuxing.MU) == False

        # 火克金
        assert Wuxing.HUO.overcomes(Wuxing.JIN) == True
        assert Wuxing.HUO.overcomes(Wuxing.TU) == False

    def test_wuxing_maps(self):
        """测试五行映射表"""
        assert WUXING_SHENG[Wuxing.JIN] == Wuxing.SHUI
        assert WUXING_KE[Wuxing.JIN] == Wuxing.MU


# =============================================================================
# 任务 1.2 - 天干枚举测试
# =============================================================================

class TestTiangan:
    """天干枚举测试"""

    def test_tiangan_values(self):
        """测试天干枚举值"""
        assert Tiangan.JIA.value == "甲"
        assert Tiangan.YI.value == "乙"
        assert Tiangan.BING.value == "丙"
        assert Tiangan.DING.value == "丁"
        assert Tiangan.WU.value == "戊"
        assert Tiangan.JI.value == "己"
        assert Tiangan.GENG.value == "庚"
        assert Tiangan.XIN.value == "辛"
        assert Tiangan.REN.value == "壬"
        assert Tiangan.GUI.value == "癸"

    def test_tiangan_wuxing(self):
        """测试天干五行属性"""
        # 甲乙属木
        assert Tiangan.JIA.wuxing == Wuxing.MU
        assert Tiangan.YI.wuxing == Wuxing.MU

        # 丙丁属火
        assert Tiangan.BING.wuxing == Wuxing.HUO
        assert Tiangan.DING.wuxing == Wuxing.HUO

        # 戊己属土
        assert Tiangan.WU.wuxing == Wuxing.TU
        assert Tiangan.JI.wuxing == Wuxing.TU

        # 庚辛属金
        assert Tiangan.GENG.wuxing == Wuxing.JIN
        assert Tiangan.XIN.wuxing == Wuxing.JIN

        # 壬癸属水
        assert Tiangan.REN.wuxing == Wuxing.SHUI
        assert Tiangan.GUI.wuxing == Wuxing.SHUI

    def test_tiangan_from_char(self):
        """测试从字符获取天干"""
        assert Tiangan.from_char("甲") == Tiangan.JIA
        assert Tiangan.from_char("癸") == Tiangan.GUI
        assert Tiangan.from_char("X") is None


# =============================================================================
# 任务 1.3 - 地支枚举测试
# =============================================================================

class TestDizhi:
    """地支枚举测试"""

    def test_dizhi_values(self):
        """测试地支枚举值"""
        dizhi_names = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
        for i, name in enumerate(dizhi_names):
            assert list(Dizhi)[i].value == name

    def test_dizhi_wuxing(self):
        """测试地支五行属性"""
        # 亥子属水
        assert Dizhi.HAI.wuxing == Wuxing.SHUI
        assert Dizhi.ZI.wuxing == Wuxing.SHUI

        # 寅卯属木
        assert Dizhi.YIN.wuxing == Wuxing.MU
        assert Dizhi.MAO.wuxing == Wuxing.MU

        # 巳午属火
        assert Dizhi.SI.wuxing == Wuxing.HUO
        assert Dizhi.WU.wuxing == Wuxing.HUO

        # 申酉属金
        assert Dizhi.SHEN.wuxing == Wuxing.JIN
        assert Dizhi.YOU.wuxing == Wuxing.JIN

        # 丑未辰戌属土
        assert Dizhi.CHOU.wuxing == Wuxing.TU
        assert Dizhi.WEI.wuxing == Wuxing.TU
        assert Dizhi.CHEN.wuxing == Wuxing.TU
        assert Dizhi.XU.wuxing == Wuxing.TU


# =============================================================================
# 任务 1.4 - 地支相合测试
# =============================================================================

class TestDizhiHe:
    """地支相合关系测试"""

    def test_dizhi_he(self):
        """测试地支相合关系"""
        # 子丑合
        assert Dizhi.ZI.is_he(Dizhi.CHOU) == True
        assert Dizhi.CHOU.is_he(Dizhi.ZI) == True

        # 寅亥合
        assert Dizhi.YIN.is_he(Dizhi.HAI) == True
        assert Dizhi.HAI.is_he(Dizhi.YIN) == True

        # 卯戌合
        assert Dizhi.MAO.is_he(Dizhi.XU) == True
        assert Dizhi.XU.is_he(Dizhi.MAO) == True

        # 辰酉合
        assert Dizhi.CHEN.is_he(Dizhi.YOU) == True
        assert Dizhi.YOU.is_he(Dizhi.CHEN) == True

        # 巳申合
        assert Dizhi.SI.is_he(Dizhi.SHEN) == True
        assert Dizhi.SHEN.is_he(Dizhi.SI) == True

        # 午未合
        assert Dizhi.WU.is_he(Dizhi.WEI) == True
        assert Dizhi.WEI.is_he(Dizhi.WU) == True

    def test_dizhi_not_he(self):
        """测试不相合的地支"""
        assert Dizhi.ZI.is_he(Dizhi.WU) == False  # 子午不相合
        assert Dizhi.YIN.is_he(Dizhi.MAO) == False


# =============================================================================
# 任务 1.5 - 地支相冲测试
# =============================================================================

class TestDizhiChong:
    """地支相冲关系测试"""

    def test_dizhi_chong(self):
        """测试地支相冲关系"""
        # 子午冲
        assert Dizhi.ZI.is_chong(Dizhi.WU) == True
        assert Dizhi.WU.is_chong(Dizhi.ZI) == True

        # 丑未冲
        assert Dizhi.CHOU.is_chong(Dizhi.WEI) == True
        assert Dizhi.WEI.is_chong(Dizhi.CHOU) == True

        # 寅申冲
        assert Dizhi.YIN.is_chong(Dizhi.SHEN) == True
        assert Dizhi.SHEN.is_chong(Dizhi.YIN) == True

        # 卯酉冲
        assert Dizhi.MAO.is_chong(Dizhi.YOU) == True
        assert Dizhi.YOU.is_chong(Dizhi.MAO) == True

        # 辰戌冲
        assert Dizhi.CHEN.is_chong(Dizhi.XU) == True
        assert Dizhi.XU.is_chong(Dizhi.CHEN) == True

        # 巳亥冲
        assert Dizhi.SI.is_chong(Dizhi.HAI) == True
        assert Dizhi.HAI.is_chong(Dizhi.SI) == True

    def test_dizhi_not_chong(self):
        """测试不相冲的地支"""
        assert Dizhi.ZI.is_chong(Dizhi.CHOU) == False  # 子丑不相冲
        assert Dizhi.YIN.is_chong(Dizhi.HAI) == False  # 寅亥相合，不相冲


# =============================================================================
# 任务 1.6 - 地支三合局测试
# =============================================================================

class TestDizhiSanhe:
    """地支三合局测试"""

    def test_dizhi_sanhe(self):
        """测试三合局判断"""
        # 申子辰合水局
        assert Dizhi.SHEN.is_sanhe(Dizhi.ZI, Dizhi.CHEN) == True
        assert Dizhi.ZI.is_sanhe(Dizhi.SHEN, Dizhi.CHEN) == True
        assert Dizhi.CHEN.is_sanhe(Dizhi.SHEN, Dizhi.ZI) == True

        # 亥卯未合木局
        assert Dizhi.HAI.is_sanhe(Dizhi.MAO, Dizhi.WEI) == True

        # 寅午戌合火局
        assert Dizhi.YIN.is_sanhe(Dizhi.WU, Dizhi.XU) == True

        # 巳酉丑合金局
        assert Dizhi.SI.is_sanhe(Dizhi.YOU, Dizhi.CHOU) == True

    def test_dizhi_sanhe_wuxing(self):
        """测试三合局五行"""
        # 申子辰合水局
        assert Dizhi.SHEN.get_sanhe_wuxing([Dizhi.ZI, Dizhi.CHEN]) == Wuxing.SHUI

        # 亥卯未合木局
        assert Dizhi.HAI.get_sanhe_wuxing([Dizhi.MAO, Dizhi.WEI]) == Wuxing.MU

        # 寅午戌合火局
        assert Dizhi.YIN.get_sanhe_wuxing([Dizhi.WU, Dizhi.XU]) == Wuxing.HUO

        # 巳酉丑合金局
        assert Dizhi.SI.get_sanhe_wuxing([Dizhi.YOU, Dizhi.CHOU]) == Wuxing.JIN

    def test_dizhi_not_sanhe(self):
        """测试非三合局"""
        assert Dizhi.ZI.is_sanhe(Dizhi.CHOU, Dizhi.YIN) == False


# =============================================================================
# 任务 1.7 - 单卦枚举测试
# =============================================================================

class TestDanGua:
    """单卦枚举测试"""

    def test_dangua_code(self):
        """测试单卦代码"""
        assert DanGua.QIAN.code == 0b111  # 乾111
        assert DanGua.DUI.code == 0b110   # 兑110
        assert DanGua.LI.code == 0b101    # 离101
        assert DanGua.ZHEN.code == 0b100  # 震100
        assert DanGua.XUN.code == 0b011   # 巽011
        assert DanGua.KAN.code == 0b010   # 坎010
        assert DanGua.GEN.code == 0b001   # 艮001
        assert DanGua.KUN.code == 0b000   # 坤000

    def test_dangua_wuxing(self):
        """测试单卦五行"""
        # 坎属水
        assert DanGua.KAN.wuxing == Wuxing.SHUI

        # 震巽属木
        assert DanGua.ZHEN.wuxing == Wuxing.MU
        assert DanGua.XUN.wuxing == Wuxing.MU

        # 离属火
        assert DanGua.LI.wuxing == Wuxing.HUO

        # 乾兑属金
        assert DanGua.QIAN.wuxing == Wuxing.JIN
        assert DanGua.DUI.wuxing == Wuxing.JIN

        # 坤艮属土
        assert DanGua.KUN.wuxing == Wuxing.TU
        assert DanGua.GEN.wuxing == Wuxing.TU

    def test_dangua_from_code(self):
        """测试从代码获取单卦"""
        assert DanGua.from_code(0b111) == DanGua.QIAN
        assert DanGua.from_code(0b000) == DanGua.KUN
        assert DanGua.from_code(0b1000) is None  # 超出3位范围

    def test_dangua_from_name(self):
        """测试从卦名获取单卦"""
        assert DanGua.from_name("乾") == DanGua.QIAN
        assert DanGua.from_name("坤") == DanGua.KUN
        assert DanGua.from_name("XXX") is None


# =============================================================================
# 任务 1.8 - 重卦枚举测试
# =============================================================================

class TestZhongGua:
    """重卦枚举测试"""

    def test_zhonggua_count(self):
        """测试重卦数量"""
        assert len(list(ZhongGua)) == 64

    def test_zhonggua_qian(self):
        """测试乾为天"""
        gua = ZhongGua.QIAN_WEI_TIAN
        assert gua.code == 0b111111
        assert gua.gua_name == "乾为天"
        assert gua.neigua == DanGua.QIAN
        assert gua.waigua == DanGua.QIAN
        assert gua.gongwei == "乾宫"
        assert gua.gongwei_index == "本宫"
        assert gua.gongwuxing == Wuxing.JIN

    def test_zhonggua_kun(self):
        """测试坤为地"""
        gua = ZhongGua.KUN_WEI_DI
        assert gua.code == 0b000000
        assert gua.gua_name == "坤为地"
        assert gua.neigua == DanGua.KUN
        assert gua.waigua == DanGua.KUN
        assert gua.gongwei == "坤宫"
        assert gua.gongwei_index == "本宫"
        assert gua.gongwuxing == Wuxing.TU

    def test_zhonggua_shan_feng_gu(self):
        """测试山风蛊"""
        gua = ZhongGua.SHAN_FENG_GU
        assert gua.gua_name == "山风蛊"
        assert gua.code == 0b011001
        assert gua.neigua == DanGua.XUN
        assert gua.waigua == DanGua.GEN

    def test_zhonggua_liuchong(self):
        """测试六冲卦"""
        # 乾为天是六冲卦
        assert ZhongGua.QIAN_WEI_TIAN.is_liuchong == True
        # 坤为地是六冲卦
        assert ZhongGua.KUN_WEI_DI.is_liuchong == True
        # 雷天大壮是六冲卦
        assert ZhongGua.LEI_TIAN_DA_ZHUANG.is_liuchong == True
        # 天风姤不是六冲卦
        assert ZhongGua.TIAN_FENG_GOU.is_liuchong == False

    def test_zhonggua_liuhe(self):
        """测试六合卦"""
        # 天地否是六合卦
        assert ZhongGua.TIAN_DI_FOU.is_liuhe == True
        # 地天泰是六合卦
        assert ZhongGua.DI_TIAN_TAI.is_liuhe == True
        # 风泽中孚是六合卦
        assert ZhongGua.FENG_ZE_ZHONG_FU.is_liuhe == True
        # 乾为天不是六合卦
        assert ZhongGua.QIAN_WEI_TIAN.is_liuhe == False


# =============================================================================
# 任务 1.9 - 重卦代码解析测试
# =============================================================================

class TestZhongGuaParse:
    """重卦代码解析测试"""

    def test_from_code(self):
        """测试从代码获取重卦"""
        gua = ZhongGua.from_code(0b111111)
        assert gua == ZhongGua.QIAN_WEI_TIAN

        gua = ZhongGua.from_code(0b000000)
        assert gua == ZhongGua.KUN_WEI_DI

    def test_from_name(self):
        """测试从卦名获取重卦"""
        gua = ZhongGua.from_name("乾为天")
        assert gua == ZhongGua.QIAN_WEI_TIAN

        gua = ZhongGua.from_name("山风蛊")
        assert gua == ZhongGua.SHAN_FENG_GU

        gua = ZhongGua.from_name("不存在的卦")
        assert gua is None

    def test_parse_code_to_neigua_waigua(self):
        """测试从代码解析内外卦"""
        # 乾为天: 111111
        neigua, waigua = ZhongGua.parse_code_to_neigua_waigua(0b111111)
        assert neigua == DanGua.QIAN
        assert waigua == DanGua.QIAN

        # 山风蛊: 011001
        neigua, waigua = ZhongGua.parse_code_to_neigua_waigua(0b011001)
        assert neigua == DanGua.XUN
        assert waigua == DanGua.GEN


# =============================================================================
# 任务 1.10 - 六亲枚举测试
# =============================================================================

class TestLiuQin:
    """六亲枚举测试"""

    def test_liuqin_values(self):
        """测试六亲枚举值"""
        assert LiuQin.FU_MU.value == "父母"
        assert LiuQin.GUAN_GUI.value == "官鬼"
        assert LiuQin.ZI_SUN.value == "子孙"
        assert LiuQin.QI_CAI.value == "妻财"
        assert LiuQin.XIONG_DI.value == "兄弟"

    def test_liuqin_calculate(self):
        """测试六亲计算"""
        # 卦宫五行=金
        gongwuxing = Wuxing.JIN

        # 爻地支五行=水，金生水 → 子孙
        assert LiuQin.calculate(gongwuxing, Wuxing.SHUI) == LiuQin.ZI_SUN

        # 爻地支五行=木，金克木 → 妻财
        assert LiuQin.calculate(gongwuxing, Wuxing.MU) == LiuQin.QI_CAI

        # 爻地支五行=火，火克金 → 官鬼
        assert LiuQin.calculate(gongwuxing, Wuxing.HUO) == LiuQin.GUAN_GUI

        # 爻地支五行=土，土生金 → 父母
        assert LiuQin.calculate(gongwuxing, Wuxing.TU) == LiuQin.FU_MU

        # 爻地支五行=金，金=金 → 兄弟
        assert LiuQin.calculate(gongwuxing, Wuxing.JIN) == LiuQin.XIONG_DI


# =============================================================================
# 任务 1.11 - 六神枚举测试
# =============================================================================

class TestLiuShen:
    """六神枚举测试"""

    def test_liushen_values(self):
        """测试六神枚举值"""
        assert LiuShen.QING_LONG.value == "青龙"
        assert LiuShen.ZHU_QUE.value == "朱雀"
        assert LiuShen.GOU_CHEN.value == "勾陈"
        assert LiuShen.TENG_SHE.value == "螣蛇"
        assert LiuShen.BAI_HU.value == "白虎"
        assert LiuShen.XUAN_WU.value == "玄武"

    def test_liushen_by_tiangan_jia(self):
        """测试甲乙日六神"""
        # 甲乙日: 初青龙、二朱雀、三勾陈、四螣蛇、五白虎、上玄武
        assert LiuShen.get_by_tiangan_and_position(Tiangan.JIA, 1) == LiuShen.QING_LONG
        assert LiuShen.get_by_tiangan_and_position(Tiangan.JIA, 2) == LiuShen.ZHU_QUE
        assert LiuShen.get_by_tiangan_and_position(Tiangan.JIA, 3) == LiuShen.GOU_CHEN
        assert LiuShen.get_by_tiangan_and_position(Tiangan.JIA, 4) == LiuShen.TENG_SHE
        assert LiuShen.get_by_tiangan_and_position(Tiangan.JIA, 5) == LiuShen.BAI_HU
        assert LiuShen.get_by_tiangan_and_position(Tiangan.JIA, 6) == LiuShen.XUAN_WU

    def test_liushen_by_tiangan_bing(self):
        """测试丙丁日六神"""
        # 丙丁日: 初朱雀、二勾陈、三螣蛇、四白虎、五玄武、上青龙
        assert LiuShen.get_by_tiangan_and_position(Tiangan.BING, 1) == LiuShen.ZHU_QUE
        assert LiuShen.get_by_tiangan_and_position(Tiangan.BING, 6) == LiuShen.QING_LONG

    def test_liushen_by_tiangan_geng(self):
        """测试庚辛日六神"""
        # 庚辛日: 初白虎、二玄武、三青龙、四朱雀、五勾陈、上螣蛇
        assert LiuShen.get_by_tiangan_and_position(Tiangan.GENG, 1) == LiuShen.BAI_HU
        assert LiuShen.get_by_tiangan_and_position(Tiangan.GENG, 3) == LiuShen.QING_LONG


# =============================================================================
# 任务 1.12 - 神煞枚举测试
# =============================================================================

class TestShenSha:
    """神煞枚举测试"""

    def test_shensha_values(self):
        """测试神煞枚举值"""
        assert ShenSha.GAN_LU.value == "干禄"
        assert ShenSha.YI_MA.value == "驿马"
        assert ShenSha.YANG_REN.value == "羊刃"
        assert ShenSha.TAO_HUA.value == "桃花"

    def test_ganlu(self):
        """测试干禄"""
        # 甲禄在寅
        assert get_ganlu(Tiangan.JIA) == Dizhi.YIN
        # 乙禄在卯
        assert get_ganlu(Tiangan.YI) == Dizhi.MAO
        # 丙戊禄在巳
        assert get_ganlu(Tiangan.BING) == Dizhi.SI
        assert get_ganlu(Tiangan.WU) == Dizhi.SI
        # 庚禄在申
        assert get_ganlu(Tiangan.GENG) == Dizhi.SHEN
        # 壬禄在亥
        assert get_ganlu(Tiangan.REN) == Dizhi.HAI

    def test_yima(self):
        """测试驿马"""
        # 申子辰日，驿马在寅
        assert get_yima(Dizhi.SHEN) == Dizhi.YIN
        assert get_yima(Dizhi.ZI) == Dizhi.YIN
        assert get_yima(Dizhi.CHEN) == Dizhi.YIN

        # 亥卯未日，驿马在巳
        assert get_yima(Dizhi.HAI) == Dizhi.SI

        # 寅午戌日，驿马在申
        assert get_yima(Dizhi.YIN) == Dizhi.SHEN

        # 巳酉丑日，驿马在亥
        assert get_yima(Dizhi.SI) == Dizhi.HAI

    def test_yangren(self):
        """测试羊刃"""
        # 甲刃在卯
        assert get_yangren(Tiangan.JIA) == Dizhi.MAO
        # 乙刃在寅
        assert get_yangren(Tiangan.YI) == Dizhi.YIN
        # 庚刃在酉
        assert get_yangren(Tiangan.GENG) == Dizhi.YOU

    def test_taohua(self):
        """测试桃花"""
        # 申子辰日，桃花在酉
        assert get_taohua(Dizhi.SHEN) == Dizhi.YOU
        assert get_taohua(Dizhi.ZI) == Dizhi.YOU
        assert get_taohua(Dizhi.CHEN) == Dizhi.YOU

        # 亥卯未日，桃花在子
        assert get_taohua(Dizhi.HAI) == Dizhi.ZI

        # 寅午戌日，桃花在卯
        assert get_taohua(Dizhi.YIN) == Dizhi.MAO

        # 巳酉丑日，桃花在午
        assert get_taohua(Dizhi.SI) == Dizhi.WU

    def test_shensha_with_chonghe(self):
        """测试神煞传播（冲合）"""
        # 假设子是神煞，则丑（合）、午（冲）也带神煞
        result = get_shensha_with_chonghe(Dizhi.ZI)
        assert Dizhi.ZI in result
        assert Dizhi.CHOU in result   # 子丑合
        assert Dizhi.WU in result     # 子午冲


# =============================================================================
# 世应定位测试
# =============================================================================

class TestShiYing:
    """世应定位测试"""

    def test_shiying_map(self):
        """测试世应映射"""
        # 本宫: 世上，应三
        assert get_shiying_by_gongwei("本宫") == (6, 3)

        # 一世: 世初，应四
        assert get_shiying_by_gongwei("一世") == (1, 4)

        # 游魂: 世四，应初
        assert get_shiying_by_gongwei("游魂") == (4, 1)

        # 归魂: 世三，应上
        assert get_shiying_by_gongwei("归魂") == (3, 6)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
