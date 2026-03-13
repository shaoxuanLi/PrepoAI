from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_mongo, get_pg_session
from backend_db.db_models import Project, TaskAssignment, TaskStatus, User

router = APIRouter()


@router.get("/admin")
async def admin_dashboard(pg: AsyncSession = Depends(get_pg_session)) -> dict:
    project_total = (await pg.execute(select(func.count(Project.id)))).scalar() or 0
    user_total = (await pg.execute(select(func.count(User.id)))).scalar() or 0
    task_total = (await pg.execute(select(func.count(TaskAssignment.id)))).scalar() or 0

    status_stmt = (
        select(TaskAssignment.status, func.count(TaskAssignment.id))
        .group_by(TaskAssignment.status)
        .order_by(TaskAssignment.status)
    )
    status_rows = (await pg.execute(status_stmt)).all()

    return {
        "project_total": int(project_total),
        "user_total": int(user_total),
        "task_total": int(task_total),
        "task_status_distribution": {row[0].value: int(row[1]) for row in status_rows},
    }


@router.get("/annotator/{annotator_id}")
async def annotator_dashboard(
    annotator_id: int,
    pg: AsyncSession = Depends(get_pg_session),
) -> dict:
    completed_stmt = select(func.count(TaskAssignment.id)).where(
        TaskAssignment.assignee_id == annotator_id,
        TaskAssignment.status.in_([TaskStatus.COMPLETED, TaskStatus.FINALIZED]),
    )
    in_progress_stmt = select(func.count(TaskAssignment.id)).where(
        TaskAssignment.assignee_id == annotator_id,
        TaskAssignment.status == TaskStatus.IN_PROGRESS,
    )

    completed = (await pg.execute(completed_stmt)).scalar() or 0
    in_progress = (await pg.execute(in_progress_stmt)).scalar() or 0

    return {
        "annotator_id": annotator_id,
        "completed_tasks": int(completed),
        "in_progress_tasks": int(in_progress),
        "today_points_estimate": int(completed) * 5,
    }


@router.get("/data-distribution")
async def data_distribution(mongo=Depends(get_mongo)) -> dict:
    task_content_count = await mongo["task_content"].count_documents({})
    annotation_count = await mongo["annotation_result"].count_documents({})
    text_count = await mongo["task_content"].count_documents({"modality": "text"})
    image_count = await mongo["task_content"].count_documents({"modality": "image"})

    return {
        "task_content_total": task_content_count,
        "annotation_result_total": annotation_count,
        "by_modality": {
            "text": text_count,
            "image": image_count,
        },
    }
