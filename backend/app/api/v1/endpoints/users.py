import uuid
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user, require_admin
from app.database import get_db
from app.models.user import User, UserRole, UserStatus
from app.schemas.user import (
    UserAdminUpdate,
    UserListResponse,
    UserResponse,
    UserUpdate,
    UserUpdatePassword,
)
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


# ─────────────────── self-service endpoints ───────────────────

@router.get("/me", response_model=UserResponse, summary="获取当前用户资料")
async def get_my_profile(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> UserResponse:
    return UserResponse.model_validate(current_user)


@router.patch("/me", response_model=UserResponse, summary="更新当前用户资料")
async def update_my_profile(
    data: UserUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserResponse:
    user = await UserService.update_profile(db, current_user, data)
    return UserResponse.model_validate(user)


@router.put("/me/password", status_code=status.HTTP_204_NO_CONTENT, summary="修改密码")
async def change_my_password(
    data: UserUpdatePassword,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    success = await UserService.change_password(
        db, current_user, data.current_password, data.new_password
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="当前密码不正确",
        )


# ─────────────────── admin endpoints ─────────────────────────

@router.get(
    "",
    response_model=UserListResponse,
    dependencies=[Depends(require_admin)],
    summary="[管理员] 获取用户列表",
)
async def list_users(
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    role: Optional[UserRole] = Query(None),
    status: Optional[UserStatus] = Query(None),
    search: Optional[str] = Query(None, max_length=100),
) -> UserListResponse:
    users, total = await UserService.list_users(
        db, page=page, page_size=page_size, role=role, status=status, search=search
    )
    return UserListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[UserResponse.model_validate(u) for u in users],
    )


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    dependencies=[Depends(require_admin)],
    summary="[管理员] 获取指定用户",
)
async def get_user(
    user_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserResponse:
    user = await UserService.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    return UserResponse.model_validate(user)


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    dependencies=[Depends(require_admin)],
    summary="[管理员] 修改用户角色/状态",
)
async def admin_update_user(
    user_id: uuid.UUID,
    data: UserAdminUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> UserResponse:
    user = await UserService.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")

    # Protect superadmin from demotion by non-superadmin
    if (
        user.role == UserRole.SUPERADMIN
        and current_user.role != UserRole.SUPERADMIN
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权修改超级管理员",
        )

    user = await UserService.admin_update(db, user, data)
    return UserResponse.model_validate(user)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin)],
    summary="[管理员] 软删除用户",
)
async def delete_user(
    user_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> None:
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除自己的账号",
        )
    user = await UserService.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    if user.role == UserRole.SUPERADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权删除超级管理员",
        )
    await UserService.soft_delete(db, user)
