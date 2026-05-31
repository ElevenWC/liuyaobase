"""FastAPI 应用入口"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config import SERVER_HOST, SERVER_PORT
from backend.db.connection import engine, init_db
from backend.api.main import router as api_router
from backend.services.sync_watcher import start_watcher, stop_watcher


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    init_db()
    start_watcher()
    yield
    # shutdown
    stop_watcher()
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
