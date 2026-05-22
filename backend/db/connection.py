"""数据库连接管理"""
import os
from sqlmodel import create_engine, Session, SQLModel
from backend.config import DATABASE_URL

DB_ECHO = os.environ.get("LIUYAO_DB_ECHO", "false").lower() == "true"

engine = create_engine(DATABASE_URL, echo=DB_ECHO)


def get_session():
    """每次请求创建新 session，请求结束自动关闭（FastAPI Depends 注入用）"""
    with Session(engine) as session:
        yield session


def init_db():
    """创建所有表（由 main.py startup 事件调用）"""
    SQLModel.metadata.create_all(engine)
