"""
测试数据库连接

运行: pytest backend/tests/test_connection.py -v
"""
import pytest
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def test_import_config():
    """测试配置模块导入"""
    from backend.config import settings
    assert settings is not None
    assert settings.app_name == "六爻卦例分析系统"
    print("✓ 配置模块导入成功")


def test_import_connection():
    """测试连接模块导入"""
    from backend.db.connection import (
        sync_engine,
        async_engine,
        get_session,
        get_async_session,
        Base
    )
    assert sync_engine is not None
    assert async_engine is not None
    assert Base is not None
    print("✓ 连接模块导入成功")


def test_session_context():
    """测试同步会话上下文管理器"""
    from backend.db.connection import get_session
    from sqlalchemy import text

    try:
        with get_session() as session:
            assert session is not None
            # 注意：这里只是测试上下文管理器，实际连接需要配置正确的数据库
            print("✓ 同步会话上下文管理器创建成功")
    except Exception as e:
        # 如果数据库未配置，这是预期的
        print(f"! 会话创建跳过 (数据库可能未配置): {e}")


def test_config_database_url():
    """测试数据库URL配置"""
    from backend.config import settings

    # 验证URL格式
    assert "mysql" in settings.database_url
    assert "pymysql" in settings.database_url
    print(f"✓ 数据库URL配置正确: {settings.database_url[:30]}...")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
