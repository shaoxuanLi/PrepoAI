from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_pg_session
from app.core.security import create_access_token, get_password_hash, verify_password
from app.schemas.domain import Token, UserCreate, UserLogin, UserRead
from backend_db.db_models import User

router = APIRouter()


@router.post("/register", response_model=UserRead)
async def register_user(payload: UserCreate, pg: AsyncSession = Depends(get_pg_session)) -> User:
    exists_stmt = select(User).where((User.username == payload.username) | (User.email == payload.email))
    existing = (await pg.execute(exists_stmt)).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")

    user = User(
        username=payload.username,
        email=payload.email,
        password_hash=get_password_hash(payload.password),
        role=payload.role,
    )
    pg.add(user)
    await pg.commit()
    await pg.refresh(user)
    return user


@router.post("/login", response_model=Token)
async def login_user(payload: UserLogin, pg: AsyncSession = Depends(get_pg_session)) -> Token:
    stmt = select(User).where(User.username == payload.username)
    user = (await pg.execute(stmt)).scalar_one_or_none()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token(subject=str(user.id), role=user.role.value)
    return Token(access_token=token)
