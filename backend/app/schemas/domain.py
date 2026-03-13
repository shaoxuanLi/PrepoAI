from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from backend_db.db_models import ProjectStatus, QualityMetricType, TaskStatus, UserRole


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=64)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)
    role: UserRole


class UserLogin(BaseModel):
    username: str
    password: str


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: EmailStr
    role: UserRole
    points: int
    is_active: bool


class ProjectCreate(BaseModel):
    name: str
    client_name: str
    created_by: int


class ProjectRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    client_name: str
    status: ProjectStatus
    progress: float
    dashboard_endpoint: str | None
    created_by: int


class ImportTaskContentsRequest(BaseModel):
    modality: str = Field(default="text")
    task_contents: list[dict[str, Any]]


class TaskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    task_content_doc_id: str
    assignee_id: int | None
    status: TaskStatus
    modality: str
    result_doc_id: str | None
    started_at: datetime | None
    completed_at: datetime | None


class TaskClaimRequest(BaseModel):
    user_id: int


class TaskSubmitRequest(BaseModel):
    user_id: int
    annotation_payload: dict[str, Any]


class QualityMetricCreate(BaseModel):
    task_assignment_id: int
    annotator_id: int
    reviewer_id: int | None = None
    metric_type: QualityMetricType
    score: float
    detail_json: dict[str, Any] = Field(default_factory=dict)
    note: str | None = None


class QualityMetricRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    task_assignment_id: int
    annotator_id: int
    reviewer_id: int | None
    metric_type: QualityMetricType
    score: float
    detail_json: dict[str, Any]
    note: str | None
    created_at: datetime
