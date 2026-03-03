import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class UserRole(str, enum.Enum):
    """Platform-level roles."""
    SUPERADMIN = "SUPERADMIN"   # 超级管理员：管理全平台
    ADMIN = "ADMIN"             # 管理员：管理项目与成员
    PROJECT_MANAGER = "PROJECT_MANAGER"  # 项目经理：创建/管理项目
    ANNOTATOR = "ANNOTATOR"     # 标注员：执行标注任务
    REVIEWER = "REVIEWER"       # 审核员：审核标注结果


class UserStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"       # 正常
    INACTIVE = "INACTIVE"   # 禁用
    PENDING = "PENDING"     # 待审核（注册后等待管理员激活）


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    username: Mapped[str] = mapped_column(
        String(64), unique=True, index=True, nullable=False
    )
    full_name: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    hashed_password: Mapped[str] = mapped_column(String(256), nullable=False)

    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role"), nullable=False, default=UserRole.ANNOTATOR
    )
    status: Mapped[UserStatus] = mapped_column(
        Enum(UserStatus, name="user_status"), nullable=False, default=UserStatus.PENDING
    )

    avatar_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    bio: Mapped[str | None] = mapped_column(String(512), nullable=True)

    # Refresh token storage (single active session; extend to a separate table for multi-device)
    refresh_token: Mapped[str | None] = mapped_column(String(512), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Soft-delete flag
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email} role={self.role}>"
