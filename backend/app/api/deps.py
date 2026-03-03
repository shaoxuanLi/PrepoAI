import uuid
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_token
from app.database import get_db
from app.models.user import User, UserRole, UserStatus
from app.services.user_service import UserService

bearer_scheme = HTTPBearer(auto_error=True)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """Extract and validate the JWT access token, return the active user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证身份凭证",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(credentials.credentials)
        if payload.type != "access":
            raise credentials_exception
        user_id = uuid.UUID(payload.sub)
    except (JWTError, ValueError):
        raise credentials_exception

    user = await UserService.get_by_id(db, user_id)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    if current_user.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账号已被停用，请联系管理员",
        )
    return current_user


def require_roles(*roles: UserRole):
    """Dependency factory: checks that the current user has one of the given roles."""

    async def _check(
        current_user: Annotated[User, Depends(get_current_active_user)],
    ) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足",
            )
        return current_user

    return _check


# Convenience shortcuts
require_admin = require_roles(UserRole.SUPERADMIN, UserRole.ADMIN)
require_superadmin = require_roles(UserRole.SUPERADMIN)
require_manager_or_above = require_roles(
    UserRole.SUPERADMIN, UserRole.ADMIN, UserRole.PROJECT_MANAGER
)
