import os
from collections.abc import AsyncGenerator

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase


MONGO_DSN = os.getenv("MONGO_DSN", "mongodb://mongodb:27017")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "prepoai")

_mongo_client: AsyncIOMotorClient | None = None


def get_mongo_client() -> AsyncIOMotorClient:
    global _mongo_client
    if _mongo_client is None:
        _mongo_client = AsyncIOMotorClient(MONGO_DSN)
    return _mongo_client


def get_mongo_db() -> AsyncIOMotorDatabase:
    return get_mongo_client()[MONGO_DB_NAME]


async def get_mongo_database() -> AsyncGenerator[AsyncIOMotorDatabase, None]:
    """FastAPI dependency wrapper for MongoDB database object."""
    yield get_mongo_db()
