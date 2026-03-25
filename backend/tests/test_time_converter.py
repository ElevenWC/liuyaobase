"""
六爻卦例分析系统 - 时间转换模块测试

测试time_converter模块的所有功能
"""
import pytest
import sys
import os
from datetime import date

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.core.time_converter import (
    solar_to_ganzhi_year,
    solar_to_ganzhi_month,
    solar_to_ganzhi_day,
    get_xunkong,
    solar_to_ganzhi_full,
    extract_tiangan_dizhi_from_ganzhi,
    extract_tiangan_enum_from_ganzhi,
    extract_dizhi_enum_from_ganzhi,
    get_day_tiangan,
    get_day_dizhi,
    convert_date_to_ganzhi,
    validate_ganzhi,
    check_lunar_available,
    LUNAR_AVAILABLE
)
from backend.core.enums import Tiangan, Dizhi


# =============================================================================
# 任务 3.1 - 集成lunar-python库测试
# =============================================================================

class TestLunarPythonIntegration:
    """lunar-python库集成测试"""

    def test_lunar_available(self):
        """测试lunar-python库是否可用"""
        assert check_lunar_available() == True, "lunar-python库未安装"

    def test_lunar_basic_usage(self):
        """测试lunar-python基本用法"""
        if not LUNAR_AVAILABLE:
            pytest.skip("lunar-python库未安装")

        from lunar_python import Solar
        solar = Solar.fromYmd(2024, 2, 12)
        lunar = solar.getLunar()

        assert lunar.getYearInGanZhi() is not None
        assert lunar.getMonthInGanZhi() is not None
        assert lunar.getDayInGanZhi() is not None


# =============================================================================
# 任务 3.2 - 公历转干支年柱测试
# =============================================================================

class TestSolarToGanzhiYear:
    """公历转年柱干支测试"""

    def test_year_2024(self):
        """测试2024年年柱"""
        # 2024年是甲辰年
        result = solar_to_ganzhi_year(2024)
        assert result == "甲辰"

    def test_year_2025(self):
        """测试2025年年柱"""
        # 2025年是乙巳年
        result = solar_to_ganzhi_year(2025)
        assert result == "乙巳"

    def test_year_2020(self):
        """测试2020年年柱"""
        # 2020年是庚子年
        result = solar_to_ganzhi_year(2020)
        assert result == "庚子"

    def test_year_1984(self):
        """测试1984年年柱（甲子年，60年周期开始）"""
        result = solar_to_ganzhi_year(1984)
        assert result == "甲子"


# =============================================================================
# 任务 3.3 - 公历转干支月柱测试
# =============================================================================

class TestSolarToGanzhiMonth:
    """公历转月柱干支测试"""

    def test_month_2024_2(self):
        """测试2024年2月月柱"""
        # 2024年2月是丙寅月
        result = solar_to_ganzhi_month(2024, 2)
        assert result == "丙寅"

    def test_month_2024_1(self):
        """测试2024年1月月柱"""
        result = solar_to_ganzhi_month(2024, 1)
        assert result is not None
        assert len(result) == 2

    def test_month_2024_12(self):
        """测试2024年12月月柱"""
        result = solar_to_ganzhi_month(2024, 12)
        assert result is not None
        assert len(result) == 2


# =============================================================================
# 任务 3.4 - 公历转干支日柱测试
# =============================================================================

class TestSolarToGanzhiDay:
    """公历转日柱干支测试"""

    def test_day_2024_2_12(self):
        """测试2024年2月12日日柱"""
        # 2024年2月12日是丙午日
        result = solar_to_ganzhi_day(2024, 2, 12)
        assert result == "丙午"

    def test_day_2024_2_13(self):
        """测试2024年2月13日日柱"""
        # 日柱每天递增
        result = solar_to_ganzhi_day(2024, 2, 13)
        assert result == "丁未"

    def test_day_format(self):
        """测试日柱格式"""
        result = solar_to_ganzhi_day(2024, 2, 12)
        assert len(result) == 2
        assert result[0] in "甲乙丙丁戊己庚辛壬癸"
        assert result[1] in "子丑寅卯辰巳午未申酉戌亥"


# =============================================================================
# 任务 3.5 - 旬空计算测试
# =============================================================================

class TestGetXunkong:
    """旬空计算测试"""

    def test_xunkong_2024_2_12(self):
        """测试2024年2月12日旬空"""
        # 甲午日，甲午旬的旬空是辰巳
        result = get_xunkong(2024, 2, 12)
        assert result is not None
        assert len(result) == 2

    def test_xunkong_not_empty(self):
        """测试旬空不为空"""
        result = get_xunkong(2024, 2, 15)
        assert result is not None
        assert len(result) == 2

    def test_xunkong_format(self):
        """测试旬空格式"""
        result = get_xunkong(2024, 3, 1)
        # 旬空应该是两个地支
        assert result[0] in "子丑寅卯辰巳午未申酉戌亥"
        assert result[1] in "子丑寅卯辰巳午未申酉戌亥"


# =============================================================================
# 任务 3.6 - 完整时间转换测试
# =============================================================================

class TestSolarToGanzhiFull:
    """完整时间转换测试"""

    def test_full_2024_2_12(self):
        """测试2024年2月12日完整转换"""
        result = solar_to_ganzhi_full(2024, 2, 12)

        assert "year" in result
        assert "month" in result
        assert "day" in result
        assert "xunkong" in result

        assert result["year"] == "甲辰"
        assert result["day"] == "丙午"

    def test_full_result_format(self):
        """测试完整转换结果格式"""
        result = solar_to_ganzhi_full(2024, 2, 12)

        # 年柱两个字
        assert len(result["year"]) == 2
        # 月柱两个字
        assert len(result["month"]) == 2
        # 日柱两个字
        assert len(result["day"]) == 2
        # 旬空两个字
        assert len(result["xunkong"]) == 2

    def test_full_consistency(self):
        """测试完整转换与单独转换的一致性"""
        year, month, day = 2024, 5, 20

        full_result = solar_to_ganzhi_full(year, month, day)

        assert full_result["year"] == solar_to_ganzhi_year(year)
        assert full_result["month"] == solar_to_ganzhi_month(year, month)
        assert full_result["day"] == solar_to_ganzhi_day(year, month, day)
        assert full_result["xunkong"] == get_xunkong(year, month, day)


# =============================================================================
# 任务 3.7 - 日干日支提取测试
# =============================================================================

class TestExtractTianganDizhi:
    """日干日支提取测试"""

    def test_extract_tiangan_dizhi(self):
        """测试从干支字符串提取天干地支"""
        tiangan, dizhi = extract_tiangan_dizhi_from_ganzhi("甲午")
        assert tiangan == "甲"
        assert dizhi == "午"

    def test_extract_tiangan_dizhi_yisi(self):
        """测试乙巳"""
        tiangan, dizhi = extract_tiangan_dizhi_from_ganzhi("乙巳")
        assert tiangan == "乙"
        assert dizhi == "巳"

    def test_extract_tiangan_enum(self):
        """测试提取天干枚举"""
        tiangan = extract_tiangan_enum_from_ganzhi("甲午")
        assert tiangan == Tiangan.JIA

    def test_extract_dizhi_enum(self):
        """测试提取地支枚举"""
        dizhi = extract_dizhi_enum_from_ganzhi("甲午")
        assert dizhi == Dizhi.WU

    def test_extract_invalid_ganzhi(self):
        """测试无效干支字符串"""
        with pytest.raises(ValueError):
            extract_tiangan_dizhi_from_ganzhi("")


# =============================================================================
# 便捷函数测试
# =============================================================================

class TestConvenienceFunctions:
    """便捷函数测试"""

    def test_get_day_tiangan(self):
        """测试获取日干"""
        tiangan = get_day_tiangan(2024, 2, 12)
        assert tiangan == Tiangan.BING

    def test_get_day_dizhi(self):
        """测试获取日支"""
        dizhi = get_day_dizhi(2024, 2, 12)
        assert dizhi == Dizhi.WU

    def test_convert_date_to_ganzhi(self):
        """测试date对象转换"""
        solar_date = date(2024, 2, 12)
        result = convert_date_to_ganzhi(solar_date)

        assert result["year"] == "甲辰"
        assert result["day"] == "丙午"


# =============================================================================
# 验证函数测试
# =============================================================================

class TestValidateGanzhi:
    """验证函数测试"""

    def test_validate_valid_ganzhi(self):
        """测试有效干支"""
        assert validate_ganzhi("甲子") == True
        assert validate_ganzhi("乙丑") == True
        assert validate_ganzhi("癸亥") == True

    def test_validate_invalid_ganzhi(self):
        """测试无效干支"""
        assert validate_ganzhi("") == False
        assert validate_ganzhi("甲") == False
        assert validate_ganzhi("甲子乙") == False
        assert validate_ganzhi("XX") == False


# =============================================================================
# 边界条件测试
# =============================================================================

class TestBoundaryConditions:
    """边界条件测试"""

    def test_year_boundary(self):
        """测试年份边界"""
        # 测试不同年份
        result = solar_to_ganzhi_year(1900)
        assert result is not None

        result = solar_to_ganzhi_year(2100)
        assert result is not None

    def test_month_boundary(self):
        """测试月份边界"""
        # 1月
        result = solar_to_ganzhi_month(2024, 1)
        assert result is not None

        # 12月
        result = solar_to_ganzhi_month(2024, 12)
        assert result is not None

    def test_day_boundary(self):
        """测试日期边界"""
        # 月初
        result = solar_to_ganzhi_day(2024, 2, 1)
        assert result is not None

        # 月末（2024年是闰年，2月有29天）
        result = solar_to_ganzhi_day(2024, 2, 29)
        assert result is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
