from collections.abc import AsyncGenerator

from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from backend_db.db import get_db_session
from backend_db.db_interface import DBInterface
from backend_db.mongo import get_mongo_database


async def get_pg_session() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_db_session():
        yield session


async def get_mongo() -> AsyncGenerator[AsyncIOMotorDatabase, None]:
    async for mongo_db in get_mongo_database():
        yield mongo_db


async def get_db_interface(
    pg: AsyncSession = Depends(get_pg_session),
    mongo: AsyncIOMotorDatabase = Depends(get_mongo),
) -> DBInterface:
    return DBInterface(pg=pg, mongo=mongo)
