import os
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

# 初始化 SQLAlchemy 异步引擎（POSTGRES_DSN）。
# 提供 FastAPI 依赖 get_db_session()。


#初始化连接
POSTGRES_DSN = os.getenv(
    "POSTGRES_DSN", 
    #preproai:preproai - username:password
    #postgres:5432 - host:port
    #preproai - database name
    "postgresql+asyncpg://preproai:preproai@postgres:5432/preproai", #default if above doesn't exist
)


class Base(DeclarativeBase):
    """SQLAlchemy declarative base for PostgreSQL models."""


engine = create_async_engine(POSTGRES_DSN, echo=False, pool_pre_ping=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for async DB sessions."""
    async with SessionLocal() as session:
        yield session


async def init_postgres_models() -> None:
    """Create PostgreSQL tables for first-time bootstrap."""
    async with engine.begin() as conn:
        from backend_db import db_models  # noqa: F401

        await conn.run_sync(Base.metadata.create_all)
