# -*- coding: utf-8 -*-
"""
六爻卦例分析系统 - Pydantic模型测试

测试任务16.3和16.4的schemas
"""
import pytest
from pydantic import ValidationError

from backend.api.schemas import (
    GualiCreate,
    GualiUpdate,
    GualiResponse,
    GualiDetailResponse,
    YaoResponse,
    GualiListResponse,
    MessageResponse,
    ErrorResponse
)


class TestGualiCreate:
    """测试GualiCreate模型 - 任务16.3"""

    def test_create_with_required_fields(self):
        """测试只使用必填字段创建"""
        data = GualiCreate(
            solar_year=2024,
            solar_month=2,
            solar_day=12,
            ben_gua_name="乾为天"
        )
        assert data.solar_year == 2024
        assert data.solar_month == 2
        assert data.solar_day == 12
        assert data.ben_gua_name == "乾为天"
        assert data.zhi_gua_name is None
        assert data.zhan_wen is None

    def test_create_with_all_fields(self):
        """测试使用所有字段创建"""
        data = GualiCreate(
            solar_year=2024,
            solar_month=2,
            solar_day=12,
            ben_gua_name="山风蛊",
            zhi_gua_name="火地晋",
            zhan_wen="测试占问",
            zhan_duan="测试占断",
            image_path="/images/test.jpg"
        )
        assert data.solar_year == 2024
        assert data.ben_gua_name == "山风蛊"
        assert data.zhi_gua_name == "火地晋"
        assert data.zhan_wen == "测试占问"
        assert data.zhan_duan == "测试占断"
        assert data.image_path == "/images/test.jpg"

    def test_create_with_zhi_gua_none(self):
        """测试之卦为None"""
        data = GualiCreate(
            solar_year=2024,
            solar_month=2,
            solar_day=12,
            ben_gua_name="乾为天",
            zhi_gua_name=None
        )
        assert data.zhi_gua_name is None

    def test_create_missing_required_field(self):
        """测试缺少必填字段"""
        with pytest.raises(ValidationError):
            GualiCreate(
                solar_year=2024,
                solar_month=2,
                # 缺少solar_day
                ben_gua_name="乾为天"
            )

    def test_create_missing_ben_gua_name(self):
        """测试缺少本卦名"""
        with pytest.raises(ValidationError):
            GualiCreate(
                solar_year=2024,
                solar_month=2,
                solar_day=12
                # 缺少ben_gua_name
            )

    def test_create_invalid_year(self):
        """测试无效年份"""
        with pytest.raises(ValidationError):
            GualiCreate(
                solar_year=1800,  # 超出范围
                solar_month=2,
                solar_day=12,
                ben_gua_name="乾为天"
            )

    def test_create_invalid_month(self):
        """测试无效月份"""
        with pytest.raises(ValidationError):
            GualiCreate(
                solar_year=2024,
                solar_month=13,  # 超出范围
                solar_day=12,
                ben_gua_name="乾为天"
            )

    def test_create_invalid_day(self):
        """测试无效日期"""
        with pytest.raises(ValidationError):
            GualiCreate(
                solar_year=2024,
                solar_month=2,
                solar_day=32,  # 超出范围
                ben_gua_name="乾为天"
            )


class TestGualiUpdate:
    """测试GualiUpdate模型"""

    def test_update_zhan_wen(self):
        """测试更新占问"""
        data = GualiUpdate(zhan_wen="更新后的占问")
        assert data.zhan_wen == "更新后的占问"
        assert data.zhan_duan is None

    def test_update_zhan_duan(self):
        """测试更新占断"""
        data = GualiUpdate(zhan_duan="更新后的占断")
        assert data.zhan_duan == "更新后的占断"
        assert data.zhan_wen is None

    def test_update_both(self):
        """测试同时更新"""
        data = GualiUpdate(
            zhan_wen="新占问",
            zhan_duan="新占断"
        )
        assert data.zhan_wen == "新占问"
        assert data.zhan_duan == "新占断"

    def test_update_empty(self):
        """测试空更新"""
        data = GualiUpdate()
        assert data.zhan_wen is None
        assert data.zhan_duan is None


class TestGualiResponse:
    """测试GualiResponse模型 - 任务16.4"""

    def test_response_basic(self):
        """测试基本响应"""
        response = GualiResponse(
            id=1,
            solar_year=2024,
            solar_month=2,
            solar_day=12,
            ben_gua_name="乾为天"
        )
        assert response.id == 1
        assert response.solar_year == 2024
        assert response.ben_gua_name == "乾为天"

    def test_response_with_all_fields(self):
        """测试完整响应"""
        response = GualiResponse(
            id=1,
            solar_year=2024,
            solar_month=2,
            solar_day=12,
            ganzhi_year="甲辰",
            ganzhi_month="丙寅",
            ganzhi_day="甲午",
            xunkong="辰巳",
            ben_gua_name="山风蛊",
            zhi_gua_name="火地晋",
            ben_gua_code=11,  # 0b001011 = 11
            zhi_gua_code=5,   # 0b000101 = 5
            yao_bian_code=14,  # XOR = 0b001110 = 14
            gongwei="巽宫",
            gongwei_index="归魂",
            zhan_wen="占问股票走势",
            zhan_duan="占断上涨"
        )
        assert response.id == 1
        assert response.ganzhi_year == "甲辰"
        assert response.ganzhi_day == "甲午"
        assert response.xunkong == "辰巳"
        assert response.ben_gua_name == "山风蛊"
        assert response.zhi_gua_name == "火地晋"
        assert response.ben_gua_code == 11
        assert response.zhi_gua_code == 5
        assert response.yao_bian_code == 14
        assert response.gongwei == "巽宫"
        assert response.gongwei_index == "归魂"
        assert response.zhan_wen == "占问股票走势"
        assert response.zhan_duan == "占断上涨"

    def test_response_missing_id(self):
        """测试缺少ID"""
        with pytest.raises(ValidationError):
            GualiResponse(
                solar_year=2024,
                solar_month=2,
                solar_day=12
            )


class TestYaoResponse:
    """测试YaoResponse模型"""

    def test_yao_basic(self):
        """测试基本爻响应"""
        yao = YaoResponse(
            position=1,
            yao_type=1,
            state=0
        )
        assert yao.position == 1
        assert yao.yao_type == 1
        assert yao.state == 0

    def test_yao_with_all_fields(self):
        """测试完整爻响应"""
        yao = YaoResponse(
            position=1,
            yao_type=1,
            state=0,
            dizhi="子",
            liuqin="子孙",
            liushen="青龙",
            wuxing="水",
            is_world=True,
            is_response=False,
            position_name="初爻",
            yao_type_name="阳爻",
            state_name="静爻"
        )
        assert yao.dizhi == "子"
        assert yao.liuqin == "子孙"
        assert yao.liushen == "青龙"
        assert yao.wuxing == "水"
        assert yao.is_world is True
        assert yao.is_response is False
        assert yao.position_name == "初爻"

    def test_yao_invalid_position(self):
        """测试无效爻位"""
        with pytest.raises(ValidationError):
            YaoResponse(
                position=7,  # 超出范围
                yao_type=1,
                state=0
            )


class TestGualiDetailResponse:
    """测试GualiDetailResponse模型"""

    def test_detail_response(self):
        """测试详情响应"""
        yaos = [
            YaoResponse(position=1, yao_type=1, state=0, dizhi="子"),
            YaoResponse(position=2, yao_type=0, state=0, dizhi="寅"),
            YaoResponse(position=3, yao_type=1, state=0, dizhi="辰"),
            YaoResponse(position=4, yao_type=1, state=0, dizhi="午"),
            YaoResponse(position=5, yao_type=0, state=0, dizhi="申"),
            YaoResponse(position=6, yao_type=1, state=0, dizhi="戌"),
        ]

        response = GualiDetailResponse(
            id=1,
            solar_year=2024,
            solar_month=2,
            solar_day=12,
            ben_gua_name="乾为天",
            yaos=yaos,
            fushen={"has_fushen": False},
            fanyin_fuyin={"has_fanyin": False, "has_fuyin": False},
            shensha={"干禄": {"dizhi": "寅", "is_in_gua": True}},
            shengwang_mujue={}
        )

        assert response.id == 1
        assert len(response.yaos) == 6
        assert response.yaos[0].dizhi == "子"
        assert response.fushen["has_fushen"] is False


class TestGualiListResponse:
    """测试GualiListResponse模型"""

    def test_list_response(self):
        """测试列表响应"""
        items = [
            GualiResponse(id=1, solar_year=2024, solar_month=2, solar_day=12, ben_gua_name="乾为天"),
            GualiResponse(id=2, solar_year=2024, solar_month=2, solar_day=13, ben_gua_name="坤为地"),
        ]

        response = GualiListResponse(
            items=items,
            total=100,
            page=1,
            page_size=10,
            pages=10
        )

        assert len(response.items) == 2
        assert response.total == 100
        assert response.page == 1
        assert response.page_size == 10
        assert response.pages == 10


class TestMessageResponse:
    """测试MessageResponse模型"""

    def test_message_response(self):
        """测试消息响应"""
        response = MessageResponse(message="操作成功", success=True)
        assert response.message == "操作成功"
        assert response.success is True

    def test_error_message(self):
        """测试错误消息"""
        response = MessageResponse(message="操作失败", success=False)
        assert response.message == "操作失败"
        assert response.success is False


class TestErrorResponse:
    """测试ErrorResponse模型"""

    def test_error_response(self):
        """测试错误响应"""
        response = ErrorResponse(detail="卦例不存在", code="NOT_FOUND")
        assert response.detail == "卦例不存在"
        assert response.code == "NOT_FOUND"

    def test_error_response_no_code(self):
        """测试无代码的错误响应"""
        response = ErrorResponse(detail="未知错误")
        assert response.detail == "未知错误"
        assert response.code is None
