from fastapi import APIRouter

from app.api.routes import auth, dashboard, projects, quality, system, tasks

api_router = APIRouter()
api_router.include_router(system.router, tags=["system"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(quality.router, prefix="/quality", tags=["quality"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
