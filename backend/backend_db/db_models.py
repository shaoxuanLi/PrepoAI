from datetime import datetime
from enum import Enum

from sqlalchemy import JSON, DateTime, Enum as SAEnum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend_db.db import Base


class UserRole(str, Enum):
    ADMIN = "admin"
    EMPLOYER = "employer"
    ANNOTATOR = "annotator"
    AUDITOR = "auditor"
    SENIOR_ANNOTATOR = "senior_annotator"


class ProjectStatus(str, Enum):
    BLANK = "blank"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    UNDER_REVIEW = "under_review"
    FINALIZED = "finalized"


class QualityMetricType(str, Enum):
    HUMAN_F1 = "human_f1"
    GOLDEN_MATCH = "golden_match"
    ARBITRATION = "arbitration"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(SAEnum(UserRole), nullable=False)
    points: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    assigned_tasks: Mapped[list["TaskAssignment"]] = relationship(
        foreign_keys="TaskAssignment.assignee_id", back_populates="assignee"
    )
    locked_tasks: Mapped[list["TaskAssignment"]] = relationship(
        foreign_keys="TaskAssignment.locked_by_id", back_populates="locked_by"
    )
    quality_metrics: Mapped[list["QualityMetric"]] = relationship(
        foreign_keys="QualityMetric.annotator_id", back_populates="annotator"
    )


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    client_name: Mapped[str] = mapped_column(String(128), nullable=False)
    status: Mapped[ProjectStatus] = mapped_column(
        SAEnum(ProjectStatus), default=ProjectStatus.BLANK, nullable=False
    )
    progress: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    dashboard_endpoint: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    tasks: Mapped[list["TaskAssignment"]] = relationship(back_populates="project")


class TaskAssignment(Base):
    __tablename__ = "task_assignments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)
    task_content_doc_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    assignee_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    status: Mapped[TaskStatus] = mapped_column(
        SAEnum(TaskStatus), default=TaskStatus.PENDING, nullable=False
    )
    modality: Mapped[str] = mapped_column(String(32), default="text", nullable=False)
    result_doc_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    locked_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    locked_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    project: Mapped[Project] = relationship(back_populates="tasks")
    assignee: Mapped["User | None"] = relationship(
        foreign_keys=[assignee_id], back_populates="assigned_tasks"
    )
    locked_by: Mapped["User | None"] = relationship(
        foreign_keys=[locked_by_id], back_populates="locked_tasks"
    )
    quality_metrics: Mapped[list["QualityMetric"]] = relationship(
        foreign_keys="QualityMetric.task_assignment_id", back_populates="task_assignment"
    )


class QualityMetric(Base):
    __tablename__ = "quality_metrics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    task_assignment_id: Mapped[int] = mapped_column(ForeignKey("task_assignments.id"), nullable=False)
    annotator_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    reviewer_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    metric_type: Mapped[QualityMetricType] = mapped_column(SAEnum(QualityMetricType), nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    detail_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    task_assignment: Mapped["TaskAssignment"] = relationship(
        foreign_keys=[task_assignment_id], back_populates="quality_metrics"
    )
    annotator: Mapped["User"] = relationship(
        foreign_keys=[annotator_id], back_populates="quality_metrics"
    )
    reviewer: Mapped["User | None"] = relationship(
        foreign_keys=[reviewer_id]
    )
