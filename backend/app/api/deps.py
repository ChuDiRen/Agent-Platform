from typing import Any, Generic, TypeVar
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.config import settings
from app.crud.user import user as user_crud
from app.db.session import SessionLocal
from app.crud.base import CRUDBase
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


class CRUDRouter(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(
        self,
        crud: CRUDBase[ModelType, CreateSchemaType, UpdateSchemaType],
        prefix: str = "",
        tag: str = "",
    ):
        self.crud = crud
        self.router = APIRouter(prefix=prefix, tags=[tag] if tag else [])
        self._register_routes()

    def _register_routes(self):
        @self.router.post("/", response_model=Any)
        def create_item(obj_in: CreateSchemaType, db: Session = Depends(get_db)):
            return self.crud.create(db, obj_in=obj_in)

        @self.router.get("/{item_id}", response_model=Any)
        def read_item(item_id: int, db: Session = Depends(get_db)):
            item = self.crud.get(db, item_id)
            if not item:
                raise HTTPException(status_code=404, detail="Item not found")
            return item

        @self.router.get("/", response_model=list[Any])
        def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
            return self.crud.get_multi(db, skip=skip, limit=limit)

        @self.router.put("/{item_id}", response_model=Any)
        def update_item(
            item_id: int, obj_in: UpdateSchemaType, db: Session = Depends(get_db)
        ):
            item = self.crud.get(db, item_id)
            if not item:
                raise HTTPException(status_code=404, detail="Item not found")
            return self.crud.update(db, db_obj=item, obj_in=obj_in)

        @self.router.delete("/{item_id}", response_model=Any)
        def delete_item(item_id: int, db: Session = Depends(get_db)):
            item = self.crud.get(db, item_id)
            if not item:
                raise HTTPException(status_code=404, detail="Item not found")
            return self.crud.remove(db, id=item_id)
