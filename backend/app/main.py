import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.config import settings
from app.database import AsyncSessionLocal, engine
from app.models import User  # noqa: F401  – triggers model registration
from app.database import Base

logger = logging.getLogger(__name__)


# ─────────────────────── lifespan ────────────────────────────

async def lifespan(app: FastAPI):
    """Startup / shutdown tasks."""
    # 1. Create tables (dev convenience; use Alembic in production)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 2. Seed initial super-admin
    from app.services.user_service import UserService

    async with AsyncSessionLocal() as db:
        try:
            admin = await UserService.ensure_superadmin(
                db,
                email=settings.FIRST_SUPERUSER_EMAIL,
                username="admin",
                full_name=settings.FIRST_SUPERUSER_NAME,
                password=settings.FIRST_SUPERUSER_PASSWORD,
            )
            await db.commit()
            logger.info("Super-admin ready: %s", admin.email)
        except Exception as exc:  # pragma: no cover
            await db.rollback()
            logger.error("Failed to seed super-admin: %s", exc)

    yield  # app is running

    await engine.dispose()


# ─────────────────────── app factory ─────────────────────────

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="PropoAI — LLM 数据标注平台 API",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router, prefix=settings.API_V1_PREFIX)

    @app.get("/health", tags=["health"])
    async def health_check():
        return {"status": "ok", "version": settings.APP_VERSION}

    return app


app = create_app()
