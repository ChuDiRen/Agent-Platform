from typing import Any, Generic, TypeVar
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.config import settings
from app.crud.user import user as user_crud
from app.db.session import SessionLocal
from app.db.base_class import Base
from app.models.user import User as UserModel

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

oauth2_scheme = HTTPBearer(auto_error=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _authentication_error() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="认证凭据无效或已过期",
        headers={"WWW-Authenticate": "Bearer"},
    )


def decode_access_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(oauth2_scheme),
) -> str:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise _authentication_error()
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        subject = payload.get("sub")
    except JWTError as exc:
        raise _authentication_error() from exc
    if not subject:
        raise _authentication_error()
    return str(subject)


def get_current_user(
    subject: str = Depends(decode_access_token),
    db: Session = Depends(get_db),
) -> UserModel:
    try:
        user_id = int(subject)
    except ValueError as exc:
        raise _authentication_error() from exc
    user = user_crud.get(db, user_id)
    if not user:
        raise _authentication_error()
    return user


def get_current_active_user(
    current_user: UserModel = Depends(get_current_user),
) -> UserModel:
    if not user_crud.is_active(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="用户已被禁用")
    return current_user


def require_admin(
    current_user: UserModel = Depends(get_current_active_user),
) -> UserModel:
    if not user_crud.is_superuser(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="需要管理员权限")
    return current_user
