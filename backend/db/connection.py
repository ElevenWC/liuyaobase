"""
六爻卦例分析系统 - 数据库连接模块
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.ext.asyncio import async_sessionmaker
from contextlib import contextmanager, asynccontextmanager
from backend.config import settings


# 同步引擎
sync_engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=settings.debug
)

# 异步引擎
async_engine = create_async_engine(
    settings.async_database_url,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=settings.debug
)

# 同步会话工厂
SyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=sync_engine
)

# 异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

# 声明基类
Base = declarative_base()


@contextmanager
def get_session():
    """
    同步数据库会话上下文管理器

    使用示例:
        with get_session() as session:
            result = session.execute(text("SELECT 1"))
            print(result.scalar())
    """
    session = SyncSessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


@asynccontextmanager
async def get_async_session():
    """
    异步数据库会话上下文管理器

    使用示例:
        async with get_async_session() as session:
            result = await session.execute(text("SELECT 1"))
            print(result.scalar())
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def init_db():
    """
    初始化数据库表

    创建所有定义的表结构
    """
    Base.metadata.create_all(bind=sync_engine)


async def async_init_db():
    """
    异步初始化数据库表
    """
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


def test_connection() -> bool:
    """
    测试数据库连接

    Returns:
        bool: 连接成功返回True，否则返回False
    """
    try:
        with get_session() as session:
            from sqlalchemy import text
            result = session.execute(text("SELECT 1"))
            return result.scalar() == 1
    except Exception as e:
        print(f"数据库连接失败: {e}")
        return False


async def async_test_connection() -> bool:
    """
    异步测试数据库连接

    Returns:
        bool: 连接成功返回True，否则返回False
    """
    try:
        async with get_async_session() as session:
            from sqlalchemy import text
            result = await session.execute(text("SELECT 1"))
            return result.scalar() == 1
    except Exception as e:
        print(f"数据库连接失败: {e}")
        return False
