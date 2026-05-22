"""数据库连接管理"""
import os
from sqlalchemy import create_engine as sa_create_engine, text
from sqlmodel import create_engine, Session, SQLModel
from backend.config import (
    DATABASE_URL,
    DATABASE_HOST,
    DATABASE_PORT,
    DATABASE_USER,
    DATABASE_PASSWORD,
    DATABASE_NAME,
)

DB_ECHO = os.environ.get("LIUYAO_DB_ECHO", "false").lower() == "true"

# 确保数据库存在（首次部署时自动创建）
_init_url = f"mysql+pymysql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}"
_init_engine = sa_create_engine(_init_url)
with _init_engine.connect() as conn:
    conn = conn.execution_options(isolation_level="AUTOCOMMIT")
    conn.execute(text(
        f"CREATE DATABASE IF NOT EXISTS `{DATABASE_NAME}` "
        "DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
    ))
_init_engine.dispose()

engine = create_engine(DATABASE_URL, echo=DB_ECHO)


def get_session():
    """每次请求创建新 session，请求结束自动关闭（FastAPI Depends 注入用）"""
    with Session(engine) as session:
        yield session


def init_db():
    """创建所有表（由 main.py startup 事件调用）"""
    SQLModel.metadata.create_all(engine)
