"""FastAPI 应用入口"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config import SERVER_HOST, SERVER_PORT
from backend.db.connection import engine, init_db
from backend.api.main import router as api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup: 确保数据库表存在
    init_db()
    yield
    # shutdown: 关闭连接池
    engine.dispose()


app = FastAPI(title="liuyaobase", lifespan=lifespan)

# CORS —— Vite 前端默认端口 5173
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")


@app.get("/")
def root():
    return {"message": "liuyaobase API"}
