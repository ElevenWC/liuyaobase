# -*- coding: utf-8 -*-
"""
六爻卦例分析系统 - 卦例API测试

测试阶段十七和十八的API接口
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from backend.api.main import app
from backend.core.enums import ZhongGua, Dizhi, LiuQin, LiuShen
from backend.core.models import Guali, Yao


client = TestClient(app)


class TestGualiAPI:
    """测试卦例API接口"""

    def test_root_endpoint(self):
        """测试根路由"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data

    def test_health_endpoint(self):
        """测试健康检查接口"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "database" in data

    def test_list_gualis_empty(self):
        """测试获取空卦例列表"""
        with patch('backend.api.routers.guali.guali_repository') as mock_repo:
            mock_repo.get_all_gualis.return_value = ([], 0)

            response = client.get("/api/guali")
            assert response.status_code == 200
            data = response.json()
            assert data["total"] == 0
            assert data["items"] == []
            assert data["page"] == 1

    def test_list_gualis_with_data(self):
        """测试获取卦例列表（有数据）"""
        from backend.db.models import GualiModel

        mock_model = GualiModel(
            id=1,
            solar_year=2024,
            solar_month=2,
            solar_day=12,
            ganzhi_year="甲辰",
            ganzhi_month="丙寅",
            ganzhi_day="甲午",
            xunkong="辰巳",
            ben_gua_code=63,  # 乾为天
            zhi_gua_code=None,
            yao_bian_code=0,
            gongwei="乾宫",
            gongwei_index="本宫",
            zhan_wen="测试占问",
            zhan_duan=None
        )

        with patch('backend.api.routers.guali.guali_repository') as mock_repo:
            mock_repo.get_all_gualis.return_value = ([mock_model], 1)

            response = client.get("/api/guali")
            assert response.status_code == 200
            data = response.json()
            assert data["total"] == 1
            assert len(data["items"]) == 1
            assert data["items"][0]["id"] == 1

    def test_list_gualis_pagination(self):
        """测试卦例列表分页"""
        with patch('backend.api.routers.guali.guali_repository') as mock_repo:
            mock_repo.get_all_gualis.return_value = ([], 100)

            response = client.get("/api/guali?page=2&page_size=10")
            assert response.status_code == 200

            # 验证分页参数传递正确
            call_args = mock_repo.get_all_gualis.call_args
            assert call_args.kwargs["page"] == 2
            assert call_args.kwargs["page_size"] == 10

    def test_list_gualis_filter_by_year(self):
        """测试按年份筛选卦例"""
        with patch('backend.api.routers.guali.guali_repository') as mock_repo:
            mock_repo.get_gualis_by_year.return_value = ([], 0)

            response = client.get("/api/guali?year=2024")
            assert response.status_code == 200

            # 验证调用了年份筛选方法
            mock_repo.get_gualis_by_year.assert_called_once()
            call_args = mock_repo.get_gualis_by_year.call_args
            assert call_args.kwargs["year"] == 2024

    def test_get_guali_not_found(self):
        """测试获取不存在的卦例"""
        with patch('backend.api.routers.guali.guali_repository') as mock_repo:
            mock_repo.get_guali_by_id.return_value = None

            response = client.get("/api/guali/999")
            assert response.status_code == 404

    def test_get_guali_success(self):
        """测试获取卦例成功"""
        from backend.db.models import GualiModel

        mock_model = GualiModel(
            id=1,
            solar_year=2024,
            solar_month=2,
            solar_day=12,
            ganzhi_year="甲辰",
            ganzhi_month="丙寅",
            ganzhi_day="甲午",
            xunkong="辰巳",
            ben_gua_code=63,
            zhi_gua_code=None,
            yao_bian_code=0,
            gongwei="乾宫",
            gongwei_index="本宫"
        )

        with patch('backend.api.routers.guali.guali_repository') as mock_repo:
            mock_repo.get_guali_by_id.return_value = mock_model

            response = client.get("/api/guali/1")
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == 1
            assert data["solar_year"] == 2024

    def test_create_guali_success(self):
        """测试创建卦例成功"""
        from backend.db.models import GualiModel

        mock_model = GualiModel(
            id=1,
            solar_year=2024,
            solar_month=2,
            solar_day=12,
            ganzhi_year="甲辰",
            ganzhi_month="丙寅",
            ganzhi_day="甲午",
            xunkong="辰巳",
            ben_gua_code=63,
            zhi_gua_code=None,
            yao_bian_code=0,
            gongwei="乾宫",
            gongwei_index="本宫"
        )

        with patch('backend.api.routers.guali.guali_repository') as mock_repo, \
             patch('backend.api.routers.guali.yao_detail_repository') as mock_yao_repo:

            mock_repo.create_from_guali.return_value = mock_model
            mock_yao_repo.save_yao_details.return_value = []

            response = client.post(
                "/api/guali",
                json={
                    "solar_year": 2024,
                    "solar_month": 2,
                    "solar_day": 12,
                    "ben_gua_name": "乾为天",
                    "zhi_gua_name": None,
                    "zhan_wen": "测试占问"
                }
            )
            assert response.status_code == 201
            data = response.json()
            assert data["solar_year"] == 2024

    def test_create_guali_invalid_gua_name(self):
        """测试创建卦例时使用无效卦名"""
        response = client.post(
            "/api/guali",
            json={
                "solar_year": 2024,
                "solar_month": 2,
                "solar_day": 12,
                "ben_gua_name": "不存在的卦",
                "zhi_gua_name": None
            }
        )
        assert response.status_code == 400

    def test_update_guali_success(self):
        """测试更新卦例成功"""
        from backend.db.models import GualiModel

        mock_model = GualiModel(
            id=1,
            solar_year=2024,
            solar_month=2,
            solar_day=12,
            ganzhi_year="甲辰",
            ganzhi_month="丙寅",
            ganzhi_day="甲午",
            xunkong="辰巳",
            ben_gua_code=63,
            zhi_gua_code=None,
            yao_bian_code=0,
            gongwei="乾宫",
            gongwei_index="本宫",
            zhan_wen="更新后的占问"
        )

        with patch('backend.api.routers.guali.guali_repository') as mock_repo:
            mock_repo.update_guali.return_value = mock_model

            response = client.put(
                "/api/guali/1",
                json={"zhan_wen": "更新后的占问"}
            )
            assert response.status_code == 200
            data = response.json()
            assert data["zhan_wen"] == "更新后的占问"

    def test_update_guali_no_data(self):
        """测试更新卦例时没有提供数据"""
        response = client.put("/api/guali/1", json={})
        assert response.status_code == 400

    def test_update_guali_not_found(self):
        """测试更新不存在的卦例"""
        with patch('backend.api.routers.guali.guali_repository') as mock_repo:
            mock_repo.update_guali.return_value = None

            response = client.put(
                "/api/guali/999",
                json={"zhan_wen": "测试"}
            )
            assert response.status_code == 404

    def test_delete_guali_success(self):
        """测试删除卦例成功"""
        with patch('backend.api.routers.guali.guali_repository') as mock_repo:
            mock_repo.delete_guali.return_value = True

            response = client.delete("/api/guali/1")
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True

    def test_delete_guali_not_found(self):
        """测试删除不存在的卦例"""
        with patch('backend.api.routers.guali.guali_repository') as mock_repo:
            mock_repo.delete_guali.return_value = False

            response = client.delete("/api/guali/999")
            assert response.status_code == 404

    def test_get_guali_detail_success(self):
        """测试获取卦例详情成功"""
        from backend.db.models import GualiModel

        mock_model = GualiModel(
            id=1,
            solar_year=2024,
            solar_month=2,
            solar_day=12,
            ganzhi_year="甲辰",
            ganzhi_month="丙寅",
            ganzhi_day="甲午",
            xunkong="辰巳",
            ben_gua_code=63,
            zhi_gua_code=None,
            yao_bian_code=0,
            gongwei="乾宫",
            gongwei_index="本宫"
        )
        mock_model.yao_details = []

        # 创建业务对象用于model_to_guali
        guali = Guali(
            id=1,
            solar_year=2024,
            solar_month=2,
            solar_day=12,
            ganzhi_year="甲辰",
            ganzhi_month="丙寅",
            ganzhi_day="甲午",
            xunkong="辰巳",
            ben_gua=ZhongGua.QIAN_WEI_TIAN,
            zhi_gua=None,
            yao_bian_code=0
        )
        guali.calculate_all()

        with patch('backend.api.routers.guali.guali_repository') as mock_repo:
            mock_repo.get_guali_by_id.return_value = mock_model
            mock_repo.model_to_guali.return_value = guali

            response = client.get("/api/guali/1/detail")
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == 1
            assert "yaos" in data
            assert len(data["yaos"]) == 6

    def test_get_guali_detail_not_found(self):
        """测试获取不存在的卦例详情"""
        with patch('backend.api.routers.guali.guali_repository') as mock_repo:
            mock_repo.get_guali_by_id.return_value = None

            response = client.get("/api/guali/999/detail")
            assert response.status_code == 404


class TestModelToResponse:
    """测试模型转换函数"""

    def test_model_to_response(self):
        """测试数据库模型转换为响应模型"""
        from backend.api.routers.guali import model_to_response
        from backend.db.models import GualiModel

        mock_model = GualiModel(
            id=1,
            solar_year=2024,
            solar_month=2,
            solar_day=12,
            ganzhi_year="甲辰",
            ganzhi_month="丙寅",
            ganzhi_day="甲午",
            xunkong="辰巳",
            ben_gua_code=63,  # 乾为天
            zhi_gua_code=None,
            yao_bian_code=0,
            gongwei="乾宫",
            gongwei_index="本宫",
            zhan_wen="测试占问",
            zhan_duan="测试占断"
        )

        response = model_to_response(mock_model)

        assert response.id == 1
        assert response.solar_year == 2024
        assert response.ben_gua_name == "乾为天"
        assert response.zhi_gua_name is None
        assert response.gongwei == "乾宫"
        assert response.zhan_wen == "测试占问"

    def test_model_to_response_with_zhi_gua(self):
        """测试带之卦的模型转换"""
        from backend.api.routers.guali import model_to_response
        from backend.db.models import GualiModel

        mock_model = GualiModel(
            id=1,
            solar_year=2024,
            solar_month=2,
            solar_day=12,
            ganzhi_year="甲辰",
            ganzhi_month="丙寅",
            ganzhi_day="甲午",
            xunkong="辰巳",
            ben_gua_code=25,  # 山风蛊
            zhi_gua_code=5,   # 火地晋
            yao_bian_code=28,  # 25 XOR 5 = 28
            gongwei="巽宫",
            gongwei_index="归魂"
        )

        response = model_to_response(mock_model)

        assert response.ben_gua_name == "山风蛊"
        assert response.zhi_gua_name == "火地晋"
        assert response.yao_bian_code == 28


class TestGualiToDetailResponse:
    """测试业务对象转换详情响应"""

    def test_guali_to_detail_response(self):
        """测试业务对象转换为详情响应"""
        from backend.api.routers.guali import guali_to_detail_response

        guali = Guali(
            id=1,
            solar_year=2024,
            solar_month=2,
            solar_day=12,
            ganzhi_year="甲辰",
            ganzhi_month="丙寅",
            ganzhi_day="甲午",
            xunkong="辰巳",
            ben_gua=ZhongGua.QIAN_WEI_TIAN,
            zhi_gua=None,
            yao_bian_code=0,
            zhan_wen="测试占问"
        )
        guali.calculate_all()

        response = guali_to_detail_response(guali)

        assert response.id == 1
        assert response.solar_year == 2024
        assert response.ben_gua_name == "乾为天"
        assert len(response.yaos) == 6

        # 检查第一爻
        first_yao = response.yaos[0]
        assert first_yao.position == 1
        assert first_yao.dizhi == "子"  # 乾卦初爻地支为子
