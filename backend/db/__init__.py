# -*- coding: utf-8 -*-
"""
六爻卦例分析系统 - 数据访问层

本模块提供数据库连接、ORM模型和数据仓库功能。
"""

from backend.db.connection import (
    get_session,
    get_async_session,
    init_db,
    async_init_db,
    test_connection,
    async_test_connection,
    Base,
    sync_engine,
    async_engine,
)

from backend.db.models import (
    GualiModel,
    YaoDetailModel,
    YanqingModel,
)

from backend.db.repositories import (
    GualiRepository,
    YaoDetailRepository,
    YanqingRepository,
    guali_repository,
    yao_detail_repository,
    yanqing_repository,
)

__all__ = [
    # 连接
    'get_session',
    'get_async_session',
    'init_db',
    'async_init_db',
    'test_connection',
    'async_test_connection',
    'Base',
    'sync_engine',
    'async_engine',
    # 模型
    'GualiModel',
    'YaoDetailModel',
    'YanqingModel',
    # 仓库
    'GualiRepository',
    'YaoDetailRepository',
    'YanqingRepository',
    'guali_repository',
    'yao_detail_repository',
    'yanqing_repository',
]
