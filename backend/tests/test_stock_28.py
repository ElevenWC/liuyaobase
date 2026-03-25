# -*- coding: utf-8 -*-
"""
六爻卦例分析系统 - 股票接口测试

测试股票数据获取和卦例关联功能
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime


class TestStockCache:
    """测试股票数据缓存"""

    def test_cache_set_and_get(self):
        """测试缓存设置和获取"""
        from backend.api.routers.stock import set_cache, get_cache, clear_cache

        clear_cache()

        # 设置缓存
        set_cache("test_key", {"data": "test_value"})

        # 获取缓存
        result = get_cache("test_key")
        assert result is not None
        assert result["data"] == "test_value"

        # 清除缓存
        clear_cache()
        result = get_cache("test_key")
        assert result is None

    def test_cache_expire(self):
        """测试缓存过期"""
        from backend.api.routers.stock import set_cache, get_cache, clear_cache

        clear_cache()

        # 设置立即过期的缓存
        set_cache("expire_key", {"data": "expire_value"}, expire_seconds=-1)

        # 获取应该返回None（已过期）
        result = get_cache("expire_key")
        assert result is None


class TestStockSearch:
    """测试股票搜索"""

    @patch('backend.api.routers.stock.check_akshare_available')
    def test_check_akshare_available_true(self, mock_check):
        """测试Akshare可用"""
        mock_check.return_value = True
        from backend.api.routers.stock import check_akshare_available

        result = check_akshare_available()
        assert result is True

    @patch('backend.api.routers.stock.check_akshare_available')
    def test_check_akshare_available_false(self, mock_check):
        """测试Akshare不可用"""
        mock_check.return_value = False
        from backend.api.routers.stock import check_akshare_available

        result = check_akshare_available()
        assert result is False

    @patch('backend.api.routers.stock.check_akshare_available')
    @patch('backend.api.routers.stock.clear_cache')
    def test_search_stock_akshare_not_available(self, mock_clear, mock_check):
        """测试Akshare不可用时的搜索"""
        mock_check.return_value = False

        from backend.api.routers.stock import search_stock_impl

        with pytest.raises(ImportError) as excinfo:
            search_stock_impl("贵州茅台")

        assert "Akshare" in str(excinfo.value)


class TestKlineData:
    """测试K线数据获取"""

    @patch('backend.api.routers.stock.check_akshare_available')
    def test_get_kline_data_akshare_not_available(self, mock_check):
        """测试Akshare不可用时的K线获取"""
        mock_check.return_value = False

        from backend.api.routers.stock import get_kline_data_impl

        with pytest.raises(ImportError) as excinfo:
            get_kline_data_impl("600519", "20240101", "20240131")

        assert "Akshare" in str(excinfo.value)


class TestIntradayData:
    """测试分时数据获取"""

    @patch('backend.api.routers.stock.check_akshare_available')
    def test_get_intraday_data_akshare_not_available(self, mock_check):
        """测试Akshare不可用时的分时获取"""
        mock_check.return_value = False

        from backend.api.routers.stock import get_intraday_data_impl

        with pytest.raises(ImportError) as excinfo:
            get_intraday_data_impl("600519")

        assert "Akshare" in str(excinfo.value)


class TestStockAPI:
    """测试股票API接口"""

    def test_search_stock_api_validation(self):
        """测试搜索接口参数验证"""
        from fastapi.testclient import TestClient
        from backend.api.main import app

        client = TestClient(app)

        # 测试缺少keyword参数
        response = client.get("/api/stock/search")
        assert response.status_code == 422  # 参数验证失败

    def test_kline_api_validation(self):
        """测试K线接口参数验证"""
        from fastapi.testclient import TestClient
        from backend.api.main import app

        client = TestClient(app)

        # 测试缺少必要参数
        response = client.get("/api/stock/kline")
        assert response.status_code == 422  # 参数验证失败

    def test_intraday_api_validation(self):
        """测试分时接口参数验证"""
        from fastapi.testclient import TestClient
        from backend.api.main import app

        client = TestClient(app)

        # 测试缺少code参数
        response = client.get("/api/stock/intraday")
        assert response.status_code == 422  # 参数验证失败

    def test_guali_mapping_api_validation(self):
        """测试卦例映射接口参数验证"""
        from fastapi.testclient import TestClient
        from backend.api.main import app

        client = TestClient(app)

        # 测试缺少name参数
        response = client.get("/api/stock/guali-mapping")
        assert response.status_code == 422  # 参数验证失败

    def test_status_api(self):
        """测试状态接口"""
        from fastapi.testclient import TestClient
        from backend.api.main import app

        client = TestClient(app)

        response = client.get("/api/stock/status")
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "akshare_available" in data
        assert "cache_size" in data

    def test_cache_clear_api(self):
        """测试缓存清除接口"""
        from fastapi.testclient import TestClient
        from backend.api.main import app

        client = TestClient(app)

        response = client.get("/api/stock/cache/clear")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "缓存已清除" in data["message"]


class TestGualiMappingWithRepo:
    """测试卦例映射（需要数据库）"""

    @pytest.mark.skip(reason="需要数据库连接")
    def test_guali_mapping_with_real_data(self):
        """测试真实的卦例映射查询"""
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
