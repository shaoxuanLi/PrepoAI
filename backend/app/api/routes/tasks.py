from datetime import datetime

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_interface, get_mongo, get_pg_session
from app.schemas.domain import TaskClaimRequest, TaskRead, TaskSubmitRequest
from backend_db.db_interface import DBInterface
from backend_db.db_models import TaskAssignment

router = APIRouter()


@router.get("/square", response_model=list[TaskRead])
async def task_square(
    limit: int = 50,
    dbi: DBInterface = Depends(get_db_interface),
) -> list[TaskAssignment]:
    return await dbi.list_task_square(limit=limit)


@router.get("/{task_id}/content")
async def get_task_content(task_id: int, pg: AsyncSession = Depends(get_pg_session), mongo: AsyncIOMotorDatabase = Depends(get_mongo)) -> dict:
    task = await pg.get(TaskAssignment, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    doc = await mongo["task_content"].find_one({"_id": ObjectId(task.task_content_doc_id)})
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task content not found")

    doc["_id"] = str(doc["_id"])
    return doc


@router.post("/{task_id}/claim", response_model=TaskRead)
async def claim_task(task_id: int, payload: TaskClaimRequest, dbi: DBInterface = Depends(get_db_interface)) -> TaskAssignment:
    try:
        return await dbi.claim_task(task_id=task_id, user_id=payload.user_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/{task_id}/submit", response_model=TaskRead)
async def submit_task(task_id: int, payload: TaskSubmitRequest, dbi: DBInterface = Depends(get_db_interface)) -> TaskAssignment:
    try:
        data = dict(payload.annotation_payload)
        data["client_submitted_at"] = datetime.utcnow().isoformat()
        return await dbi.submit_annotation(task_id=task_id, user_id=payload.user_id, annotation_payload=data)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/{task_id}/under-review", response_model=TaskRead)
async def mark_under_review(task_id: int, dbi: DBInterface = Depends(get_db_interface)) -> TaskAssignment:
    try:
        return await dbi.mark_under_review(task_id=task_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/{task_id}/finalize", response_model=TaskRead)
async def finalize_task(task_id: int, dbi: DBInterface = Depends(get_db_interface)) -> TaskAssignment:
    try:
        return await dbi.finalize_task(task_id=task_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
