"""
六爻卦例分析系统 - 六神计算模块测试

测试liushen模块的所有功能
"""
import pytest
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.core.enums import Tiangan, LiuShen
from backend.core.liushen import (
    LIUSHEN_ORDER,
    TIANGAN_LIUSHEN_OFFSET,
    LIUSHEN_MAP,
    get_liushen_by_tiangan,
    get_liushen_by_tiangan_and_position,
    get_liushen_by_tiangan_char,
    get_liushen_element,
    get_liushen_meaning
)


# =============================================================================
# 任务 6.1 - 六神映射表测试
# =============================================================================

class TestLiushenMappingTable:
    """六神映射表测试"""

    def test_liushen_order(self):
        """测试六神基础顺序"""
        assert len(LIUSHEN_ORDER) == 6
        assert LIUSHEN_ORDER[0] == LiuShen.QING_LONG
        assert LIUSHEN_ORDER[1] == LiuShen.ZHU_QUE
        assert LIUSHEN_ORDER[2] == LiuShen.GOU_CHEN
        assert LIUSHEN_ORDER[3] == LiuShen.TENG_SHE
        assert LIUSHEN_ORDER[4] == LiuShen.BAI_HU
        assert LIUSHEN_ORDER[5] == LiuShen.XUAN_WU

    def test_tiangan_offset_map(self):
        """测试日干偏移映射表"""
        # 甲乙日从青龙开始，偏移0
        assert TIANGAN_LIUSHEN_OFFSET[Tiangan.JIA] == 0
        assert TIANGAN_LIUSHEN_OFFSET[Tiangan.YI] == 0
        # 丙丁日从朱雀开始，偏移1
        assert TIANGAN_LIUSHEN_OFFSET[Tiangan.BING] == 1
        assert TIANGAN_LIUSHEN_OFFSET[Tiangan.DING] == 1
        # 庚辛日从白虎开始，偏移4
        assert TIANGAN_LIUSHEN_OFFSET[Tiangan.GENG] == 4
        assert TIANGAN_LIUSHEN_OFFSET[Tiangan.XIN] == 4
        # 壬癸日从玄武开始，偏移5
        assert TIANGAN_LIUSHEN_OFFSET[Tiangan.REN] == 5
        assert TIANGAN_LIUSHEN_OFFSET[Tiangan.GUI] == 5

    def test_liushen_map_completeness(self):
        """测试六神映射表完整性"""
        # 验证映射表包含所有日干组
        assert len(LIUSHEN_MAP) == 6

        # 验证每个映射都有6个六神
        for key, value in LIUSHEN_MAP.items():
            assert len(value) == 6


# =============================================================================
# 任务 6.2 - 根据日干计算六神测试
# =============================================================================

class TestGetLiushenByTiangan:
    """根据日干获取六神列表测试"""

    def test_jia_yi_day(self):
        """测试甲乙日六神"""
        # 甲乙日: 初青龙、二朱雀、三勾陈、四螣蛇、五白虎、上玄武
        result = get_liushen_by_tiangan(Tiangan.JIA)
        assert result[0] == LiuShen.QING_LONG  # 初爻青龙
        assert result[1] == LiuShen.ZHU_QUE    # 二爻朱雀
        assert result[2] == LiuShen.GOU_CHEN   # 三爻勾陈
        assert result[3] == LiuShen.TENG_SHE   # 四爻螣蛇
        assert result[4] == LiuShen.BAI_HU     # 五爻白虎
        assert result[5] == LiuShen.XUAN_WU    # 上爻玄武

        # 乙日应该和甲日相同
        result_yi = get_liushen_by_tiangan(Tiangan.YI)
        assert result == result_yi

    def test_bing_ding_day(self):
        """测试丙丁日六神"""
        # 丙丁日: 初朱雀、二勾陈、三螣蛇、四白虎、五玄武、上青龙
        result = get_liushen_by_tiangan(Tiangan.BING)
        assert result[0] == LiuShen.ZHU_QUE    # 初爻朱雀
        assert result[1] == LiuShen.GOU_CHEN   # 二爻勾陈
        assert result[2] == LiuShen.TENG_SHE   # 三爻螣蛇
        assert result[3] == LiuShen.BAI_HU     # 四爻白虎
        assert result[4] == LiuShen.XUAN_WU    # 五爻玄武
        assert result[5] == LiuShen.QING_LONG  # 上爻青龙

    def test_wu_day(self):
        """测试戊日六神"""
        # 戊日: 初勾陈、二螣蛇、三白虎、四玄武、五青龙、上朱雀
        result = get_liushen_by_tiangan(Tiangan.WU)
        assert result[0] == LiuShen.GOU_CHEN   # 初爻勾陈
        assert result[1] == LiuShen.TENG_SHE   # 二爻螣蛇
        assert result[2] == LiuShen.BAI_HU     # 三爻白虎
        assert result[3] == LiuShen.XUAN_WU    # 四爻玄武
        assert result[4] == LiuShen.QING_LONG  # 五爻青龙
        assert result[5] == LiuShen.ZHU_QUE    # 上爻朱雀

    def test_ji_day(self):
        """测试己日六神"""
        # 己日: 初螣蛇、二白虎、三玄武、四青龙、五朱雀、上勾陈
        result = get_liushen_by_tiangan(Tiangan.JI)
        assert result[0] == LiuShen.TENG_SHE   # 初爻螣蛇
        assert result[1] == LiuShen.BAI_HU     # 二爻白虎
        assert result[2] == LiuShen.XUAN_WU    # 三爻玄武
        assert result[3] == LiuShen.QING_LONG  # 四爻青龙
        assert result[4] == LiuShen.ZHU_QUE    # 五爻朱雀
        assert result[5] == LiuShen.GOU_CHEN   # 上爻勾陈

    def test_geng_xin_day(self):
        """测试庚辛日六神"""
        # 庚辛日: 初白虎、二玄武、三青龙、四朱雀、五勾陈、上螣蛇
        result = get_liushen_by_tiangan(Tiangan.GENG)
        assert result[0] == LiuShen.BAI_HU     # 初爻白虎
        assert result[1] == LiuShen.XUAN_WU    # 二爻玄武
        assert result[2] == LiuShen.QING_LONG  # 三爻青龙
        assert result[3] == LiuShen.ZHU_QUE    # 四爻朱雀
        assert result[4] == LiuShen.GOU_CHEN   # 五爻勾陈
        assert result[5] == LiuShen.TENG_SHE   # 上爻螣蛇

    def test_ren_gui_day(self):
        """测试壬癸日六神"""
        # 壬癸日: 初玄武、二青龙、三朱雀、四勾陈、五螣蛇、上白虎
        result = get_liushen_by_tiangan(Tiangan.REN)
        assert result[0] == LiuShen.XUAN_WU    # 初爻玄武
        assert result[1] == LiuShen.QING_LONG  # 二爻青龙
        assert result[2] == LiuShen.ZHU_QUE    # 三爻朱雀
        assert result[3] == LiuShen.GOU_CHEN   # 四爻勾陈
        assert result[4] == LiuShen.TENG_SHE   # 五爻螣蛇
        assert result[5] == LiuShen.BAI_HU     # 上爻白虎


class TestGetLiushenByTianganAndPosition:
    """根据日干和爻位获取六神测试"""

    def test_jia_day_all_positions(self):
        """测试甲日所有爻位"""
        assert get_liushen_by_tiangan_and_position(Tiangan.JIA, 1) == LiuShen.QING_LONG
        assert get_liushen_by_tiangan_and_position(Tiangan.JIA, 2) == LiuShen.ZHU_QUE
        assert get_liushen_by_tiangan_and_position(Tiangan.JIA, 3) == LiuShen.GOU_CHEN
        assert get_liushen_by_tiangan_and_position(Tiangan.JIA, 4) == LiuShen.TENG_SHE
        assert get_liushen_by_tiangan_and_position(Tiangan.JIA, 5) == LiuShen.BAI_HU
        assert get_liushen_by_tiangan_and_position(Tiangan.JIA, 6) == LiuShen.XUAN_WU

    def test_geng_day_all_positions(self):
        """测试庚日所有爻位"""
        assert get_liushen_by_tiangan_and_position(Tiangan.GENG, 1) == LiuShen.BAI_HU
        assert get_liushen_by_tiangan_and_position(Tiangan.GENG, 2) == LiuShen.XUAN_WU
        assert get_liushen_by_tiangan_and_position(Tiangan.GENG, 3) == LiuShen.QING_LONG
        assert get_liushen_by_tiangan_and_position(Tiangan.GENG, 4) == LiuShen.ZHU_QUE
        assert get_liushen_by_tiangan_and_position(Tiangan.GENG, 5) == LiuShen.GOU_CHEN
        assert get_liushen_by_tiangan_and_position(Tiangan.GENG, 6) == LiuShen.TENG_SHE

    def test_invalid_position(self):
        """测试无效爻位"""
        with pytest.raises(ValueError):
            get_liushen_by_tiangan_and_position(Tiangan.JIA, 0)
        with pytest.raises(ValueError):
            get_liushen_by_tiangan_and_position(Tiangan.JIA, 7)
        with pytest.raises(ValueError):
            get_liushen_by_tiangan_and_position(Tiangan.JIA, -1)


class TestGetLiushenByTianganChar:
    """根据日干字符获取六神测试"""

    def test_valid_tiangan_char(self):
        """测试有效日干字符"""
        result = get_liushen_by_tiangan_char("甲")
        assert result[0] == LiuShen.QING_LONG

        result = get_liushen_by_tiangan_char("庚")
        assert result[0] == LiuShen.BAI_HU

    def test_invalid_tiangan_char(self):
        """测试无效日干字符"""
        with pytest.raises(ValueError):
            get_liushen_by_tiangan_char("X")
        with pytest.raises(ValueError):
            get_liushen_by_tiangan_char("")


# =============================================================================
# 任务 6.3 - 卦例六神计算测试
# =============================================================================

class TestGualiLiushen:
    """卦例六神计算测试"""

    def test_set_liushen_jia_day(self):
        """测试甲日六神设置（完整测试）"""
        from backend.core.enums import ZhongGua
        from backend.core.models import Guali

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

    def test_set_liushen_geng_day(self):
        """测试庚日六神设置"""
        from backend.core.enums import ZhongGua
        from backend.core.models import Guali

        guali = Guali(
            ben_gua=ZhongGua.QIAN_WEI_TIAN,
            ganzhi_day="庚申"
        )
        guali.set_liushen()

        # 庚日: 初白虎、二玄武、三青龙、四朱雀、五勾陈、上螣蛇
        assert guali.yaos[0].liushen == LiuShen.BAI_HU
        assert guali.yaos[1].liushen == LiuShen.XUAN_WU
        assert guali.yaos[2].liushen == LiuShen.QING_LONG
        assert guali.yaos[3].liushen == LiuShen.ZHU_QUE
        assert guali.yaos[4].liushen == LiuShen.GOU_CHEN
        assert guali.yaos[5].liushen == LiuShen.TENG_SHE

    def test_set_liushen_ren_day(self):
        """测试壬日六神设置"""
        from backend.core.enums import ZhongGua
        from backend.core.models import Guali

        guali = Guali(
            ben_gua=ZhongGua.QIAN_WEI_TIAN,
            ganzhi_day="壬子"
        )
        guali.set_liushen()

        # 壬日: 初玄武、二青龙、三朱雀、四勾陈、五螣蛇、上白虎
        assert guali.yaos[0].liushen == LiuShen.XUAN_WU
        assert guali.yaos[1].liushen == LiuShen.QING_LONG
        assert guali.yaos[2].liushen == LiuShen.ZHU_QUE
        assert guali.yaos[3].liushen == LiuShen.GOU_CHEN
        assert guali.yaos[4].liushen == LiuShen.TENG_SHE
        assert guali.yaos[5].liushen == LiuShen.BAI_HU

    def test_set_liushen_no_day(self):
        """测试无日干时六神设置"""
        from backend.core.enums import ZhongGua
        from backend.core.models import Guali

        guali = Guali(ben_gua=ZhongGua.QIAN_WEI_TIAN)
        guali.set_liushen()

        # 无日干时，六神应该为None
        for yao in guali.yaos:
            assert yao.liushen is None


# =============================================================================
# 六神属性函数测试
# =============================================================================

class TestLiushenProperties:
    """六神属性函数测试"""

    def test_get_liushen_element(self):
        """测试获取六神五行属性"""
        assert get_liushen_element(LiuShen.QING_LONG) == "木"
        assert get_liushen_element(LiuShen.ZHU_QUE) == "火"
        assert get_liushen_element(LiuShen.GOU_CHEN) == "土"
        assert get_liushen_element(LiuShen.TENG_SHE) == "土"
        assert get_liushen_element(LiuShen.BAI_HU) == "金"
        assert get_liushen_element(LiuShen.XUAN_WU) == "水"

    def test_get_liushen_meaning(self):
        """测试获取六神含义"""
        assert "喜庆" in get_liushen_meaning(LiuShen.QING_LONG)
        assert "文书" in get_liushen_meaning(LiuShen.ZHU_QUE)
        assert "田土" in get_liushen_meaning(LiuShen.GOU_CHEN)
        assert "惊恐" in get_liushen_meaning(LiuShen.TENG_SHE)
        assert "凶险" in get_liushen_meaning(LiuShen.BAI_HU)
        assert "暗昧" in get_liushen_meaning(LiuShen.XUAN_WU)


# =============================================================================
# 所有日干六神验证测试
# =============================================================================

class TestAllTianganLiushen:
    """所有日干六神验证测试"""

    def test_all_tiangan_have_consistent_results(self):
        """测试所有日干的六神结果一致"""
        for tiangan in Tiangan:
            # 获取列表形式
            liushen_list = get_liushen_by_tiangan(tiangan)

            # 逐个爻位获取
            for pos in range(1, 7):
                liushen = get_liushen_by_tiangan_and_position(tiangan, pos)
                assert liushen == liushen_list[pos - 1]


# =============================================================================
# 集成测试 - calculate_all方法
# =============================================================================

class TestCalculateAll:
    """calculate_all方法集成测试"""

    def test_calculate_all_with_liuqin_liushen(self):
        """测试calculate_all包含六亲和六神计算"""
        from backend.core.enums import ZhongGua, LiuQin
        from backend.core.models import Guali

        guali = Guali(
            solar_year=2024,
            solar_month=2,
            solar_day=12,
            ganzhi_day="甲午",
            ben_gua=ZhongGua.QIAN_WEI_TIAN
        )
        guali.calculate_all()

        # 验证纳甲装卦
        assert all(yao.dizhi is not None for yao in guali.yaos)

        # 验证世应
        assert guali.world_yao is not None
        assert guali.response_yao is not None

        # 验证六亲
        assert all(yao.liuqin is not None for yao in guali.yaos)

        # 验证六神
        assert all(yao.liushen is not None for yao in guali.yaos)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
