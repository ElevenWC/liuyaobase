"""
六爻卦例分析系统 - 五行生克辅助模块测试

测试wuxing_helper模块的所有功能
"""
import pytest
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.core.enums import Wuxing, LiuQin
from backend.core.wuxing_helper import (
    wuxing_sheng,
    wuxing_ke,
    wuxing_sheng_by,
    wuxing_ke_by,
    calculate_liuqin,
    get_liuqin_by_relation,
    analyze_wuxing_relation
)


# =============================================================================
# 任务 5.1 - 五行生克判断辅助函数测试
# =============================================================================

class TestWuxingSheng:
    """五行相生判断测试"""

    def test_jin_sheng_shui(self):
        """测试金生水"""
        assert wuxing_sheng(Wuxing.JIN, Wuxing.SHUI) == True

    def test_shui_sheng_mu(self):
        """测试水生木"""
        assert wuxing_sheng(Wuxing.SHUI, Wuxing.MU) == True

    def test_mu_sheng_huo(self):
        """测试木生火"""
        assert wuxing_sheng(Wuxing.MU, Wuxing.HUO) == True

    def test_huo_sheng_tu(self):
        """测试火生土"""
        assert wuxing_sheng(Wuxing.HUO, Wuxing.TU) == True

    def test_tu_sheng_jin(self):
        """测试土生金"""
        assert wuxing_sheng(Wuxing.TU, Wuxing.JIN) == True

    def test_shui_not_sheng_jin(self):
        """测试水不生金"""
        assert wuxing_sheng(Wuxing.SHUI, Wuxing.JIN) == False

    def test_jin_not_sheng_mu(self):
        """测试金不生木"""
        assert wuxing_sheng(Wuxing.JIN, Wuxing.MU) == False

    def test_same_not_sheng(self):
        """测试相同五行不相生"""
        assert wuxing_sheng(Wuxing.JIN, Wuxing.JIN) == False


class TestWuxingKe:
    """五行相克判断测试"""

    def test_jin_ke_mu(self):
        """测试金克木"""
        assert wuxing_ke(Wuxing.JIN, Wuxing.MU) == True

    def test_mu_ke_tu(self):
        """测试木克土"""
        assert wuxing_ke(Wuxing.MU, Wuxing.TU) == True

    def test_tu_ke_shui(self):
        """测试土克水"""
        assert wuxing_ke(Wuxing.TU, Wuxing.SHUI) == True

    def test_shui_ke_huo(self):
        """测试水克火"""
        assert wuxing_ke(Wuxing.SHUI, Wuxing.HUO) == True

    def test_huo_ke_jin(self):
        """测试火克金"""
        assert wuxing_ke(Wuxing.HUO, Wuxing.JIN) == True

    def test_mu_not_ke_jin(self):
        """测试木不克金"""
        assert wuxing_ke(Wuxing.MU, Wuxing.JIN) == False

    def test_jin_not_ke_shui(self):
        """测试金不克水"""
        assert wuxing_ke(Wuxing.JIN, Wuxing.SHUI) == False

    def test_same_not_ke(self):
        """测试相同五行不相克"""
        assert wuxing_ke(Wuxing.JIN, Wuxing.JIN) == False


class TestWuxingShengBy:
    """五行被生判断测试"""

    def test_shui_sheng_by_jin(self):
        """测试水被金生"""
        assert wuxing_sheng_by(Wuxing.SHUI, Wuxing.JIN) == True

    def test_mu_sheng_by_shui(self):
        """测试木被水生"""
        assert wuxing_sheng_by(Wuxing.MU, Wuxing.SHUI) == True


class TestWuxingKeBy:
    """五行被克判断测试"""

    def test_mu_ke_by_jin(self):
        """测试木被金克"""
        assert wuxing_ke_by(Wuxing.MU, Wuxing.JIN) == True

    def test_huo_ke_by_shui(self):
        """测试火被水克"""
        assert wuxing_ke_by(Wuxing.HUO, Wuxing.SHUI) == True


# =============================================================================
# 任务 5.2 - 单爻六亲计算测试
# =============================================================================

class TestCalculateLiuqin:
    """六亲计算测试"""

    def test_liuqin_xiong_di(self):
        """测试相同五行为兄弟"""
        # 卦宫五行 = 爻地支五行 → 兄弟
        assert calculate_liuqin(Wuxing.MU, Wuxing.MU) == LiuQin.XIONG_DI
        assert calculate_liuqin(Wuxing.HUO, Wuxing.HUO) == LiuQin.XIONG_DI
        assert calculate_liuqin(Wuxing.JIN, Wuxing.JIN) == LiuQin.XIONG_DI

    def test_liuqin_zi_sun(self):
        """测试卦宫生爻为子孙"""
        # 卦宫五行生爻地支五行 → 子孙
        assert calculate_liuqin(Wuxing.SHUI, Wuxing.MU) == LiuQin.ZI_SUN   # 水生木
        assert calculate_liuqin(Wuxing.MU, Wuxing.HUO) == LiuQin.ZI_SUN    # 木生火
        assert calculate_liuqin(Wuxing.JIN, Wuxing.SHUI) == LiuQin.ZI_SUN  # 金生水

    def test_liuqin_qi_cai(self):
        """测试卦宫克爻为妻财"""
        # 卦宫五行克爻地支五行 → 妻财
        assert calculate_liuqin(Wuxing.MU, Wuxing.TU) == LiuQin.QI_CAI   # 木克土
        assert calculate_liuqin(Wuxing.SHUI, Wuxing.HUO) == LiuQin.QI_CAI  # 水克火
        assert calculate_liuqin(Wuxing.JIN, Wuxing.MU) == LiuQin.QI_CAI   # 金克木

    def test_liuqin_fu_mu(self):
        """测试爻生卦宫为父母"""
        # 爻地支五行生卦宫五行 → 父母
        assert calculate_liuqin(Wuxing.JIN, Wuxing.TU) == LiuQin.FU_MU   # 土生金
        assert calculate_liuqin(Wuxing.MU, Wuxing.SHUI) == LiuQin.FU_MU  # 水生木
        assert calculate_liuqin(Wuxing.HUO, Wuxing.MU) == LiuQin.FU_MU   # 木生火

    def test_liuqin_guan_gui(self):
        """测试爻克卦宫为官鬼"""
        # 爻地支五行克卦宫五行 → 官鬼
        assert calculate_liuqin(Wuxing.MU, Wuxing.JIN) == LiuQin.GUAN_GUI   # 金克木（爻是木，卦宫是金）
        assert calculate_liuqin(Wuxing.SHUI, Wuxing.TU) == LiuQin.GUAN_GUI  # 土克水
        assert calculate_liuqin(Wuxing.HUO, Wuxing.SHUI) == LiuQin.GUAN_GUI # 水克火

    def test_liuqin_qian_gong(self):
        """测试乾宫（金）六亲"""
        gongwuxing = Wuxing.JIN  # 乾宫属金

        # 子水 - 金生水 → 子孙
        assert calculate_liuqin(gongwuxing, Wuxing.SHUI) == LiuQin.ZI_SUN
        # 寅木 - 金克木 → 妻财
        assert calculate_liuqin(gongwuxing, Wuxing.MU) == LiuQin.QI_CAI
        # 辰土 - 土生金 → 父母
        assert calculate_liuqin(gongwuxing, Wuxing.TU) == LiuQin.FU_MU
        # 申金 - 金=金 → 兄弟
        assert calculate_liuqin(gongwuxing, Wuxing.JIN) == LiuQin.XIONG_DI
        # 巳火 - 火克金 → 官鬼
        assert calculate_liuqin(gongwuxing, Wuxing.HUO) == LiuQin.GUAN_GUI


# =============================================================================
# 任务 5.3 - 卦例六亲计算测试
# =============================================================================

class TestGualiLiuqin:
    """卦例六亲计算测试"""

    def test_qian_wei_tian_liuqin(self):
        """测试乾为天六亲（完整测试）"""
        from backend.core.enums import ZhongGua, Dizhi
        from backend.core.models import Guali
        from backend.core.nama import load_dizhi_to_guali

        guali = Guali(ben_gua=ZhongGua.QIAN_WEI_TIAN)
        load_dizhi_to_guali(guali)  # 装地支
        guali.set_liuqin()          # 计算六亲

        # 乾宫属金
        # 初爻子水 → 金生水 → 子孙
        assert guali.yaos[0].liuqin == LiuQin.ZI_SUN
        # 二爻寅木 → 金克木 → 妻财
        assert guali.yaos[1].liuqin == LiuQin.QI_CAI
        # 三爻辰土 → 土生金 → 父母
        assert guali.yaos[2].liuqin == LiuQin.FU_MU
        # 四爻午火 → 火克金 → 官鬼
        assert guali.yaos[3].liuqin == LiuQin.GUAN_GUI
        # 五爻申金 → 金=金 → 兄弟
        assert guali.yaos[4].liuqin == LiuQin.XIONG_DI
        # 上爻戌土 → 土生金 → 父母
        assert guali.yaos[5].liuqin == LiuQin.FU_MU

    def test_kun_wei_di_liuqin(self):
        """测试坤为地六亲"""
        from backend.core.enums import ZhongGua
        from backend.core.models import Guali
        from backend.core.nama import load_dizhi_to_guali

        guali = Guali(ben_gua=ZhongGua.KUN_WEI_DI)
        load_dizhi_to_guali(guali)
        guali.set_liuqin()

        # 坤宫属土
        # 验证所有六亲已设置
        for yao in guali.yaos:
            assert yao.liuqin is not None


# =============================================================================
# 辅助函数测试
# =============================================================================

class TestHelperFunctions:
    """辅助函数测试"""

    def test_get_liuqin_by_relation(self):
        """测试获取五行关系描述"""
        # 相同
        assert get_liuqin_by_relation(Wuxing.JIN, Wuxing.JIN) == "同"
        # 生
        assert get_liuqin_by_relation(Wuxing.JIN, Wuxing.SHUI) == "生"
        # 克
        assert get_liuqin_by_relation(Wuxing.JIN, Wuxing.MU) == "克"
        # 被生
        assert get_liuqin_by_relation(Wuxing.SHUI, Wuxing.JIN) == "被生"
        # 被克
        assert get_liuqin_by_relation(Wuxing.MU, Wuxing.JIN) == "被克"

    def test_analyze_wuxing_relation(self):
        """测试五行关系详细分析"""
        result = analyze_wuxing_relation(Wuxing.JIN, Wuxing.MU)

        assert result["a"] == "金"
        assert result["b"] == "木"
        assert result["a_sheng_b"] == False
        assert result["a_ke_b"] == True
        assert result["b_sheng_a"] == False
        assert result["b_ke_a"] == False
        assert result["same"] == False
        assert result["relation"] == "克"


# =============================================================================
# 边界条件测试
# =============================================================================

class TestBoundaryConditions:
    """边界条件测试"""

    def test_all_wuxing_combinations(self):
        """测试所有五行组合"""
        wuxing_list = [Wuxing.MU, Wuxing.HUO, Wuxing.TU, Wuxing.JIN, Wuxing.SHUI]

        for a in wuxing_list:
            for b in wuxing_list:
                # 确保不会抛出异常
                liuqin = calculate_liuqin(a, b)
                assert liuqin in LiuQin


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
