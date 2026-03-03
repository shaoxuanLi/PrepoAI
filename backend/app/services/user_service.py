import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, verify_password
from app.models.user import User, UserRole, UserStatus
from app.schemas.user import UserAdminUpdate, UserRegister, UserUpdate


class UserService:
    """Business logic for user management."""

    # ─────────────────────── queries ─────────────────────────

    @staticmethod
    async def get_by_id(db: AsyncSession, user_id: uuid.UUID) -> Optional[User]:
        result = await db.execute(
            select(User).where(User.id == user_id, User.is_deleted.is_(False))
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_email(db: AsyncSession, email: str) -> Optional[User]:
        result = await db.execute(
            select(User).where(User.email == email, User.is_deleted.is_(False))
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_username(db: AsyncSession, username: str) -> Optional[User]:
        result = await db.execute(
            select(User).where(User.username == username, User.is_deleted.is_(False))
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list_users(
        db: AsyncSession,
        *,
        page: int = 1,
        page_size: int = 20,
        role: Optional[UserRole] = None,
        status: Optional[UserStatus] = None,
        search: Optional[str] = None,
    ) -> tuple[list[User], int]:
        query = select(User).where(User.is_deleted.is_(False))

        if role:
            query = query.where(User.role == role)
        if status:
            query = query.where(User.status == status)
        if search:
            like = f"%{search}%"
            query = query.where(
                User.email.ilike(like) | User.username.ilike(like) | User.full_name.ilike(like)
            )

        # total count
        count_result = await db.execute(
            select(func.count()).select_from(query.subquery())
        )
        total = count_result.scalar_one()

        # paginated results
        result = await db.execute(
            query.order_by(User.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return result.scalars().all(), total

    # ────────────────────── mutations ────────────────────────

    @staticmethod
    async def create_user(
        db: AsyncSession,
        data: UserRegister,
        role: UserRole = UserRole.ANNOTATOR,
        status: UserStatus = UserStatus.PENDING,
    ) -> User:
        user = User(
            email=data.email,
            username=data.username,
            full_name=data.full_name,
            bio=data.bio,
            avatar_url=data.avatar_url,
            hashed_password=hash_password(data.password),
            role=role,
            status=status,
        )
        db.add(user)
        await db.flush()
        await db.refresh(user)
        return user

    @staticmethod
    async def authenticate(db: AsyncSession, email: str, password: str) -> Optional[User]:
        user = await UserService.get_by_email(db, email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    @staticmethod
    async def update_last_login(db: AsyncSession, user: User) -> None:
        user.last_login_at = datetime.now(timezone.utc)
        await db.flush()

    @staticmethod
    async def store_refresh_token(db: AsyncSession, user: User, token: str) -> None:
        user.refresh_token = token
        await db.flush()

    @staticmethod
    async def revoke_refresh_token(db: AsyncSession, user: User) -> None:
        user.refresh_token = None
        await db.flush()

    @staticmethod
    async def update_profile(db: AsyncSession, user: User, data: UserUpdate) -> User:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(user, field, value)
        await db.flush()
        await db.refresh(user)
        return user

    @staticmethod
    async def change_password(
        db: AsyncSession, user: User, current_password: str, new_password: str
    ) -> bool:
        if not verify_password(current_password, user.hashed_password):
            return False
        user.hashed_password = hash_password(new_password)
        await db.flush()
        return True

    @staticmethod
    async def admin_update(db: AsyncSession, user: User, data: UserAdminUpdate) -> User:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(user, field, value)
        await db.flush()
        await db.refresh(user)
        return user

    @staticmethod
    async def soft_delete(db: AsyncSession, user: User) -> None:
        user.is_deleted = True
        await db.flush()

    # ──────────────────────── seed ───────────────────────────

    @staticmethod
    async def ensure_superadmin(
        db: AsyncSession,
        email: str,
        username: str,
        full_name: str,
        password: str,
    ) -> User:
        """Create the initial super-admin if not present."""
        existing = await UserService.get_by_email(db, email)
        if existing:
            return existing
        from app.schemas.user import UserRegister  # local to avoid circular import
        data = UserRegister(
            email=email,
            username=username,
            full_name=full_name,
            password=password,
        )
        user = await UserService.create_user(
            db, data, role=UserRole.SUPERADMIN, status=UserStatus.ACTIVE
        )
        return user
