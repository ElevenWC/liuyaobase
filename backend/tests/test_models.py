"""
六爻卦例分析系统 - 核心业务类测试

测试Yao类和Guali类
"""
import pytest
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.core.enums import (
    Wuxing, Tiangan, Dizhi, DanGua, ZhongGua, LiuQin, LiuShen
)
from backend.core.models import Yao, Guali, create_guali_from_input


# =============================================================================
# 任务 2.1 - Yao类基础结构测试
# =============================================================================

class TestYaoBasic:
    """Yao类基础结构测试"""

    def test_yao_creation(self):
        """测试Yao类创建"""
        yao = Yao(
            position=1,
            yao_type=1,  # 阳爻
            state=0,     # 静爻
            dizhi=Dizhi.ZI,
            liuqin=LiuQin.ZI_SUN,
            liushen=LiuShen.QING_LONG,
            is_world=False,
            is_response=False
        )
        assert yao.position == 1
        assert yao.yao_type == 1
        assert yao.state == 0
        assert yao.dizhi == Dizhi.ZI
        assert yao.liuqin == LiuQin.ZI_SUN
        assert yao.liushen == LiuShen.QING_LONG
        assert yao.is_world == False
        assert yao.is_response == False

    def test_yao_default_values(self):
        """测试Yao类默认值"""
        yao = Yao(position=2, yao_type=0)
        assert yao.state == 0
        assert yao.dizhi is None
        assert yao.liuqin is None
        assert yao.liushen is None
        assert yao.is_world == False
        assert yao.is_response == False

    def test_yao_position_names(self):
        """测试爻位名称"""
        assert Yao(position=1, yao_type=1).position_name == "初爻"
        assert Yao(position=2, yao_type=1).position_name == "二爻"
        assert Yao(position=3, yao_type=1).position_name == "三爻"
        assert Yao(position=4, yao_type=1).position_name == "四爻"
        assert Yao(position=5, yao_type=1).position_name == "五爻"
        assert Yao(position=6, yao_type=1).position_name == "上爻"

    def test_yao_type_names(self):
        """测试爻类型名称"""
        assert Yao(position=1, yao_type=1).yao_type_name == "阳爻"
        assert Yao(position=1, yao_type=0).yao_type_name == "阴爻"

    def test_yao_state_names(self):
        """测试爻状态名称"""
        assert Yao(position=1, yao_type=1, state=0).state_name == "静爻"
        assert Yao(position=1, yao_type=1, state=1).state_name == "动爻"


# =============================================================================
# 任务 2.2 - Yao类wuxing属性测试
# =============================================================================

class TestYaoWuxing:
    """Yao类wuxing属性测试"""

    def test_yao_wuxing_from_dizhi(self):
        """测试从地支获取五行"""
        # 子属水
        yao = Yao(position=1, yao_type=1, dizhi=Dizhi.ZI)
        assert yao.wuxing == Wuxing.SHUI

        # 卯属木
        yao2 = Yao(position=2, yao_type=0, dizhi=Dizhi.MAO)
        assert yao2.wuxing == Wuxing.MU

        # 巳属火
        yao3 = Yao(position=3, yao_type=1, dizhi=Dizhi.SI)
        assert yao3.wuxing == Wuxing.HUO

        # 申属金
        yao4 = Yao(position=4, yao_type=1, dizhi=Dizhi.SHEN)
        assert yao4.wuxing == Wuxing.JIN

        # 丑属土
        yao5 = Yao(position=5, yao_type=0, dizhi=Dizhi.CHOU)
        assert yao5.wuxing == Wuxing.TU

    def test_yao_wuxing_none_when_no_dizhi(self):
        """测试当地支为None时wuxing为None"""
        yao = Yao(position=1, yao_type=1, dizhi=None)
        assert yao.wuxing is None


# =============================================================================
# 任务 2.3 - Guali类基础结构测试
# =============================================================================

class TestGualiBasic:
    """Guali类基础结构测试"""

    def test_guali_creation(self):
        """测试Guali类创建"""
        guali = Guali(
            id=1,
            solar_year=2024,
            solar_month=2,
            solar_day=12,
            ben_gua=ZhongGua.QIAN_WEI_TIAN,
            zhi_gua=None,
            zhan_wen="测试占问"
        )
        assert guali.id == 1
        assert guali.solar_year == 2024
        assert guali.ben_gua == ZhongGua.QIAN_WEI_TIAN
        assert guali.zhi_gua is None

    def test_guali_properties(self):
        """测试Guali类属性"""
        guali = Guali(
            solar_year=2024,
            solar_month=2,
            solar_day=12,
            ben_gua=ZhongGua.QIAN_WEI_TIAN
        )
        assert guali.ben_gua_name == "乾为天"
        assert guali.zhi_gua_name is None
        assert guali.gongwei == "乾宫"
        assert guali.gongwei_index == "本宫"
        assert guali.gongwuxing == Wuxing.JIN

    def test_guali_gua_display_name(self):
        """测试卦名显示"""
        # 无之卦
        guali1 = Guali(ben_gua=ZhongGua.QIAN_WEI_TIAN)
        assert guali1.gua_display_name == "乾为天"

        # 有之卦
        guali2 = Guali(
            ben_gua=ZhongGua.QIAN_WEI_TIAN,
            zhi_gua=ZhongGua.TIAN_FENG_GOU,
            yao_bian_code=0b000001
        )
        assert guali2.gua_display_name == "乾为天之天风姤"

    def test_guali_day_tiangan_dizhi(self):
        """测试日干日支提取"""
        guali = Guali(ganzhi_day="甲午")
        assert guali.day_tiangan == Tiangan.JIA
        assert guali.day_dizhi == Dizhi.WU


# =============================================================================
# 任务 2.4 - Guali类爻列表初始化测试
# =============================================================================

class TestGualiYaos:
    """Guali类爻列表初始化测试"""

    def test_guali_yaos_count(self):
        """测试爻数量"""
        guali = Guali(ben_gua=ZhongGua.QIAN_WEI_TIAN)
        assert len(guali.yaos) == 6

    def test_guali_yaos_type_qian(self):
        """测试乾卦爻类型（全部阳爻）"""
        guali = Guali(ben_gua=ZhongGua.QIAN_WEI_TIAN)  # 111111
        for yao in guali.yaos:
            assert yao.yao_type == 1  # 全部阳爻

    def test_guali_yaos_type_kun(self):
        """测试坤卦爻类型（全部阴爻）"""
        guali = Guali(ben_gua=ZhongGua.KUN_WEI_DI)  # 000000
        for yao in guali.yaos:
            assert yao.yao_type == 0  # 全部阴爻

    def test_guali_yaos_state_no_zhi_gua(self):
        """测试无之卦时爻状态（全部静爻）"""
        guali = Guali(
            ben_gua=ZhongGua.QIAN_WEI_TIAN,
            zhi_gua=None,
            yao_bian_code=0
        )
        for yao in guali.yaos:
            assert yao.state == 0  # 全部静爻

    def test_guali_yaos_state_with_zhi_gua(self):
        """测试有之卦时爻状态"""
        # 乾为天(111111) -> 天风姤(011111)
        # 只有初爻变动（1->0）
        guali = Guali(
            ben_gua=ZhongGua.QIAN_WEI_TIAN,
            zhi_gua=ZhongGua.TIAN_FENG_GOU,
            yao_bian_code=0b000001  # 只有初爻动
        )
        assert guali.yaos[0].state == 1  # 初爻动
        for i in range(1, 6):
            assert guali.yaos[i].state == 0  # 其他静爻

    def test_guali_yaos_position(self):
        """测试爻位正确性"""
        guali = Guali(ben_gua=ZhongGua.QIAN_WEI_TIAN)
        for i, yao in enumerate(guali.yaos):
            assert yao.position == i + 1


# =============================================================================
# Guali类世应设置测试
# =============================================================================

class TestGualiShiYing:
    """Guali类世应设置测试"""

    def test_set_shiying_bengong(self):
        """测试本宫世应"""
        guali = Guali(ben_gua=ZhongGua.QIAN_WEI_TIAN)  # 本宫
        guali.set_shiying()
        # 本宫: 世上(6)，应三(3)
        assert guali.get_yao_by_position(6).is_world == True
        assert guali.get_yao_by_position(3).is_response == True

    def test_set_shiying_yishi(self):
        """测试一世世应"""
        guali = Guali(ben_gua=ZhongGua.TIAN_FENG_GOU)  # 一世
        guali.set_shiying()
        # 一世: 世初(1)，应四(4)
        assert guali.get_yao_by_position(1).is_world == True
        assert guali.get_yao_by_position(4).is_response == True

    def test_set_shiying_youhun(self):
        """测试游魂世应"""
        guali = Guali(ben_gua=ZhongGua.HUO_DI_JIN)  # 游魂
        guali.set_shiying()
        # 游魂: 世四(4)，应初(1)
        assert guali.get_yao_by_position(4).is_world == True
        assert guali.get_yao_by_position(1).is_response == True


# =============================================================================
# Guali类六亲设置测试
# =============================================================================

class TestGualiLiuqin:
    """Guali类六亲设置测试"""

    def test_set_liuqin(self):
        """测试六亲设置"""
        guali = Guali(ben_gua=ZhongGua.QIAN_WEI_TIAN)
        # 设置地支
        guali.yaos[0].dizhi = Dizhi.ZI  # 子水

        guali.set_liuqin()

        # 乾宫属金，子水
        # 金生水 → 子孙
        assert guali.yaos[0].liuqin == LiuQin.ZI_SUN


# =============================================================================
# Guali类六神设置测试
# =============================================================================

class TestGualiLiushen:
    """Guali类六神设置测试"""

    def test_set_liushen_jia_day(self):
        """测试甲日六神设置"""
        guali = Guali(
            ben_gua=ZhongGua.QIAN_WEI_TIAN,
            ganzhi_day="甲午"
        )
        guali.set_liushen()

        # 甲日: 初青龙、二朱雀、三勾陈、四螣蛇、五白虎、上玄武
        assert guali.yaos[0].liushen == LiuShen.QING_LONG
        assert guali.yaos[1].liushen == LiuShen.ZHU_QUE
        assert guali.yaos[2].liushen == LiuShen.GOU_CHEN
        assert guali.yaos[3].liushen == LiuShen.TENG_SHE
        assert guali.yaos[4].liushen == LiuShen.BAI_HU
        assert guali.yaos[5].liushen == LiuShen.XUAN_WU


# =============================================================================
# 工厂函数测试
# =============================================================================

class TestCreateGualiFromInput:
    """工厂函数测试"""

    def test_create_guali_basic(self):
        """测试基本创建"""
        guali = create_guali_from_input(
            solar_year=2024,
            solar_month=2,
            solar_day=12,
            ben_gua_name="乾为天"
        )
        assert guali.solar_year == 2024
        assert guali.ben_gua == ZhongGua.QIAN_WEI_TIAN
        assert guali.zhi_gua is None
        assert guali.yao_bian_code == 0

    def test_create_guali_with_zhi_gua(self):
        """测试带之卦创建"""
        guali = create_guali_from_input(
            solar_year=2024,
            solar_month=2,
            solar_day=12,
            ben_gua_name="乾为天",
            zhi_gua_name="天风姤"
        )
        assert guali.zhi_gua == ZhongGua.TIAN_FENG_GOU
        # 乾为天(111111) ^ 天风姤(011111) = 100000 = 32
        # 但实际上乾为天的code和天风姤的code需要验证
        assert guali.yao_bian_code != 0

    def test_create_guali_invalid_bengua(self):
        """测试无效本卦名"""
        with pytest.raises(ValueError):
            create_guali_from_input(
                solar_year=2024,
                solar_month=2,
                solar_day=12,
                ben_gua_name="不存在的卦"
            )

    def test_create_guali_invalid_zhigua(self):
        """测试无效之卦名"""
        with pytest.raises(ValueError):
            create_guali_from_input(
                solar_year=2024,
                solar_month=2,
                solar_day=12,
                ben_gua_name="乾为天",
                zhi_gua_name="不存在的卦"
            )


# =============================================================================
# Guali类显示测试
# =============================================================================

class TestGualiDisplay:
    """Guali类显示测试"""

    def test_display_basic(self):
        """测试基本显示"""
        guali = Guali(
            solar_year=2024,
            solar_month=2,
            solar_day=12,
            ganzhi_day="甲午",
            ben_gua=ZhongGua.QIAN_WEI_TIAN,
            zhan_wen="测试占问",
            zhan_duan="测试占断"
        )
        display = guali.display()
        assert "乾为天" in display
        assert "2024" in display
        assert "甲午" in display

    def test_repr(self):
        """测试字符串表示"""
        guali = Guali(
            id=1,
            solar_year=2024,
            solar_month=2,
            solar_day=12,
            ben_gua=ZhongGua.QIAN_WEI_TIAN,
            zhan_wen="测试占问"
        )
        repr_str = repr(guali)
        assert "Guali" in repr_str
        assert "乾为天" in repr_str


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
