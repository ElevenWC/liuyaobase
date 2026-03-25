"""
六爻卦例分析系统 - FastAPI应用入口
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from backend.config import settings
from backend.api.routers import guali_router, images_router
from backend.api.routers.search import router as search_router
from backend.api.routers.yanqing import router as yanqing_router
from backend.api.routers.stock import router as stock_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # Startup
    print(f"🚀 {settings.app_name} v{settings.app_version} 启动中...")
    print(f"📁 图片存储路径: {settings.image_storage_path}")
    yield
    # Shutdown
    print(f"👋 {settings.app_name} 已关闭")


# 创建FastAPI应用实例
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="六爻卦例的录入、存储、查看和复杂检索系统",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应配置具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(guali_router)
app.include_router(images_router)
app.include_router(search_router)
app.include_router(yanqing_router)
app.include_router(stock_router)

# 挂载静态文件目录（可选，用于直接访问图片）
# 确保图片目录存在
settings.ensure_image_directory()


@app.get("/", tags=["Root"])
async def root():
    """根路由 - 欢迎信息"""
    return {
        "message": f"欢迎使用{settings.app_name}",
        "version": settings.app_version,
        "docs": "/docs"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """健康检查接口"""
    from backend.db.connection import test_connection

    db_status = "connected" if test_connection() else "disconnected"

    return {
        "status": "ok",
        "database": db_status,
        "app_name": settings.app_name,
        "version": settings.app_version
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.api.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
