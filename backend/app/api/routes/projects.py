from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_interface, get_pg_session
from app.schemas.domain import ImportTaskContentsRequest, ProjectCreate, ProjectRead, TaskRead
from backend_db.db_interface import DBInterface
from backend_db.db_models import Project

router = APIRouter()


@router.post("", response_model=ProjectRead)
async def create_project(payload: ProjectCreate, dbi: DBInterface = Depends(get_db_interface)) -> Project:
    return await dbi.create_project(
        name=payload.name,
        client_name=payload.client_name,
        created_by=payload.created_by,
    )


@router.get("", response_model=list[ProjectRead])
async def list_projects(pg: AsyncSession = Depends(get_pg_session)) -> list[Project]:
    rows = await pg.execute(select(Project).order_by(Project.id.desc()))
    return list(rows.scalars().all())


@router.post("/{project_id}/import-data", response_model=list[TaskRead])
async def import_project_data(
    project_id: int,
    payload: ImportTaskContentsRequest,
    dbi: DBInterface = Depends(get_db_interface),
) -> list:
    if not payload.task_contents:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="task_contents is empty")

    tasks = await dbi.import_task_contents(
        project_id=project_id,
        modality=payload.modality,
        task_contents=payload.task_contents,
    )
    return tasks
