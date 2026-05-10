from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    email: str
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserUpdate(UserBase):
    password: Optional[str] = None
    is_active: Optional[bool] = None


class UserInDB(UserBase):
    id: int
    hashed_password: str
    is_active: bool
    is_superuser: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class User(UserBase):
    id: int
    is_active: bool
    is_superuser: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: User
