from datetime import datetime, timezone
from typing import Any

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend_db.db_models import (
    Project,
    ProjectStatus,
    QualityMetric,
    QualityMetricType,
    TaskAssignment,
    TaskStatus,
    User,
    UserRole,
)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class DBInterface:
    """Hybrid DB interface: relational metadata in PostgreSQL, flexible content in MongoDB."""

    def __init__(self, pg: AsyncSession, mongo: AsyncIOMotorDatabase):
        self.pg = pg
        self.mongo = mongo

    # -------------------------------------------------------------------------
    # Auth
    # -------------------------------------------------------------------------

    async def create_user(
        self,
        *,
        username: str,
        email: str,
        password_hash: str,
        role: UserRole,
    ) -> User:
        # called at POST /auth/register
        user = User(username=username, email=email, password_hash=password_hash, role=role)
        self.pg.add(user)
        await self.pg.commit()
        await self.pg.refresh(user)
        return user

    async def get_user(self, *, user_id: int | None = None, username: str | None = None) -> User | None:
        # called at POST /auth/login and on every protected request to verify token
        if user_id is not None:
            return await self.pg.get(User, user_id)
        if username is not None:
            stmt = select(User).where(User.username == username)
            row = await self.pg.execute(stmt)
            return row.scalars().first()
        raise ValueError("Provide either user_id or username")

    # -------------------------------------------------------------------------
    # Projects
    # -------------------------------------------------------------------------

    async def create_project(self, *, name: str, client_name: str, created_by: int) -> Project:
        project = Project(name=name, client_name=client_name, created_by=created_by)
        self.pg.add(project)
        await self.pg.commit()
        await self.pg.refresh(project)
        return project

    async def get_project(self, *, project_id: int) -> Project | None:
        # called at GET /projects/{id}
        return await self.pg.get(Project, project_id)

    async def list_projects(self, *, created_by: int | None = None) -> list[Project]:
        # called at GET /projects — optionally filtered by employer
        stmt: Select[tuple[Project]] = select(Project).order_by(Project.created_at.desc())
        if created_by is not None:
            stmt = stmt.where(Project.created_by == created_by)
        rows = await self.pg.execute(stmt)
        return list(rows.scalars().all())

    async def update_project_progress(self, *, project_id: int) -> None:
        # called internally after finalize_task() to keep progress % in sync
        total_stmt = select(func.count()).where(TaskAssignment.project_id == project_id)
        finalized_stmt = select(func.count()).where(
            TaskAssignment.project_id == project_id,
            TaskAssignment.status == TaskStatus.FINALIZED,
        )
        total = (await self.pg.execute(total_stmt)).scalar() or 0
        finalized = (await self.pg.execute(finalized_stmt)).scalar() or 0

        project = await self.pg.get(Project, project_id)
        if project and total > 0:
            project.progress = round(finalized / total * 100, 2)
            if finalized == total:
                project.status = ProjectStatus.COMPLETED
            await self.pg.commit()

    # -------------------------------------------------------------------------
    # Task content & import
    # -------------------------------------------------------------------------

    async def import_task_contents(
        self,
        *,
        project_id: int,
        modality: str, #type of data being annotated
        task_contents: list[dict[str, Any]], #the data to be annotated
    ) -> list[TaskAssignment]:
        #directly store the data to be annotated into mongo
        inserted = await self.mongo["task_content"].insert_many(
            [
                {
                    **item, # unpacking the original content fields
                    "project_id": project_id,
                    "modality": modality,
                    "created_at": _now(),
                }
                for item in task_contents
            ]
        )
        tasks = [
            TaskAssignment(
                project_id=project_id,
                modality=modality,
                task_content_doc_id=str(doc_id),
                status=TaskStatus.PENDING,
            )
            for doc_id in inserted.inserted_ids # for each id from the mongo db
        ]
        self.pg.add_all(tasks)

        project = await self.pg.get(Project, project_id)
        if project:
            project.status = ProjectStatus.IN_PROGRESS

        await self.pg.commit()
        return tasks

    async def get_task_with_content(self, *, task_id: int) -> dict[str, Any] | None:
        # called at GET /tasks/{id} — combines postgres metadata + mongo content
        # so the annotator sees everything needed to annotate in one response
        task = await self.pg.get(TaskAssignment, task_id)
        if not task:
            return None
        content = await self.mongo["task_content"].find_one(
            {"_id": ObjectId(task.task_content_doc_id)}
        )
        if content:
            content["_id"] = str(content["_id"])
        return {"task": task, "content": content}

    # -------------------------------------------------------------------------
    # Annotator actions
    # -------------------------------------------------------------------------

    async def list_task_square(self, *, limit: int = 50) -> list[TaskAssignment]:
        stmt: Select[tuple[TaskAssignment]] = (
            select(TaskAssignment)
            .where(TaskAssignment.status == TaskStatus.PENDING)
            .order_by(TaskAssignment.id.asc())
            .limit(limit)
        )
        rows = await self.pg.execute(stmt)
        return list(rows.scalars().all())

    async def claim_task(self, *, task_id: int, user_id: int) -> TaskAssignment:
        task = await self.pg.get(TaskAssignment, task_id)
        if not task:
            raise ValueError("Task not found")
        if task.status != TaskStatus.PENDING:
            raise ValueError("Task is not claimable")

        task.assignee_id = user_id
        task.locked_by_id = user_id
        task.locked_at = _now()
        task.started_at = _now()
        task.status = TaskStatus.IN_PROGRESS
        await self.pg.commit()
        await self.pg.refresh(task)
        return task

    async def submit_annotation(
        self,
        *,
        task_id: int,
        user_id: int,
        annotation_payload: dict[str, Any],
    ) -> TaskAssignment:
        task = await self.pg.get(TaskAssignment, task_id)
        if not task:
            raise ValueError("Task not found")
        if task.assignee_id != user_id:
            raise ValueError("Task not assigned to this annotator")
        if task.status != TaskStatus.IN_PROGRESS:
            raise ValueError("Task is not in progress")

        result = await self.mongo["annotation_result"].insert_one(
            {
                "task_id": task_id,
                "project_id": task.project_id,
                "annotator_id": user_id,
                "payload": annotation_payload,
                "submitted_at": _now(),
            }
        )

        task.result_doc_id = str(result.inserted_id)
        task.status = TaskStatus.COMPLETED
        task.completed_at = _now()
        await self.pg.commit()
        await self.pg.refresh(task)
        return task

    # -------------------------------------------------------------------------
    # Auditor / review actions
    # -------------------------------------------------------------------------

    async def mark_under_review(self, *, task_id: int) -> TaskAssignment:
        task = await self.pg.get(TaskAssignment, task_id)
        if not task:
            raise ValueError("Task not found")
        task.status = TaskStatus.UNDER_REVIEW
        await self.pg.commit()
        await self.pg.refresh(task)
        return task

    async def get_annotation_result(self, *, task_id: int) -> dict[str, Any] | None:
        # called when a reviewer opens a task to inspect the submitted annotation
        task = await self.pg.get(TaskAssignment, task_id)
        if not task or not task.result_doc_id:
            return None
        result = await self.mongo["annotation_result"].find_one(
            {"_id": ObjectId(task.result_doc_id)}
        )
        if result:
            result["_id"] = str(result["_id"])
        return result

    async def finalize_task(self, *, task_id: int) -> TaskAssignment:
        task = await self.pg.get(TaskAssignment, task_id)
        if not task:
            raise ValueError("Task not found")
        task.status = TaskStatus.FINALIZED
        await self.pg.commit()
        await self.pg.refresh(task)
        await self.update_project_progress(project_id=task.project_id)
        return task

    async def record_quality_metric(
        self,
        *,
        task_assignment_id: int,
        annotator_id: int,
        metric_type: QualityMetricType,
        score: float,
        reviewer_id: int | None = None,
        detail_json: dict[str, Any] | None = None,
        note: str | None = None,
    ) -> QualityMetric:
        metric = QualityMetric(
            task_assignment_id=task_assignment_id,
            annotator_id=annotator_id,
            reviewer_id=reviewer_id,
            metric_type=metric_type,
            score=score,
            detail_json=detail_json or {},
            note=note,
        )
        self.pg.add(metric)
        await self.pg.commit()
        await self.pg.refresh(metric)
        return metric

    # -------------------------------------------------------------------------
    # Export
    # -------------------------------------------------------------------------

    async def export_finalized_tasks(self, *, project_id: int) -> list[dict[str, Any]]:
        # called at GET /projects/{id}/export — bundles postgres metadata + mongo annotation for SFT/RLHF
        stmt: Select[tuple[TaskAssignment]] = select(TaskAssignment).where(
            TaskAssignment.project_id == project_id,
            TaskAssignment.status == TaskStatus.FINALIZED,
        )
        rows = await self.pg.execute(stmt)
        tasks = list(rows.scalars().all())

        export = []
        for task in tasks:
            content = await self.mongo["task_content"].find_one(
                {"_id": ObjectId(task.task_content_doc_id)}
            )
            annotation = await self.mongo["annotation_result"].find_one(
                {"_id": ObjectId(task.result_doc_id)}
            ) if task.result_doc_id else None

            if content:
                content["_id"] = str(content["_id"])
            if annotation:
                annotation["_id"] = str(annotation["_id"])

            export.append({
                "task_id": task.id,
                "project_id": task.project_id,
                "modality": task.modality,
                "content": content,
                "annotation": annotation,
            })

        return export
