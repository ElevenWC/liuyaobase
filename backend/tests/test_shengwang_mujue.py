"""
六爻卦例分析系统 - 生旺墓绝计算模块测试

测试shengwang_mujue模块的所有功能
"""
import pytest
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.core.enums import Dizhi, Wuxing, ZhongGua
from backend.core.shengwang_mujue import (
    SHENGWANG_MUJUE_MAP,
    DIZHI_STATE_MAP,
    get_changsheng,
    get_diwang,
    get_mu,
    get_jue,
    get_all_states,
    get_shengwang_mujue_state,
    is_changsheng,
    is_diwang,
    is_mu,
    is_jue,
    calculate_yao_shengwang_mujue,
    calculate_shengwang_mujue_for_guali
)


# =============================================================================
# 任务 11.1 - 生旺墓绝映射表测试
# =============================================================================

class TestShengWangMuJueMap:
    """生旺墓绝映射表测试"""

    def test_map_completeness(self):
        """测试映射表包含所有五行"""
        assert len(SHENGWANG_MUJUE_MAP) == 5  # 五行
        for wuxing in Wuxing:
            assert wuxing in SHENGWANG_MUJUE_MAP

    def test_map_states_completeness(self):
        """测试每个五行包含四种状态"""
        for wuxing, states in SHENGWANG_MUJUE_MAP.items():
            assert "长生" in states
            assert "帝旺" in states
            assert "墓" in states
            assert "绝" in states


# =============================================================================
# 木的生旺墓绝测试
# =============================================================================

class TestMuShengWangMuJue:
    """木的生旺墓绝测试"""

    def test_mu_changsheng(self):
        """测试木长生在亥"""
        assert get_changsheng(Wuxing.MU) == Dizhi.HAI

    def test_mu_diwang(self):
        """测试木帝旺在卯"""
        assert get_diwang(Wuxing.MU) == Dizhi.MAO

    def test_mu_mu(self):
        """测试木墓在未"""
        assert get_mu(Wuxing.MU) == Dizhi.WEI

    def test_mu_jue(self):
        """测试木绝在申"""
        assert get_jue(Wuxing.MU) == Dizhi.SHEN

    def test_mu_all_states(self):
        """测试木的所有状态"""
        states = get_all_states(Wuxing.MU)
        assert states["长生"] == Dizhi.HAI
        assert states["帝旺"] == Dizhi.MAO
        assert states["墓"] == Dizhi.WEI
        assert states["绝"] == Dizhi.SHEN


# =============================================================================
# 火的生旺墓绝测试
# =============================================================================

class TestHuoShengWangMuJue:
    """火的生旺墓绝测试"""

    def test_huo_changsheng(self):
        """测试火长生在寅"""
        assert get_changsheng(Wuxing.HUO) == Dizhi.YIN

    def test_huo_diwang(self):
        """测试火帝旺在午"""
        assert get_diwang(Wuxing.HUO) == Dizhi.WU

    def test_huo_mu(self):
        """测试火墓在戌"""
        assert get_mu(Wuxing.HUO) == Dizhi.XU

    def test_huo_jue(self):
        """测试火绝在亥"""
        assert get_jue(Wuxing.HUO) == Dizhi.HAI

    def test_huo_all_states(self):
        """测试火的所有状态"""
        states = get_all_states(Wuxing.HUO)
        assert states["长生"] == Dizhi.YIN
        assert states["帝旺"] == Dizhi.WU
        assert states["墓"] == Dizhi.XU
        assert states["绝"] == Dizhi.HAI


# =============================================================================
# 金的生旺墓绝测试
# =============================================================================

class TestJinShengWangMuJue:
    """金的生旺墓绝测试"""

    def test_jin_changsheng(self):
        """测试金长生在巳"""
        assert get_changsheng(Wuxing.JIN) == Dizhi.SI

    def test_jin_diwang(self):
        """测试金帝旺在酉"""
        assert get_diwang(Wuxing.JIN) == Dizhi.YOU

    def test_jin_mu(self):
        """测试金墓在丑"""
        assert get_mu(Wuxing.JIN) == Dizhi.CHOU

    def test_jin_jue(self):
        """测试金绝在寅"""
        assert get_jue(Wuxing.JIN) == Dizhi.YIN

    def test_jin_all_states(self):
        """测试金的所有状态"""
        states = get_all_states(Wuxing.JIN)
        assert states["长生"] == Dizhi.SI
        assert states["帝旺"] == Dizhi.YOU
        assert states["墓"] == Dizhi.CHOU
        assert states["绝"] == Dizhi.YIN


# =============================================================================
# 水的生旺墓绝测试
# =============================================================================

class TestShuiShengWangMuJue:
    """水的生旺墓绝测试"""

    def test_shui_changsheng(self):
        """测试水长生在申"""
        assert get_changsheng(Wuxing.SHUI) == Dizhi.SHEN

    def test_shui_diwang(self):
        """测试水帝旺在子"""
        assert get_diwang(Wuxing.SHUI) == Dizhi.ZI

    def test_shui_mu(self):
        """测试水墓在辰"""
        assert get_mu(Wuxing.SHUI) == Dizhi.CHEN

    def test_shui_jue(self):
        """测试水绝在巳"""
        assert get_jue(Wuxing.SHUI) == Dizhi.SI

    def test_shui_all_states(self):
        """测试水的所有状态"""
        states = get_all_states(Wuxing.SHUI)
        assert states["长生"] == Dizhi.SHEN
        assert states["帝旺"] == Dizhi.ZI
        assert states["墓"] == Dizhi.CHEN
        assert states["绝"] == Dizhi.SI


# =============================================================================
# 土的生旺墓绝测试
# =============================================================================

class TestTuShengWangMuJue:
    """土的生旺墓绝测试"""

    def test_tu_changsheng(self):
        """测试土长生在申（与水相同）"""
        assert get_changsheng(Wuxing.TU) == Dizhi.SHEN

    def test_tu_diwang(self):
        """测试土帝旺在子（与水相同）"""
        assert get_diwang(Wuxing.TU) == Dizhi.ZI

    def test_tu_mu(self):
        """测试土墓在辰（与水相同）"""
        assert get_mu(Wuxing.TU) == Dizhi.CHEN

    def test_tu_jue(self):
        """测试土绝在巳（与水相同）"""
        assert get_jue(Wuxing.TU) == Dizhi.SI

    def test_tu_same_as_shui(self):
        """测试土的生旺墓绝与水相同"""
        tu_states = get_all_states(Wuxing.TU)
        shui_states = get_all_states(Wuxing.SHUI)
        assert tu_states == shui_states


# =============================================================================
# 任务 11.2 - 生旺墓绝状态判断测试
# =============================================================================

class TestGetShengWangMuJueState:
    """生旺墓绝状态判断测试"""

    def test_mu_changsheng_state(self):
        """测试木长生状态"""
        assert get_shengwang_mujue_state(Wuxing.MU, Dizhi.HAI) == "长生"

    def test_mu_diwang_state(self):
        """测试木帝旺状态"""
        assert get_shengwang_mujue_state(Wuxing.MU, Dizhi.MAO) == "帝旺"

    def test_mu_mu_state(self):
        """测试木墓状态"""
        assert get_shengwang_mujue_state(Wuxing.MU, Dizhi.WEI) == "墓"

    def test_mu_jue_state(self):
        """测试木绝状态"""
        assert get_shengwang_mujue_state(Wuxing.MU, Dizhi.SHEN) == "绝"

    def test_mu_no_state(self):
        """测试木无生旺墓绝状态"""
        assert get_shengwang_mujue_state(Wuxing.MU, Dizhi.ZI) is None
        assert get_shengwang_mujue_state(Wuxing.MU, Dizhi.WU) is None

    def test_huo_changsheng_state(self):
        """测试火长生状态"""
        assert get_shengwang_mujue_state(Wuxing.HUO, Dizhi.YIN) == "长生"

    def test_jin_diwang_state(self):
        """测试金帝旺状态"""
        assert get_shengwang_mujue_state(Wuxing.JIN, Dizhi.YOU) == "帝旺"

    def test_shui_mu_state(self):
        """测试水墓状态"""
        assert get_shengwang_mujue_state(Wuxing.SHUI, Dizhi.CHEN) == "墓"


# =============================================================================
# 布尔判断函数测试
# =============================================================================

class TestBooleanFunctions:
    """布尔判断函数测试"""

    def test_is_changsheng(self):
        """测试长生判断"""
        assert is_changsheng(Wuxing.MU, Dizhi.HAI) == True
        assert is_changsheng(Wuxing.MU, Dizhi.ZI) == False
        assert is_changsheng(Wuxing.HUO, Dizhi.YIN) == True

    def test_is_diwang(self):
        """测试帝旺判断"""
        assert is_diwang(Wuxing.MU, Dizhi.MAO) == True
        assert is_diwang(Wuxing.MU, Dizhi.YOU) == False
        assert is_diwang(Wuxing.JIN, Dizhi.YOU) == True

    def test_is_mu(self):
        """测试墓判断"""
        assert is_mu(Wuxing.MU, Dizhi.WEI) == True
        assert is_mu(Wuxing.MU, Dizhi.CHEN) == False
        assert is_mu(Wuxing.SHUI, Dizhi.CHEN) == True

    def test_is_jue(self):
        """测试绝判断"""
        assert is_jue(Wuxing.MU, Dizhi.SHEN) == True
        assert is_jue(Wuxing.MU, Dizhi.SI) == False
        assert is_jue(Wuxing.SHUI, Dizhi.SI) == True


# =============================================================================
# 爻与日支生旺墓绝计算测试
# =============================================================================

class TestCalculateYaoShengWangMuJue:
    """爻与日支生旺墓绝计算测试"""

    def test_yao_changsheng(self):
        """测试爻长生"""
        # 木爻在亥日
        result = calculate_yao_shengwang_mujue(Wuxing.MU, Dizhi.HAI)
        assert result["state"] == "长生"
        assert result["yao_wuxing"] == "木"
        assert result["compare_dizhi"] == "亥"
        assert "长生" in result["description"]

    def test_yao_diwang(self):
        """测试爻帝旺"""
        # 水爻在子日
        result = calculate_yao_shengwang_mujue(Wuxing.SHUI, Dizhi.ZI)
        assert result["state"] == "帝旺"
        assert "帝旺" in result["description"]

    def test_yao_mu(self):
        """测试爻墓"""
        # 金爻在丑日
        result = calculate_yao_shengwang_mujue(Wuxing.JIN, Dizhi.CHOU)
        assert result["state"] == "墓"
        assert "墓" in result["description"]

    def test_yao_jue(self):
        """测试爻绝"""
        # 火爻在亥日
        result = calculate_yao_shengwang_mujue(Wuxing.HUO, Dizhi.HAI)
        assert result["state"] == "绝"
        assert "绝" in result["description"]

    def test_yao_no_relation(self):
        """测试爻无生旺墓绝关系"""
        # 木爻在子日（水生木，但非生旺墓绝）
        result = calculate_yao_shengwang_mujue(Wuxing.MU, Dizhi.ZI)
        assert result["state"] is None
        assert "无生旺墓绝关系" in result["description"]


# =============================================================================
# 卦例生旺墓绝计算测试
# =============================================================================

class TestCalculateShengWangMuJueForGuali:
    """卦例生旺墓绝计算测试"""

    def test_guali_shengwang_mujue_structure(self):
        """测试卦例生旺墓绝计算返回结构"""
        from backend.core.models import Guali

        guali = Guali(
            ben_gua=ZhongGua.QIAN_WEI_TIAN,
            ganzhi_day="甲午"
        )
        guali.calculate_all()
        result = calculate_shengwang_mujue_for_guali(guali)

        assert "day_dizhi" in result
        assert "yaos" in result
        assert result["day_dizhi"] == "午"

    def test_guali_yao_states(self):
        """测试卦例各爻的生旺墓绝状态"""
        from backend.core.models import Guali

        # 乾为天卦，午日
        # 六爻地支：子、寅、辰、午、申、戌
        guali = Guali(
            ben_gua=ZhongGua.QIAN_WEI_TIAN,
            ganzhi_day="甲午"
        )
        guali.calculate_all()
        result = calculate_shengwang_mujue_for_guali(guali)

        # 检查返回的爻列表
        assert len(result["yaos"]) == 6

        # 检查每个爻都有必要字段
        for yao_info in result["yaos"]:
            assert "position" in yao_info
            assert "yao_dizhi" in yao_info
            assert "yao_wuxing" in yao_info
            assert "state" in yao_info
            assert "description" in yao_info

    def test_guali_no_day_info(self):
        """测试无日柱信息时返回空结果"""
        from backend.core.models import Guali

        guali = Guali(ben_gua=ZhongGua.QIAN_WEI_TIAN)
        result = calculate_shengwang_mujue_for_guali(guali)

        assert result["day_dizhi"] is None
        assert len(result["yaos"]) == 0


class TestGualiShengWangMuJueIntegration:
    """与Guali类集成测试"""

    def test_guali_set_shengwang_mujue(self):
        """测试Guali类的set_shengwang_mujue方法"""
        from backend.core.models import Guali

        guali = Guali(
            ben_gua=ZhongGua.QIAN_WEI_TIAN,
            ganzhi_day="甲午"
        )
        guali.calculate_all()

        assert guali.shengwang_mujue is not None
        assert isinstance(guali.shengwang_mujue, dict)

    def test_guali_calculate_all_includes_shengwang_mujue(self):
        """测试calculate_all包含生旺墓绝计算"""
        from backend.core.models import Guali

        guali = Guali(
            ben_gua=ZhongGua.QIAN_WEI_TIAN,
            ganzhi_day="甲午"
        )
        guali.calculate_all()

        assert guali.shengwang_mujue is not None
        assert "day_dizhi" in guali.shengwang_mujue


# =============================================================================
# 边界条件测试
# =============================================================================

class TestBoundaryConditions:
    """边界条件测试"""

    def test_all_wuxing_all_states(self):
        """测试所有五行的所有状态"""
        for wuxing in Wuxing:
            states = get_all_states(wuxing)
            assert len(states) == 4

            # 验证每个状态都有对应的地支
            for state_name, dizhi in states.items():
                assert isinstance(dizhi, Dizhi)

    def test_all_dizhi_states(self):
        """测试所有地支状态的映射"""
        # 每个五行应该有4个状态映射
        for wuxing in Wuxing:
            count = sum(1 for (w, d), s in DIZHI_STATE_MAP.items() if w == wuxing)
            assert count == 4


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
