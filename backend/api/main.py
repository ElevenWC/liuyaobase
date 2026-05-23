"""路由聚合——后续里程碑逐步添加各模块 router"""
from fastapi import APIRouter
from backend.api.routers.import_data import router as import_router
from backend.api.routers.guaci import router as guaci_router

router = APIRouter()
router.include_router(import_router)
router.include_router(guaci_router)
