"""create users table

Revision ID: 001_users
Revises:
Create Date: 2026-03-01 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "001_users"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enums
    user_role = postgresql.ENUM(
        "SUPERADMIN", "ADMIN", "PROJECT_MANAGER", "ANNOTATOR", "REVIEWER",
        name="user_role",
    )
    user_status = postgresql.ENUM(
        "ACTIVE", "INACTIVE", "PENDING",
        name="user_status",
    )
    user_role.create(op.get_bind(), checkfirst=True)
    user_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("username", sa.String(64), nullable=False),
        sa.Column("full_name", sa.String(128), nullable=False, server_default=""),
        sa.Column("hashed_password", sa.String(256), nullable=False),
        sa.Column("role", sa.Enum("SUPERADMIN", "ADMIN", "PROJECT_MANAGER", "ANNOTATOR", "REVIEWER", name="user_role"), nullable=False, server_default="ANNOTATOR"),
        sa.Column("status", sa.Enum("ACTIVE", "INACTIVE", "PENDING", name="user_status"), nullable=False, server_default="PENDING"),
        sa.Column("avatar_url", sa.Text, nullable=True),
        sa.Column("bio", sa.String(512), nullable=True),
        sa.Column("refresh_token", sa.String(512), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_deleted", sa.Boolean, nullable=False, server_default="false"),
    )
    op.create_index("ix_users_id", "users", ["id"])
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_username", "users", ["username"], unique=True)


def downgrade() -> None:
    op.drop_table("users")
    op.execute("DROP TYPE IF EXISTS user_role")
    op.execute("DROP TYPE IF EXISTS user_status")
