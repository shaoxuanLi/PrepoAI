import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.core.security import create_access_token, create_refresh_token, decode_token
from app.database import get_db
from app.models.user import User, UserStatus
from app.schemas.user import RefreshTokenRequest, Token, UserLogin, UserRegister, UserResponse
from app.services.user_service import UserService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="用户注册",
)
async def register(
    data: UserRegister,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserResponse:
    """
    注册新账号，初始状态为 **PENDING**（需管理员审核激活）。
    """
    if await UserService.get_by_email(db, data.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="该邮箱已被注册",
        )
    if await UserService.get_by_username(db, data.username):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="该用户名已被使用",
        )
    user = await UserService.create_user(db, data)
    return UserResponse.model_validate(user)


@router.post("/login", response_model=Token, summary="用户登录")
async def login(
    data: UserLogin,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Token:
    """
    邮箱 + 密码登录，返回 access_token 与 refresh_token。
    """
    user = await UserService.authenticate(db, data.email, data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="邮箱或密码错误",
        )
    if user.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账号未激活或已被停用，请联系管理员",
        )

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    await UserService.store_refresh_token(db, user, refresh_token)
    await UserService.update_last_login(db, user)

    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=Token, summary="刷新 Access Token")
async def refresh_token(
    body: RefreshTokenRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Token:
    """
    使用有效的 refresh_token 换取新的 access_token 与 refresh_token（Token Rotation）。
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效或过期的 Refresh Token",
    )
    try:
        payload = decode_token(body.refresh_token)
        if payload.type != "refresh":
            raise credentials_exception
        user_id = uuid.UUID(payload.sub)
    except (JWTError, ValueError):
        raise credentials_exception

    user = await UserService.get_by_id(db, user_id)
    if not user or user.refresh_token != body.refresh_token:
        raise credentials_exception
    if user.status != UserStatus.ACTIVE:
        raise credentials_exception

    new_access = create_access_token(user.id)
    new_refresh = create_refresh_token(user.id)
    await UserService.store_refresh_token(db, user, new_refresh)

    return Token(access_token=new_access, refresh_token=new_refresh)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT, summary="登出")
async def logout(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """吊销服务端存储的 refresh_token，无效化当前会话。"""
    await UserService.revoke_refresh_token(db, current_user)


@router.get("/me", response_model=UserResponse, summary="获取当前用户信息")
async def me(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> UserResponse:
    return UserResponse.model_validate(current_user)
