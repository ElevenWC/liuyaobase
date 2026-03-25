# -*- coding: utf-8 -*-
"""
测试 validators.py - CSV验证模块

阶段十九: CSV导入功能测试
"""
import pytest
from backend.utils.validators import (
    validate_time_format,
    validate_gua_name,
    validate_csv_row,
    validate_csv_format,
    validate_csv_file,
    parse_csv_to_guali_inputs
)


class TestValidateTimeFormat:
    """测试时间格式验证"""

    def test_valid_time_format(self):
        """测试有效的时间格式"""
        valid, error, data = validate_time_format("2024;02.12")
        assert valid is True
        assert error is None
        assert data == {"year": 2024, "month": 2, "day": 12}

    def test_valid_time_format_single_digit(self):
        """测试单数位的月日"""
        valid, error, data = validate_time_format("2024;2.5")
        assert valid is True
        assert error is None
        assert data == {"year": 2024, "month": 2, "day": 5}

    def test_invalid_time_format_no_semicolon(self):
        """测试无效格式 - 无分号"""
        valid, error, data = validate_time_format("2024.02.12")
        assert valid is False
        assert "时间格式错误" in error

    def test_invalid_time_format_wrong_separator(self):
        """测试无效格式 - 错误分隔符"""
        valid, error, data = validate_time_format("2024-02-12")
        assert valid is False

    def test_invalid_year_too_early(self):
        """测试无效年份 - 太早"""
        valid, error, data = validate_time_format("1800;02.12")
        assert valid is False
        assert "年份" in error

    def test_invalid_year_too_late(self):
        """测试无效年份 - 太晚"""
        valid, error, data = validate_time_format("2200;02.12")
        assert valid is False
        assert "年份" in error

    def test_invalid_month(self):
        """测试无效月份"""
        valid, error, data = validate_time_format("2024;13.12")
        assert valid is False
        assert "月份" in error

    def test_invalid_day(self):
        """测试无效日期"""
        valid, error, data = validate_time_format("2024;02.32")
        assert valid is False
        assert "日期" in error


class TestValidateGuaName:
    """测试卦名验证"""

    def test_valid_gua_name(self):
        """测试有效的卦名"""
        valid, error, gua = validate_gua_name("乾为天")
        assert valid is True
        assert error is None
        assert gua is not None
        assert gua.gua_name == "乾为天"

    def test_valid_gua_name_shan_feng_gu(self):
        """测试山风蛊"""
        valid, error, gua = validate_gua_name("山风蛊")
        assert valid is True
        assert gua is not None

    def test_empty_gua_name_allowed(self):
        """测试空卦名（允许）"""
        valid, error, gua = validate_gua_name("", allow_empty=True)
        assert valid is True
        assert gua is None

    def test_empty_gua_name_not_allowed(self):
        """测试空卦名（不允许）"""
        valid, error, gua = validate_gua_name("", allow_empty=False)
        assert valid is False
        assert "不能为空" in error

    def test_invalid_gua_name(self):
        """测试无效卦名"""
        valid, error, gua = validate_gua_name("不存在的卦")
        assert valid is False
        assert "无效" in error


class TestValidateCsvRow:
    """测试CSV行验证"""

    def test_valid_row_full(self):
        """测试完整的有效行"""
        row = ["2024;02.12", "乾为天", "坤为地", "占问股票", "占断上涨", "test.jpg"]
        result = validate_csv_row(row, 1)
        assert result["valid"] is True
        assert len(result["errors"]) == 0
        assert result["data"]["solar_year"] == 2024
        assert result["data"]["ben_gua_name"] == "乾为天"
        assert result["data"]["zhi_gua_name"] == "坤为地"

    def test_valid_row_minimal(self):
        """测试最小有效行（只有时间和本卦）"""
        row = ["2024;02.12", "乾为天"]
        result = validate_csv_row(row, 1)
        assert result["valid"] is True
        assert result["data"]["zhi_gua_name"] is None

    def test_valid_row_with_empty_zhi_gua(self):
        """测试之卦为空"""
        row = ["2024;02.12", "乾为天", "", "占问", "", ""]
        result = validate_csv_row(row, 1)
        assert result["valid"] is True
        assert result["data"]["zhi_gua_name"] is None

    def test_invalid_row_no_columns(self):
        """测试列数不足"""
        row = ["2024;02.12"]
        result = validate_csv_row(row, 1)
        assert result["valid"] is False
        assert "列数不足" in result["errors"][0]

    def test_invalid_row_bad_time(self):
        """测试时间格式错误"""
        row = ["2024-02-12", "乾为天"]
        result = validate_csv_row(row, 1)
        assert result["valid"] is False

    def test_invalid_row_bad_ben_gua(self):
        """测试本卦名错误"""
        row = ["2024;02.12", "不存在的卦"]
        result = validate_csv_row(row, 1)
        assert result["valid"] is False


class TestValidateCsvFormat:
    """测试CSV格式验证"""

    def test_valid_csv_single_row(self):
        """测试单行有效CSV"""
        csv_content = "2024;02.12,乾为天,,占问,"
        result = validate_csv_format(csv_content)
        assert result["valid"] is True
        assert result["valid_rows"] == 1
        assert result["invalid_rows"] == 0
        assert len(result["data"]) == 1

    def test_valid_csv_multiple_rows(self):
        """测试多行有效CSV"""
        csv_content = """2024;02.12,乾为天,,占问1,
2024;03.15,坤为地,,占问2,
2024;04.20,山风蛊,火地晋,占问3,"""
        result = validate_csv_format(csv_content)
        assert result["valid"] is True
        assert result["valid_rows"] == 3

    def test_csv_with_invalid_rows(self):
        """测试包含无效行的CSV"""
        csv_content = """2024;02.12,乾为天,,占问,
2024-03-15,坤为地,,占问,
2024;04.20,山风蛊,火地晋,占问,"""
        result = validate_csv_format(csv_content)
        assert result["valid"] is False
        assert result["valid_rows"] == 2
        assert result["invalid_rows"] == 1

    def test_empty_csv(self):
        """测试空CSV"""
        result = validate_csv_format("")
        assert result["valid"] is False
        assert "为空" in result["errors"][0]


class TestValidateCsvFile:
    """测试CSV文件验证"""

    def test_valid_csv_file_utf8(self):
        """测试UTF-8编码的CSV文件"""
        content = "2024;02.12,乾为天,,占问,".encode("utf-8")
        result = validate_csv_file(content)
        assert result["valid"] is True
        assert result["encoding"] == "utf-8"

    def test_valid_csv_file_gbk(self):
        """测试GBK编码的CSV文件"""
        content = "2024;02.12,乾为天,,占问,".encode("gbk")
        result = validate_csv_file(content)
        assert result["valid"] is True
        assert result["encoding"] == "gbk"

    def test_valid_csv_file_with_bom(self):
        """测试带BOM的UTF-8编码CSV文件"""
        # 创建带BOM的UTF-8文件内容（用utf-8-sig编码会自动添加BOM）
        content = "2024;02.12,乾为天,,占问,".encode("utf-8-sig")
        result = validate_csv_file(content)
        assert result["valid"] is True


class TestParseCsvToGualiInputs:
    """测试CSV解析为卦例输入"""

    def test_parse_valid_csv(self):
        """测试解析有效CSV"""
        csv_content = "2024;02.12,乾为天,,占问股票,"
        data, errors = parse_csv_to_guali_inputs(csv_content)
        assert len(errors) == 0
        assert len(data) == 1
        assert data[0]["solar_year"] == 2024
        assert data[0]["ben_gua_name"] == "乾为天"

    def test_parse_csv_with_errors(self):
        """测试解析包含错误的CSV"""
        csv_content = """2024;02.12,乾为天,,占问,
2024-03-15,坤为地,,占问,"""
        data, errors = parse_csv_to_guali_inputs(csv_content)
        assert len(errors) > 0
        assert len(data) == 1  # 只有一行有效
