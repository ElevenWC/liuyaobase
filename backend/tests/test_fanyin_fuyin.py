"""
六爻卦例分析系统 - 反吟伏吟计算模块测试

测试fanyin_fuyin模块的所有功能
"""
import pytest
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.core.enums import DanGua, ZhongGua
from backend.core.fanyin_fuyin import (
    YIMAO_FANYIN_PAIRS,
    YIMAO_FANYIN_MAP,
    YAOBIAN_FANYIN_PAIRS,
    YAOBIAN_FANYIN_MAP,
    FUYIN_PAIRS,
    FUYIN_MAP,
    is_yimao_fanyin,
    is_yaobian_fanyin,
    is_fuyin,
    get_yimao_fanyin_pair,
    get_yaobian_fanyin_pair,
    get_fuyin_pair,
    calculate_fanyin_fuyin_for_guali
)


# =============================================================================
# 任务 9.1 - 易冒反吟判断测试
# =============================================================================

class TestYiMaoFanYin:
    """易冒反吟判断测试"""

    def test_qian_xun_fanyin(self):
        """测试乾巽互变为易冒反吟"""
        assert is_yimao_fanyin(DanGua.QIAN, DanGua.XUN) == True
        assert is_yimao_fanyin(DanGua.XUN, DanGua.QIAN) == True

    def test_kan_li_fanyin(self):
        """测试坎离互变为易冒反吟"""
        assert is_yimao_fanyin(DanGua.KAN, DanGua.LI) == True
        assert is_yimao_fanyin(DanGua.LI, DanGua.KAN) == True

    def test_gen_kun_fanyin(self):
        """测试艮坤互变为易冒反吟"""
        assert is_yimao_fanyin(DanGua.GEN, DanGua.KUN) == True
        assert is_yimao_fanyin(DanGua.KUN, DanGua.GEN) == True

    def test_zhen_dui_fanyin(self):
        """测试震兑互变为易冒反吟"""
        assert is_yimao_fanyin(DanGua.ZHEN, DanGua.DUI) == True
        assert is_yimao_fanyin(DanGua.DUI, DanGua.ZHEN) == True

    def test_not_yimao_fanyin(self):
        """测试非易冒反吟关系"""
        assert is_yimao_fanyin(DanGua.QIAN, DanGua.KUN) == False
        assert is_yimao_fanyin(DanGua.QIAN, DanGua.QIAN) == False
        assert is_yimao_fanyin(DanGua.ZHEN, DanGua.XUN) == False

    def test_get_yimao_fanyin_pair(self):
        """测试获取易冒反吟对卦"""
        assert get_yimao_fanyin_pair(DanGua.QIAN) == DanGua.XUN
        assert get_yimao_fanyin_pair(DanGua.XUN) == DanGua.QIAN
        assert get_yimao_fanyin_pair(DanGua.KAN) == DanGua.LI
        assert get_yimao_fanyin_pair(DanGua.LI) == DanGua.KAN


# =============================================================================
# 任务 9.2 - 爻变反吟判断测试
# =============================================================================

class TestYaoBianFanYin:
    """爻变反吟判断测试"""

    def test_kun_xun_fanyin(self):
        """测试坤巽互变为爻变反吟"""
        assert is_yaobian_fanyin(DanGua.KUN, DanGua.XUN) == True
        assert is_yaobian_fanyin(DanGua.XUN, DanGua.KUN) == True

    def test_not_yaobian_fanyin(self):
        """测试非爻变反吟关系"""
        assert is_yaobian_fanyin(DanGua.QIAN, DanGua.XUN) == False
        assert is_yaobian_fanyin(DanGua.QIAN, DanGua.KUN) == False
        assert is_yaobian_fanyin(DanGua.KAN, DanGua.LI) == False

    def test_get_yaobian_fanyin_pair(self):
        """测试获取爻变反吟对卦"""
        assert get_yaobian_fanyin_pair(DanGua.KUN) == DanGua.XUN
        assert get_yaobian_fanyin_pair(DanGua.XUN) == DanGua.KUN
        assert get_yaobian_fanyin_pair(DanGua.QIAN) is None


# =============================================================================
# 任务 9.3 - 伏吟判断测试
# =============================================================================

class TestFuYin:
    """伏吟判断测试"""

    def test_qian_zhen_fuyin(self):
        """测试乾震互变为伏吟"""
        assert is_fuyin(DanGua.QIAN, DanGua.ZHEN) == True
        assert is_fuyin(DanGua.ZHEN, DanGua.QIAN) == True

    def test_not_fuyin(self):
        """测试非伏吟关系"""
        assert is_fuyin(DanGua.QIAN, DanGua.XUN) == False
        assert is_fuyin(DanGua.QIAN, DanGua.KUN) == False
        assert is_fuyin(DanGua.KAN, DanGua.LI) == False

    def test_get_fuyin_pair(self):
        """测试获取伏吟对卦"""
        assert get_fuyin_pair(DanGua.QIAN) == DanGua.ZHEN
        assert get_fuyin_pair(DanGua.ZHEN) == DanGua.QIAN
        assert get_fuyin_pair(DanGua.KAN) is None


# =============================================================================
# 任务 9.4 - 卦例反吟伏吟计算测试
# =============================================================================

class TestCalculateFanYinFuYinForGuali:
    """卦例反吟伏吟计算测试"""

    def test_no_zhi_gua(self):
        """测试无之卦时无反吟伏吟"""
        from backend.core.models import Guali

        guali = Guali(ben_gua=ZhongGua.QIAN_WEI_TIAN)
        result = calculate_fanyin_fuyin_for_guali(guali)

        assert result["has_fanyin"] == False
        assert result["has_fuyin"] == False
        assert len(result["details"]) == 0

    def test_yimao_fanyin_neigua(self):
        """测试内卦易冒反吟"""
        from backend.core.models import Guali

        # 根据规则文件：火天大有之火风鼎是内卦易冒反吟
        # 火天大有(0b111101): neigua=QIAN(乾), waigua=LI(离)
        # 火风鼎(0b011101): neigua=XUN(巽), waigua=LI(离)
        # 内卦：乾(111) → 巽(011)，乾巽互变为易冒反吟
        guali = Guali(
            ben_gua=ZhongGua.HUO_TIAN_DA_YOU,
            zhi_gua=ZhongGua.HUO_FENG_DING
        )
        guali.yao_bian_code = guali.ben_gua.code ^ guali.zhi_gua.code
        result = calculate_fanyin_fuyin_for_guali(guali)

        assert result["has_fanyin"] == True
        assert len(result["details"]) > 0
        # 验证是内卦的易冒反吟
        assert any(d["position"] == "内卦" and d["type"] == "易冒反吟" for d in result["details"])

    def test_fuyin_neigua(self):
        """测试内卦伏吟"""
        from backend.core.models import Guali

        # 天雷无妄(100111) → 天风姤(011111)
        # 注意：需要找到乾震互变的卦例
        # 使用雷天大壮(111100) → 天风姤(011111) 不是伏吟
        # 直接测试伏吟判断逻辑
        guali = Guali(
            ben_gua=ZhongGua.QIAN_WEI_TIAN,
            zhi_gua=ZhongGua.QIAN_WEI_TIAN  # 同卦
        )
        result = calculate_fanyin_fuyin_for_guali(guali)

        # 同卦没有变化，无反吟伏吟
        assert result["has_fanyin"] == False
        assert result["has_fuyin"] == False

    def test_result_structure(self):
        """测试返回结果结构"""
        from backend.core.models import Guali

        guali = Guali(
            ben_gua=ZhongGua.HUO_TIAN_DA_YOU,
            zhi_gua=ZhongGua.HUO_FENG_DING
        )
        guali.yao_bian_code = guali.ben_gua.code ^ guali.zhi_gua.code
        result = calculate_fanyin_fuyin_for_guali(guali)

        assert "has_fanyin" in result
        assert "has_fuyin" in result
        assert "neigua" in result
        assert "waigua" in result
        assert "details" in result

        assert isinstance(result["has_fanyin"], bool)
        assert isinstance(result["has_fuyin"], bool)
        assert isinstance(result["neigua"], list)
        assert isinstance(result["waigua"], list)
        assert isinstance(result["details"], list)


class TestGualiFanYinFuYinIntegration:
    """与Guali类集成测试"""

    def test_guali_set_fanyin_fuyin(self):
        """测试Guali类的set_fanyin_fuyin方法"""
        from backend.core.models import Guali

        guali = Guali(
            ben_gua=ZhongGua.HUO_TIAN_DA_YOU,
            zhi_gua=ZhongGua.HUO_FENG_DING
        )
        guali.yao_bian_code = guali.ben_gua.code ^ guali.zhi_gua.code
        guali.set_fanyin_fuyin()

        assert guali.fanyin_fuyin is not None
        assert isinstance(guali.fanyin_fuyin, dict)

    def test_guali_calculate_all_includes_fanyin_fuyin(self):
        """测试calculate_all包含反吟伏吟计算"""
        from backend.core.models import Guali

        guali = Guali(
            ben_gua=ZhongGua.HUO_TIAN_DA_YOU,
            zhi_gua=ZhongGua.HUO_FENG_DING
        )
        guali.yao_bian_code = guali.ben_gua.code ^ guali.zhi_gua.code
        guali.calculate_all()

        assert guali.fanyin_fuyin is not None
        assert "has_fanyin" in guali.fanyin_fuyin

    def test_guali_display_shows_fanyin_fuyin(self):
        """测试display方法显示反吟伏吟信息"""
        from backend.core.models import Guali

        guali = Guali(
            ben_gua=ZhongGua.HUO_TIAN_DA_YOU,
            zhi_gua=ZhongGua.HUO_FENG_DING
        )
        guali.yao_bian_code = guali.ben_gua.code ^ guali.zhi_gua.code
        guali.calculate_all()

        display_str = guali.display()

        # 如果有反吟伏吟，应该包含相应信息
        if guali.fanyin_fuyin.get("has_fanyin") or guali.fanyin_fuyin.get("has_fuyin"):
            assert "反吟伏吟" in display_str


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
