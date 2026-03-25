"""
六爻卦例分析系统 - 神煞计算模块测试

测试shensha模块的所有功能
"""
import pytest
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.core.enums import Tiangan, Dizhi, ShenSha, ZhongGua
from backend.core.shensha import (
    GANLU_MAP,
    YIMA_MAP,
    YANGREN_MAP,
    TAOHUA_MAP,
    get_ganlu,
    get_yima,
    get_yangren,
    get_taohua,
    get_shensha_with_chonghe,
    calculate_all_shensha,
    get_shensha_type_for_dizhi,
    calculate_shensha_for_guali
)


# =============================================================================
# 任务 10.1 - 干禄计算测试
# =============================================================================

class TestGanLu:
    """干禄计算测试"""

    def test_jia_ganlu(self):
        """测试甲日干禄在寅"""
        assert get_ganlu(Tiangan.JIA) == Dizhi.YIN

    def test_yi_ganlu(self):
        """测试乙日干禄在卯"""
        assert get_ganlu(Tiangan.YI) == Dizhi.MAO

    def test_bing_ganlu(self):
        """测试丙日干禄在巳"""
        assert get_ganlu(Tiangan.BING) == Dizhi.SI

    def test_ding_ganlu(self):
        """测试丁日干禄在午"""
        assert get_ganlu(Tiangan.DING) == Dizhi.WU

    def test_wu_ganlu(self):
        """测试戊日干禄在巳"""
        assert get_ganlu(Tiangan.WU) == Dizhi.SI

    def test_ji_ganlu(self):
        """测试己日干禄在午"""
        assert get_ganlu(Tiangan.JI) == Dizhi.WU

    def test_geng_ganlu(self):
        """测试庚日干禄在申"""
        assert get_ganlu(Tiangan.GENG) == Dizhi.SHEN

    def test_xin_ganlu(self):
        """测试辛日干禄在酉"""
        assert get_ganlu(Tiangan.XIN) == Dizhi.YOU

    def test_ren_ganlu(self):
        """测试壬日干禄在亥"""
        assert get_ganlu(Tiangan.REN) == Dizhi.HAI

    def test_gui_ganlu(self):
        """测试癸日干禄在子"""
        assert get_ganlu(Tiangan.GUI) == Dizhi.ZI

    def test_ganlu_map_complete(self):
        """测试干禄映射表完整性"""
        assert len(GANLU_MAP) == 10  # 十个天干
        for tiangan in Tiangan:
            assert tiangan in GANLU_MAP


# =============================================================================
# 任务 10.2 - 驿马计算测试
# =============================================================================

class TestYiMa:
    """驿马计算测试"""

    def test_shen_zi_chen_yima(self):
        """测试申子辰日驿马在寅"""
        assert get_yima(Dizhi.SHEN) == Dizhi.YIN
        assert get_yima(Dizhi.ZI) == Dizhi.YIN
        assert get_yima(Dizhi.CHEN) == Dizhi.YIN

    def test_hai_mao_wei_yima(self):
        """测试亥卯未日驿马在巳"""
        assert get_yima(Dizhi.HAI) == Dizhi.SI
        assert get_yima(Dizhi.MAO) == Dizhi.SI
        assert get_yima(Dizhi.WEI) == Dizhi.SI

    def test_yin_wu_xu_yima(self):
        """测试寅午戌日驿马在申"""
        assert get_yima(Dizhi.YIN) == Dizhi.SHEN
        assert get_yima(Dizhi.WU) == Dizhi.SHEN
        assert get_yima(Dizhi.XU) == Dizhi.SHEN

    def test_si_you_chou_yima(self):
        """测试巳酉丑日驿马在亥"""
        assert get_yima(Dizhi.SI) == Dizhi.HAI
        assert get_yima(Dizhi.YOU) == Dizhi.HAI
        assert get_yima(Dizhi.CHOU) == Dizhi.HAI

    def test_yima_map_complete(self):
        """测试驿马映射表完整性"""
        assert len(YIMA_MAP) == 12  # 十二个地支
        for dizhi in Dizhi:
            assert dizhi in YIMA_MAP


# =============================================================================
# 任务 10.3 - 羊刃计算测试
# =============================================================================

class TestYangRen:
    """羊刃计算测试"""

    def test_jia_yangren(self):
        """测试甲日羊刃在卯"""
        assert get_yangren(Tiangan.JIA) == Dizhi.MAO

    def test_yi_yangren(self):
        """测试乙日羊刃在寅"""
        assert get_yangren(Tiangan.YI) == Dizhi.YIN

    def test_bing_yangren(self):
        """测试丙日羊刃在午"""
        assert get_yangren(Tiangan.BING) == Dizhi.WU

    def test_ding_yangren(self):
        """测试丁日羊刃在巳"""
        assert get_yangren(Tiangan.DING) == Dizhi.SI

    def test_wu_yangren(self):
        """测试戊日羊刃在午"""
        assert get_yangren(Tiangan.WU) == Dizhi.WU

    def test_ji_yangren(self):
        """测试己日羊刃在巳"""
        assert get_yangren(Tiangan.JI) == Dizhi.SI

    def test_geng_yangren(self):
        """测试庚日羊刃在酉"""
        assert get_yangren(Tiangan.GENG) == Dizhi.YOU

    def test_xin_yangren(self):
        """测试辛日羊刃在申"""
        assert get_yangren(Tiangan.XIN) == Dizhi.SHEN

    def test_ren_yangren(self):
        """测试壬日羊刃在子"""
        assert get_yangren(Tiangan.REN) == Dizhi.ZI

    def test_gui_yangren(self):
        """测试癸日羊刃在亥"""
        assert get_yangren(Tiangan.GUI) == Dizhi.HAI

    def test_yangren_map_complete(self):
        """测试羊刃映射表完整性"""
        assert len(YANGREN_MAP) == 10  # 十个天干
        for tiangan in Tiangan:
            assert tiangan in YANGREN_MAP


# =============================================================================
# 任务 10.4 - 桃花计算测试
# =============================================================================

class TestTaoHua:
    """桃花计算测试"""

    def test_shen_zi_chen_taohua(self):
        """测试申子辰日桃花在酉"""
        assert get_taohua(Dizhi.SHEN) == Dizhi.YOU
        assert get_taohua(Dizhi.ZI) == Dizhi.YOU
        assert get_taohua(Dizhi.CHEN) == Dizhi.YOU

    def test_hai_mao_wei_taohua(self):
        """测试亥卯未日桃花在子"""
        assert get_taohua(Dizhi.HAI) == Dizhi.ZI
        assert get_taohua(Dizhi.MAO) == Dizhi.ZI
        assert get_taohua(Dizhi.WEI) == Dizhi.ZI

    def test_yin_wu_xu_taohua(self):
        """测试寅午戌日桃花在卯"""
        assert get_taohua(Dizhi.YIN) == Dizhi.MAO
        assert get_taohua(Dizhi.WU) == Dizhi.MAO
        assert get_taohua(Dizhi.XU) == Dizhi.MAO

    def test_si_you_chou_taohua(self):
        """测试巳酉丑日桃花在午"""
        assert get_taohua(Dizhi.SI) == Dizhi.WU
        assert get_taohua(Dizhi.YOU) == Dizhi.WU
        assert get_taohua(Dizhi.CHOU) == Dizhi.WU

    def test_taohua_map_complete(self):
        """测试桃花映射表完整性"""
        assert len(TAOHUA_MAP) == 12  # 十二个地支
        for dizhi in Dizhi:
            assert dizhi in TAOHUA_MAP


# =============================================================================
# 任务 10.5 - 神煞传播测试
# =============================================================================

class TestShenShaPropagation:
    """神煞传播测试"""

    def test_zi_propagation(self):
        """测试子的神煞传播"""
        # 子丑合、子午冲
        result = get_shensha_with_chonghe(Dizhi.ZI)
        assert Dizhi.ZI in result  # 本身
        assert Dizhi.CHOU in result  # 子丑合
        assert Dizhi.WU in result  # 子午冲

    def test_yin_propagation(self):
        """测试寅的神煞传播"""
        # 寅亥合、寅申冲
        result = get_shensha_with_chonghe(Dizhi.YIN)
        assert Dizhi.YIN in result  # 本身
        assert Dizhi.HAI in result  # 寅亥合
        assert Dizhi.SHEN in result  # 寅申冲

    def test_mao_propagation(self):
        """测试卯的神煞传播"""
        # 卯戌合、卯酉冲
        result = get_shensha_with_chonghe(Dizhi.MAO)
        assert Dizhi.MAO in result  # 本身
        assert Dizhi.XU in result  # 卯戌合
        assert Dizhi.YOU in result  # 卯酉冲

    def test_calculate_all_shensha(self):
        """测试计算所有神煞"""
        # 甲日午支
        result = calculate_all_shensha(Tiangan.JIA, Dizhi.WU)

        # 甲禄在寅
        assert ShenSha.GAN_LU in result
        assert Dizhi.YIN in result[ShenSha.GAN_LU]  # 寅本身
        assert Dizhi.HAI in result[ShenSha.GAN_LU]  # 寅亥合
        assert Dizhi.SHEN in result[ShenSha.GAN_LU]  # 寅申冲

        # 午日驿马在申
        assert ShenSha.YI_MA in result
        assert Dizhi.SHEN in result[ShenSha.YI_MA]

        # 甲羊刃在卯
        assert ShenSha.YANG_REN in result
        assert Dizhi.MAO in result[ShenSha.YANG_REN]

        # 午日桃花在卯
        assert ShenSha.TAO_HUA in result
        assert Dizhi.MAO in result[ShenSha.TAO_HUA]


# =============================================================================
# 任务 10.6 - 卦例神煞计算测试
# =============================================================================

class TestCalculateShenShaForGuali:
    """卦例神煞计算测试"""

    def test_guali_shensha_structure(self):
        """测试卦例神煞计算返回结构"""
        from backend.core.models import Guali

        guali = Guali(
            ben_gua=ZhongGua.QIAN_WEI_TIAN,
            ganzhi_day="甲午"
        )
        guali.calculate_all()
        result = calculate_shensha_for_guali(guali)

        assert "ganlu" in result
        assert "yima" in result
        assert "yangren" in result
        assert "taohua" in result

        assert "dizhi" in result["ganlu"]
        assert "is_in_gua" in result["ganlu"]
        assert "yaos" in result["ganlu"]

    def test_guali_ganlu_in_gua(self):
        """测试卦例中包含干禄"""
        from backend.core.models import Guali

        # 甲午日，甲禄在寅
        # 乾为天卦：子、寅、辰、午、申、戌
        guali = Guali(
            ben_gua=ZhongGua.QIAN_WEI_TIAN,
            ganzhi_day="甲午"
        )
        guali.calculate_all()
        result = calculate_shensha_for_guali(guali)

        # 甲禄在寅，乾卦二爻为寅
        assert result["ganlu"]["dizhi"] == "寅"
        assert result["ganlu"]["is_in_gua"] == True
        assert len(result["ganlu"]["yaos"]) > 0

    def test_guali_shensha_no_day_info(self):
        """测试无日柱信息时返回空结果"""
        from backend.core.models import Guali

        guali = Guali(ben_gua=ZhongGua.QIAN_WEI_TIAN)
        result = calculate_shensha_for_guali(guali)

        assert result["ganlu"]["dizhi"] is None
        assert result["ganlu"]["is_in_gua"] == False
        assert result["yima"]["dizhi"] is None


class TestGualiShenShaIntegration:
    """与Guali类集成测试"""

    def test_guali_set_shensha(self):
        """测试Guali类的set_shensha方法"""
        from backend.core.models import Guali

        guali = Guali(
            ben_gua=ZhongGua.QIAN_WEI_TIAN,
            ganzhi_day="甲午"
        )
        guali.calculate_all()

        assert guali.shensha is not None
        assert isinstance(guali.shensha, dict)

    def test_guali_calculate_all_includes_shensha(self):
        """测试calculate_all包含神煞计算"""
        from backend.core.models import Guali

        guali = Guali(
            ben_gua=ZhongGua.QIAN_WEI_TIAN,
            ganzhi_day="甲午"
        )
        guali.calculate_all()

        assert guali.shensha is not None
        assert "ganlu" in guali.shensha

    def test_guali_display_shows_shensha(self):
        """测试display方法显示神煞信息"""
        from backend.core.models import Guali

        guali = Guali(
            ben_gua=ZhongGua.QIAN_WEI_TIAN,
            ganzhi_day="甲午"
        )
        guali.calculate_all()

        display_str = guali.display()

        # 如果有神煞在卦中，应该包含神煞信息
        if any(guali.shensha.get(name, {}).get("is_in_gua") for name in ["ganlu", "yima", "yangren", "taohua"]):
            assert "神煞" in display_str


class TestShenShaTypeForDizhi:
    """神煞类型判断测试"""

    def test_is_ganlu(self):
        """测试是干禄"""
        # 甲禄在寅
        result = get_shensha_type_for_dizhi(Dizhi.YIN, Tiangan.JIA, Dizhi.WU)
        assert result[ShenSha.GAN_LU] == "是干禄"

    def test_dai_ganlu(self):
        """测试带干禄"""
        # 甲禄在寅，寅亥合，所以亥带干禄
        result = get_shensha_type_for_dizhi(Dizhi.HAI, Tiangan.JIA, Dizhi.WU)
        assert result[ShenSha.GAN_LU] == "带干禄"

    def test_not_ganlu(self):
        """测试不是干禄"""
        # 甲禄在寅，子不是寅，也不与寅合冲
        result = get_shensha_type_for_dizhi(Dizhi.ZI, Tiangan.JIA, Dizhi.WU)
        assert result[ShenSha.GAN_LU] is None

    def test_is_yima(self):
        """测试是驿马"""
        # 子日驿马在寅
        result = get_shensha_type_for_dizhi(Dizhi.YIN, Tiangan.JIA, Dizhi.ZI)
        assert result[ShenSha.YI_MA] == "是驿马"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
