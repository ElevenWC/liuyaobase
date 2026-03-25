# -*- coding: utf-8 -*-
"""
六爻卦例分析系统 - API路由模块
"""
from backend.api.routers.guali import router as guali_router
from backend.api.routers.images import router as images_router

__all__ = ["guali_router", "images_router"]
