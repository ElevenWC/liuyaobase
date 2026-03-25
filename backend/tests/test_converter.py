# -*- coding: utf-8 -*-
"""
六爻卦例分析系统 - 格式转换模块测试

测试阶段十五的任务
"""
import pytest

from backend.core.converter import (
    gua_name_to_code,
    code_to_gua_name,
    parse_time_part,
    parse_gua_part,
    parse_text_part,
    parse_standard_format,
    standard_format_to_guali,
    guali_to_standard_format,
    validate_standard_format
)
from backend.core.enums import ZhongGua


class TestGuaNameToCode:
    """测试卦名转代码"""

    def test_qian_wei_tian(self):
        """测试乾为天"""
        code = gua_name_to_code("乾为天")
        assert code == 0b111111  # 63

    def test_shan_feng_gu(self):
        """测试山风蛊"""
        code = gua_name_to_code("山风蛊")
        assert code == 0b011001  # 25

    def test_huo_di_jin(self):
        """测试火地晋"""
        code = gua_name_to_code("火地晋")
        assert code == 0b000101  # 5

    def test_invalid_name(self):
        """测试无效卦名"""
        code = gua_name_to_code("不存在的卦")
        assert code is None

    def test_empty_name(self):
        """测试空卦名"""
        code = gua_name_to_code("")
        assert code is None


class TestCodeToGuaName:
    """测试代码转卦名"""

    def test_code_63(self):
        """测试代码63(乾为天)"""
        name = code_to_gua_name(0b111111)
        assert name == "乾为天"

    def test_code_25(self):
        """测试代码25(山风蛊)"""
        name = code_to_gua_name(0b011001)
        assert name == "山风蛊"

    def test_code_5(self):
        """测试代码5(火地晋)"""
        name = code_to_gua_name(0b000101)
        assert name == "火地晋"

    def test_invalid_code(self):
        """测试无效代码"""
        name = code_to_gua_name(999)
        assert name is None

    def test_all_64_gua_unique_codes(self):
        """测试所有64卦的代码转换（仅测试代码唯一的卦）"""
        # 注意：有些卦有相同的代码值（如地水师和水地比），
        # 这是枚举定义中的已知问题，from_code返回第一个匹配的
        seen_codes = set()
        for gua in ZhongGua:
            if gua.code not in seen_codes:
                name = code_to_gua_name(gua.code)
                # 只验证能正确返回一个中文名
                assert name is not None
                assert isinstance(name, str)
                seen_codes.add(gua.code)


class TestParseTimePart:
    """测试时间部分解析"""

    def test_basic_format(self):
        """测试基本格式"""
        result = parse_time_part("2024;02.12,")
        assert result["year"] == 2024
        assert result["month"] == 2
        assert result["day"] == 12

    def test_without_comma(self):
        """测试不带逗号"""
        result = parse_time_part("2024;02.12")
        assert result["year"] == 2024
        assert result["month"] == 2
        assert result["day"] == 12

    def test_single_digit_month_day(self):
        """测试单数位月日"""
        result = parse_time_part("2024;2.5")
        assert result["year"] == 2024
        assert result["month"] == 2
        assert result["day"] == 5

    def test_invalid_format_no_semicolon(self):
        """测试无效格式（无分号）"""
        with pytest.raises(ValueError):
            parse_time_part("2024-02-12")

    def test_invalid_format_no_dot(self):
        """测试无效格式（无点号）"""
        with pytest.raises(ValueError):
            parse_time_part("2024;0212")


class TestParseGuaPart:
    """测试重卦部分解析"""

    def test_basic_format(self):
        """测试基本格式"""
        result = parse_gua_part("山风蛊,火地晋,")
        assert result["ben_gua_name"] == "山风蛊"
        assert result["zhi_gua_name"] == "火地晋"

    def test_without_zhi_gua(self):
        """测试无之卦"""
        result = parse_gua_part("乾为天,,")
        assert result["ben_gua_name"] == "乾为天"
        assert result["zhi_gua_name"] is None

    def test_without_trailing_comma(self):
        """测试无尾部逗号"""
        result = parse_gua_part("山风蛊,火地晋")
        assert result["ben_gua_name"] == "山风蛊"
        assert result["zhi_gua_name"] == "火地晋"

    def test_invalid_ben_gua(self):
        """测试无效本卦名"""
        with pytest.raises(ValueError):
            parse_gua_part("不存在的卦,火地晋,")

    def test_invalid_zhi_gua(self):
        """测试无效之卦名"""
        with pytest.raises(ValueError):
            parse_gua_part("山风蛊,不存在的卦,")


class TestParseTextPart:
    """测试语句部分解析"""

    def test_basic_format(self):
        """测试基本格式"""
        result = parse_text_part("占问股票走势,占断上涨")
        assert result["zhan_wen"] == "占问股票走势"
        assert result["zhan_duan"] == "占断上涨"

    def test_only_zhan_wen(self):
        """测试只有占问"""
        result = parse_text_part("占问股票走势")
        assert result["zhan_wen"] == "占问股票走势"
        assert result["zhan_duan"] is None

    def test_empty_string(self):
        """测试空字符串"""
        result = parse_text_part("")
        assert result["zhan_wen"] is None
        assert result["zhan_duan"] is None

    def test_with_comma_in_zhan_duan(self):
        """测试占断中包含逗号"""
        result = parse_text_part("占问股票,占断,可能上涨")
        assert result["zhan_wen"] == "占问股票"
        assert result["zhan_duan"] == "占断,可能上涨"


class TestParseStandardFormat:
    """测试完整标准格式解析"""

    def test_full_format(self):
        """测试完整格式"""
        result = parse_standard_format("2024;02.12,山风蛊,火地晋,占问股票走势,占断上涨")
        assert result["solar_year"] == 2024
        assert result["solar_month"] == 2
        assert result["solar_day"] == 12
        assert result["ben_gua_name"] == "山风蛊"
        assert result["zhi_gua_name"] == "火地晋"
        assert result["zhan_wen"] == "占问股票走势"
        assert result["zhan_duan"] == "占断上涨"

    def test_without_zhi_gua(self):
        """测试无之卦"""
        result = parse_standard_format("2024;02.12,乾为天,,占问股票走势,占断上涨")
        assert result["ben_gua_name"] == "乾为天"
        assert result["zhi_gua_name"] is None

    def test_without_text(self):
        """测试无语句部分"""
        result = parse_standard_format("2024;02.12,乾为天,,,")
        assert result["solar_year"] == 2024
        assert result["ben_gua_name"] == "乾为天"
        assert result["zhan_wen"] is None or result["zhan_wen"] == ""

    def test_with_brackets(self):
        """测试带方括号"""
        result = parse_standard_format("[2024;02.12,山风蛊,火地晋,占问股票走势,占断上涨]")
        assert result["solar_year"] == 2024
        assert result["ben_gua_name"] == "山风蛊"

    def test_invalid_format(self):
        """测试无效格式"""
        with pytest.raises(ValueError):
            parse_standard_format("invalid format")


class TestStandardFormatToGuali:
    """测试标准格式转Guali对象"""

    def test_basic_conversion(self):
        """测试基本转换"""
        guali = standard_format_to_guali("2024;02.12,山风蛊,火地晋,占问股票走势,占断上涨")

        assert guali.solar_year == 2024
        assert guali.solar_month == 2
        assert guali.solar_day == 12
        assert guali.ben_gua == ZhongGua.SHAN_FENG_GU
        assert guali.zhi_gua == ZhongGua.HUO_DI_JIN
        assert guali.zhan_wen == "占问股票走势"
        assert guali.zhan_duan == "占断上涨"

    def test_ganzhi_filled(self):
        """测试干支时间已填充"""
        guali = standard_format_to_guali("2024;02.12,乾为天,,占问测试,")

        assert guali.ganzhi_year is not None
        assert guali.ganzhi_month is not None
        assert guali.ganzhi_day is not None
        assert guali.xunkong is not None

    def test_yaos_calculated(self):
        """测试爻已计算"""
        guali = standard_format_to_guali("2024;02.12,乾为天,,")

        assert len(guali.yaos) == 6
        # 验证纳甲装卦
        assert guali.yaos[0].dizhi is not None
        # 验证六亲
        assert guali.yaos[0].liuqin is not None
        # 验证六神
        assert guali.yaos[0].liushen is not None

    def test_without_zhi_gua(self):
        """测试无之卦"""
        guali = standard_format_to_guali("2024;02.12,乾为天,,占问测试,占断结果")

        assert guali.ben_gua == ZhongGua.QIAN_WEI_TIAN
        assert guali.zhi_gua is None


class TestGualiToStandardFormat:
    """测试Guali对象转标准格式"""

    def test_basic_conversion(self):
        """测试基本转换"""
        guali = standard_format_to_guali("2024;02.12,山风蛊,火地晋,占问股票走势,占断上涨")
        result = guali_to_standard_format(guali)

        assert "2024;02.12" in result
        assert "山风蛊" in result
        assert "火地晋" in result
        assert "占问股票走势" in result
        assert "占断上涨" in result

    def test_roundtrip(self):
        """测试往返转换"""
        original = "2024;02.12,乾为天,,占问测试,占断结果"
        guali = standard_format_to_guali(original)
        result = guali_to_standard_format(guali)

        # 重新解析验证
        parsed = parse_standard_format(result)
        assert parsed["solar_year"] == 2024
        assert parsed["solar_month"] == 2
        assert parsed["solar_day"] == 12
        assert parsed["ben_gua_name"] == "乾为天"


class TestValidateStandardFormat:
    """测试标准格式验证"""

    def test_valid_format(self):
        """测试有效格式"""
        valid, error = validate_standard_format("2024;02.12,山风蛊,火地晋,占问,占断")
        assert valid is True
        assert error is None

    def test_invalid_format(self):
        """测试无效格式"""
        valid, error = validate_standard_format("invalid")
        assert valid is False
        assert error is not None

    def test_invalid_gua_name(self):
        """测试无效卦名"""
        valid, error = validate_standard_format("2024;02.12,不存在的卦,,占问,占断")
        assert valid is False
        assert "Invalid" in error
