import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models.user import UserRole, UserStatus


# ─────────────────────────── base ────────────────────────────

class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=64, pattern=r"^[a-zA-Z0-9_\-]+$")
    full_name: str = Field("", max_length=128)
    bio: Optional[str] = Field(None, max_length=512)
    avatar_url: Optional[str] = None


# ─────────────────────────── register ────────────────────────

class UserRegister(UserBase):
    password: str = Field(..., min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def password_complexity(cls, v: str) -> str:
        if not any(c.isupper() for c in v):
            raise ValueError("密码需包含至少一个大写字母")
        if not any(c.islower() for c in v):
            raise ValueError("密码需包含至少一个小写字母")
        if not any(c.isdigit() for c in v):
            raise ValueError("密码需包含至少一个数字")
        return v


# ─────────────────────────── login ───────────────────────────

class UserLogin(BaseModel):
    email: EmailStr
    password: str


# ─────────────────────────── update ──────────────────────────

class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, max_length=128)
    bio: Optional[str] = Field(None, max_length=512)
    avatar_url: Optional[str] = None


class UserUpdatePassword(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=128)

    @field_validator("new_password")
    @classmethod
    def password_complexity(cls, v: str) -> str:
        if not any(c.isupper() for c in v):
            raise ValueError("密码需包含至少一个大写字母")
        if not any(c.islower() for c in v):
            raise ValueError("密码需包含至少一个小写字母")
        if not any(c.isdigit() for c in v):
            raise ValueError("密码需包含至少一个数字")
        return v


# ─────────────────── admin-only updates ──────────────────────

class UserAdminUpdate(BaseModel):
    role: Optional[UserRole] = None
    status: Optional[UserStatus] = None
    full_name: Optional[str] = Field(None, max_length=128)


# ─────────────────────────── response ────────────────────────

class UserResponse(BaseModel):
    id: uuid.UUID
    email: EmailStr
    username: str
    full_name: str
    role: UserRole
    status: UserStatus
    avatar_url: Optional[str]
    bio: Optional[str]
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime]

    model_config = {"from_attributes": True}


class UserListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[UserResponse]


# ─────────────────────────── tokens ──────────────────────────

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str           # user id
    type: str          # "access" | "refresh"
    exp: Optional[int] = None


class RefreshTokenRequest(BaseModel):
    refresh_token: str
