from datetime import datetime
from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase
from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend_db.db_models import (
    Project,
    ProjectStatus,
    QualityMetric,
    QualityMetricType,
    TaskAssignment,
    TaskStatus,
)


class DBInterface:
    """Hybrid DB interface: relational metadata in PostgreSQL, flexible content in MongoDB."""

    def __init__(self, pg: AsyncSession, mongo: AsyncIOMotorDatabase):
        self.pg = pg
        self.mongo = mongo

    async def create_project(self, *, name: str, client_name: str, created_by: int) -> Project:
        project = Project(name=name, client_name=client_name, created_by=created_by)
        self.pg.add(project)
        await self.pg.commit()
        await self.pg.refresh(project)
        return project

    async def import_task_contents(
        self,
        *,
        project_id: int,
        modality: str,
        task_contents: list[dict[str, Any]],
    ) -> list[TaskAssignment]:
        inserted = await self.mongo["task_content"].insert_many(
            [
                {
                    **item,
                    "project_id": project_id,
                    "modality": modality,
                    "created_at": datetime.utcnow(),
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
            for doc_id in inserted.inserted_ids
        ]
        self.pg.add_all(tasks)

        project = await self.pg.get(Project, project_id)
        if project:
            project.status = ProjectStatus.IN_PROGRESS

        await self.pg.commit()
        return tasks

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
        task.locked_at = datetime.utcnow()
        task.started_at = datetime.utcnow()
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
                "submitted_at": datetime.utcnow(),
            }
        )

        task.result_doc_id = str(result.inserted_id)
        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.utcnow()
        await self.pg.commit()
        await self.pg.refresh(task)
        return task

    async def mark_under_review(self, *, task_id: int) -> TaskAssignment:
        task = await self.pg.get(TaskAssignment, task_id)
        if not task:
            raise ValueError("Task not found")
        task.status = TaskStatus.UNDER_REVIEW
        await self.pg.commit()
        await self.pg.refresh(task)
        return task

    async def finalize_task(self, *, task_id: int) -> TaskAssignment:
        task = await self.pg.get(TaskAssignment, task_id)
        if not task:
            raise ValueError("Task not found")
        task.status = TaskStatus.FINALIZED
        await self.pg.commit()
        await self.pg.refresh(task)
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
