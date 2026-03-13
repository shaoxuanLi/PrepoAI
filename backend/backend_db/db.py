import os
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase


POSTGRES_DSN = os.getenv(
    "POSTGRES_DSN",
    "postgresql+asyncpg://propoai:propoai@postgres:5432/propoai",
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
