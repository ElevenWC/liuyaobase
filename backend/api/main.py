"""路由聚合——后续里程碑逐步添加各模块 router"""
from fastapi import APIRouter
from backend.api.routers.import_data import router as import_router

router = APIRouter()
router.include_router(import_router)
