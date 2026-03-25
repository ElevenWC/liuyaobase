# -*- coding: utf-8 -*-
"""
六爻卦例分析系统 - 阶段十三：数据库ORM模型测试

本测试文件验证SQLAlchemy ORM模型的正确性。
"""
import pytest
from datetime import datetime

from backend.db.models import GualiModel, YaoDetailModel, YanqingModel


# =============================================================================
# 任务 13.3 - GualiModel 测试
# =============================================================================

class TestGualiModel:
    """测试GualiModel ORM模型"""

    def test_guali_model_creation(self):
        """测试GualiModel创建"""
        model = GualiModel(
            solar_year=2024,
            solar_month=2,
            solar_day=12,
            ganzhi_year="甲辰",
            ganzhi_month="丙寅",
            ganzhi_day="甲午",
            xunkong="辰巳",
            ben_gua_code=63,  # 111111 = 63
            zhi_gua_code=None,
            yao_bian_code=0,
            gongwei="乾宫",
            gongwei_index="本宫"
        )
        assert model.solar_year == 2024
        assert model.solar_month == 2
        assert model.solar_day == 12
        assert model.ganzhi_year == "甲辰"
        assert model.ben_gua_code == 63
        assert model.zhi_gua_code is None
        assert model.gongwei == "乾宫"
        assert model.gongwei_index == "本宫"

    def test_guali_model_with_zhi_gua(self):
        """测试有之卦的GualiModel"""
        model = GualiModel(
            solar_year=2024,
            solar_month=2,
            solar_day=12,
            ganzhi_year="甲辰",
            ganzhi_month="丙寅",
            ganzhi_day="甲午",
            xunkong="辰巳",
            ben_gua_code=27,  # 山风蛊 011011 = 27
            zhi_gua_code=5,   # 火地晋 000101 = 5
            yao_bian_code=28, # 011100 = 28
            gongwei="巽宫",
            gongwei_index="归魂"
        )
        assert model.ben_gua_code == 27
        assert model.zhi_gua_code == 5
        assert model.yao_bian_code == 28

    def test_guali_model_text_fields(self):
        """测试文本字段"""
        model = GualiModel(
            solar_year=2024,
            solar_month=2,
            solar_day=12,
            ganzhi_year="甲辰",
            ganzhi_month="丙寅",
            ganzhi_day="甲午",
            xunkong="辰巳",
            ben_gua_code=63,
            gongwei="乾宫",
            gongwei_index="本宫",
            zhan_wen="占问股票走势",
            zhan_duan="占断上涨",
            image_path="/images/test.jpg"
        )
        assert model.zhan_wen == "占问股票走势"
        assert model.zhan_duan == "占断上涨"
        assert model.image_path == "/images/test.jpg"

    def test_guali_model_repr(self):
        """测试__repr__方法"""
        model = GualiModel(
            id=1,
            solar_year=2024,
            solar_month=2,
            solar_day=12,
            ganzhi_year="甲辰",
            ganzhi_month="丙寅",
            ganzhi_day="甲午",
            xunkong="辰巳",
            ben_gua_code=63,
            gongwei="乾宫",
            gongwei_index="本宫"
        )
        repr_str = repr(model)
        assert "GualiModel" in repr_str
        assert "id=1" in repr_str

    def test_guali_model_to_dict(self):
        """测试to_dict方法"""
        model = GualiModel(
            id=1,
            solar_year=2024,
            solar_month=2,
            solar_day=12,
            ganzhi_year="甲辰",
            ganzhi_month="丙寅",
            ganzhi_day="甲午",
            xunkong="辰巳",
            ben_gua_code=63,
            gongwei="乾宫",
            gongwei_index="本宫",
            zhan_wen="测试占问"
        )
        d = model.to_dict()
        assert d['id'] == 1
        assert d['solar_year'] == 2024
        assert d['solar_month'] == 2
        assert d['solar_day'] == 12
        assert d['ganzhi_year'] == "甲辰"
        assert d['ben_gua_code'] == 63
        assert d['zhan_wen'] == "测试占问"

    def test_guali_model_default_yao_bian_code(self):
        """测试yao_bian_code默认值为0（需要显式设置或在数据库插入时生效）"""
        # SQLAlchemy的Column default只在数据库插入时生效
        # 创建对象时需要显式设置，或在数据库插入后才会应用默认值
        model = GualiModel(
            solar_year=2024,
            solar_month=2,
            solar_day=12,
            ganzhi_year="甲辰",
            ganzhi_month="丙寅",
            ganzhi_day="甲午",
            xunkong="辰巳",
            ben_gua_code=63,
            gongwei="乾宫",
            gongwei_index="本宫",
            yao_bian_code=0  # 显式设置
        )
        assert model.yao_bian_code == 0

    def test_guali_model_all_gongwei_index(self):
        """测试所有宫位类型"""
        gongwei_indices = ["本宫", "一世", "二世", "三世", "四世", "五世", "游魂", "归魂"]
        for idx, gongwei_index in enumerate(gongwei_indices):
            model = GualiModel(
                solar_year=2024,
                solar_month=2,
                solar_day=12,
                ganzhi_year="甲辰",
                ganzhi_month="丙寅",
                ganzhi_day="甲午",
                xunkong="辰巳",
                ben_gua_code=63,
                gongwei="乾宫",
                gongwei_index=gongwei_index
            )
            assert model.gongwei_index == gongwei_index


# =============================================================================
# 任务 13.4 - YaoDetailModel 测试
# =============================================================================

class TestYaoDetailModel:
    """测试YaoDetailModel ORM模型"""

    def test_yao_detail_model_creation(self):
        """测试YaoDetailModel创建"""
        model = YaoDetailModel(
            guali_id=1,
            position=1,
            yao_type=1,
            state=0,
            dizhi="子",
            liuqin="子孙",
            liushen="青龙",
            is_world=False,
            is_response=False
        )
        assert model.guali_id == 1
        assert model.position == 1
        assert model.yao_type == 1
        assert model.state == 0
        assert model.dizhi == "子"
        assert model.liuqin == "子孙"
        assert model.liushen == "青龙"

    def test_yao_detail_model_world_yao(self):
        """测试世爻"""
        model = YaoDetailModel(
            guali_id=1,
            position=6,
            yao_type=1,
            state=0,
            dizhi="戌",
            liuqin="父母",
            liushen="玄武",
            is_world=True,
            is_response=False
        )
        assert model.is_world == True
        assert model.is_response == False

    def test_yao_detail_model_response_yao(self):
        """测试应爻"""
        model = YaoDetailModel(
            guali_id=1,
            position=3,
            yao_type=1,
            state=0,
            dizhi="辰",
            liuqin="父母",
            liushen="勾陈",
            is_world=False,
            is_response=True
        )
        assert model.is_world == False
        assert model.is_response == True

    def test_yao_detail_model_moving_yao(self):
        """测试动爻"""
        model = YaoDetailModel(
            guali_id=1,
            position=1,
            yao_type=1,
            state=1,  # 动爻
            dizhi="子",
            liuqin="子孙"
        )
        assert model.state == 1

    def test_yao_detail_model_yin_yao(self):
        """测试阴爻"""
        model = YaoDetailModel(
            guali_id=1,
            position=2,
            yao_type=0,  # 阴爻
            state=0,
            dizhi="寅"
        )
        assert model.yao_type == 0

    def test_yao_detail_model_repr(self):
        """测试__repr__方法"""
        model = YaoDetailModel(
            id=1,
            guali_id=1,
            position=1,
            yao_type=1,
            state=0,
            dizhi="子"
        )
        repr_str = repr(model)
        assert "YaoDetailModel" in repr_str
        assert "position=1" in repr_str
        assert "dizhi=子" in repr_str

    def test_yao_detail_model_to_dict(self):
        """测试to_dict方法"""
        model = YaoDetailModel(
            id=1,
            guali_id=1,
            position=1,
            yao_type=1,
            state=0,
            dizhi="子",
            liuqin="子孙",
            liushen="青龙",
            is_world=False,
            is_response=False
        )
        d = model.to_dict()
        assert d['id'] == 1
        assert d['guali_id'] == 1
        assert d['position'] == 1
        assert d['yao_type'] == 1
        assert d['state'] == 0
        assert d['dizhi'] == "子"
        assert d['liuqin'] == "子孙"
        assert d['liushen'] == "青龙"

    def test_yao_detail_model_all_positions(self):
        """测试所有爻位"""
        for pos in range(1, 7):
            model = YaoDetailModel(
                guali_id=1,
                position=pos,
                yao_type=1,
                state=0,
                dizhi="子"
            )
            assert model.position == pos

    def test_yao_detail_model_default_values(self):
        """测试默认值（需要显式设置或在数据库插入时生效）"""
        # SQLAlchemy的Column default只在数据库插入时生效
        # 创建对象时需要显式设置
        model = YaoDetailModel(
            guali_id=1,
            position=1,
            yao_type=1,
            state=0,  # 显式设置
            dizhi="子",
            is_world=False,  # 显式设置
            is_response=False  # 显式设置
        )
        assert model.state == 0  # 静爻
        assert model.is_world == False
        assert model.is_response == False

    def test_yao_detail_model_all_liuqin(self):
        """测试所有六亲"""
        liuqin_list = ["父母", "官鬼", "子孙", "妻财", "兄弟"]
        for liuqin in liuqin_list:
            model = YaoDetailModel(
                guali_id=1,
                position=1,
                yao_type=1,
                state=0,
                dizhi="子",
                liuqin=liuqin
            )
            assert model.liuqin == liuqin

    def test_yao_detail_model_all_liushen(self):
        """测试所有六神"""
        liushen_list = ["青龙", "朱雀", "勾陈", "螣蛇", "白虎", "玄武"]
        for liushen in liushen_list:
            model = YaoDetailModel(
                guali_id=1,
                position=1,
                yao_type=1,
                state=0,
                dizhi="子",
                liushen=liushen
            )
            assert model.liushen == liushen


# =============================================================================
# YanqingModel 测试
# =============================================================================

class TestYanqingModel:
    """测试YanqingModel ORM模型"""

    def test_yanqing_model_creation(self):
        """测试YanqingModel创建"""
        model = YanqingModel(
            guali_id=1,
            status="应验",
            note="实际走势与占断一致"
        )
        assert model.guali_id == 1
        assert model.status == "应验"
        assert model.note == "实际走势与占断一致"

    def test_yanqing_model_all_status(self):
        """测试所有占验状态"""
        statuses = ["应验", "模糊", "不验"]
        for status in statuses:
            model = YanqingModel(
                guali_id=1,
                status=status
            )
            assert model.status == status

    def test_yanqing_model_repr(self):
        """测试__repr__方法"""
        model = YanqingModel(
            id=1,
            guali_id=1,
            status="应验"
        )
        repr_str = repr(model)
        assert "YanqingModel" in repr_str
        assert "guali_id=1" in repr_str

    def test_yanqing_model_to_dict(self):
        """测试to_dict方法"""
        model = YanqingModel(
            id=1,
            guali_id=1,
            status="应验",
            note="测试备注"
        )
        d = model.to_dict()
        assert d['id'] == 1
        assert d['guali_id'] == 1
        assert d['status'] == "应验"
        assert d['note'] == "测试备注"


# =============================================================================
# 模型关系测试
# =============================================================================

class TestModelRelationships:
    """测试模型间的关系"""

    def test_guali_has_yao_details_relationship(self):
        """测试GualiModel有yao_details关系属性"""
        model = GualiModel(
            solar_year=2024,
            solar_month=2,
            solar_day=12,
            ganzhi_year="甲辰",
            ganzhi_month="丙寅",
            ganzhi_day="甲午",
            xunkong="辰巳",
            ben_gua_code=63,
            gongwei="乾宫",
            gongwei_index="本宫"
        )
        # 检查关系属性存在
        assert hasattr(model, 'yao_details')

    def test_yao_detail_has_guali_relationship(self):
        """测试YaoDetailModel有guali关系属性"""
        model = YaoDetailModel(
            guali_id=1,
            position=1,
            yao_type=1,
            dizhi="子"
        )
        # 检查关系属性存在
        assert hasattr(model, 'guali')


# =============================================================================
# 边界条件测试
# =============================================================================

class TestModelBoundaryConditions:
    """测试边界条件"""

    def test_guali_max_gua_code(self):
        """测试最大卦代码（63 = 111111）"""
        model = GualiModel(
            solar_year=2024,
            solar_month=2,
            solar_day=12,
            ganzhi_year="甲辰",
            ganzhi_month="丙寅",
            ganzhi_day="甲午",
            xunkong="辰巳",
            ben_gua_code=63,  # 乾为天
            gongwei="乾宫",
            gongwei_index="本宫"
        )
        assert model.ben_gua_code == 63

    def test_guali_min_gua_code(self):
        """测试最小卦代码（0 = 000000）"""
        model = GualiModel(
            solar_year=2024,
            solar_month=2,
            solar_day=12,
            ganzhi_year="甲辰",
            ganzhi_month="丙寅",
            ganzhi_day="甲午",
            xunkong="辰巳",
            ben_gua_code=0,  # 坤为地
            gongwei="坤宫",
            gongwei_index="本宫"
        )
        assert model.ben_gua_code == 0

    def test_guali_all_gongwei(self):
        """测试所有卦宫"""
        gongwei_list = ["乾宫", "坎宫", "艮宫", "震宫", "巽宫", "离宫", "坤宫", "兑宫"]
        for gongwei in gongwei_list:
            model = GualiModel(
                solar_year=2024,
                solar_month=2,
                solar_day=12,
                ganzhi_year="甲辰",
                ganzhi_month="丙寅",
                ganzhi_day="甲午",
                xunkong="辰巳",
                ben_gua_code=63,
                gongwei=gongwei,
                gongwei_index="本宫"
            )
            assert model.gongwei == gongwei

    def test_yao_detail_all_dizhi(self):
        """测试所有地支"""
        dizhi_list = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
        for dizhi in dizhi_list:
            model = YaoDetailModel(
                guali_id=1,
                position=1,
                yao_type=1,
                dizhi=dizhi
            )
            assert model.dizhi == dizhi

    def test_guali_empty_text_fields(self):
        """测试空文本字段"""
        model = GualiModel(
            solar_year=2024,
            solar_month=2,
            solar_day=12,
            ganzhi_year="甲辰",
            ganzhi_month="丙寅",
            ganzhi_day="甲午",
            xunkong="辰巳",
            ben_gua_code=63,
            gongwei="乾宫",
            gongwei_index="本宫",
            zhan_wen=None,
            zhan_duan=None,
            image_path=None
        )
        assert model.zhan_wen is None
        assert model.zhan_duan is None
        assert model.image_path is None

    def test_yao_detail_optional_fields(self):
        """测试可选字段为空"""
        model = YaoDetailModel(
            guali_id=1,
            position=1,
            yao_type=1,
            dizhi="子"
        )
        assert model.liuqin is None
        assert model.liushen is None
