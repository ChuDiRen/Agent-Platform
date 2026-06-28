from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_current_active_user, get_db, require_admin
from app.crud.user import user as user_crud
from app.models.user import User as UserModel
from app.schemas.user import User, UserCreate, UserUpdate, LoginRequest, LoginResponse
from app.core.security import create_access_token
from app.core.response import success, fail

router = APIRouter()


@router.post("/")
def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
    existing = user_crud.get_by_email(db, email=user_in.email)
    if existing:
        return fail(message="Email already registered", code=400)
    obj = user_crud.create(db, obj_in=user_in)
    return success(data=User.model_validate(obj).model_dump())


@router.get("/{user_id}")
def read_user(
    user_id: int,
    db: Session = Depends(get_db),
    _current_user: UserModel = Depends(get_current_active_user),
):
    user = user_crud.get(db, user_id)
    if not user:
        return fail(message="User not found", code=404)
    return success(data=User.model_validate(user).model_dump())


@router.get("/")
def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _current_user: UserModel = Depends(require_admin),
):
    items = user_crud.get_multi(db, skip=skip, limit=limit)
    return success(data=[User.model_validate(u).model_dump() for u in items])


@router.put("/{user_id}")
def update_user(
    user_id: int,
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    _current_user: UserModel = Depends(get_current_active_user),
):
    user = user_crud.get(db, user_id)
    if not user:
        return fail(message="User not found", code=404)
    if user_in.email and user_in.email != user.email:
        existing = user_crud.get_by_email(db, email=user_in.email)
        if existing:
            return fail(message="Email already registered", code=400)
    updated = user_crud.update(db, db_obj=user, obj_in=user_in)
    return success(data=User.model_validate(updated).model_dump())


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    _current_user: UserModel = Depends(require_admin),
):
    user = user_crud.get(db, user_id)
    if not user:
        return fail(message="User not found", code=404)
    removed = user_crud.remove(db, id=user_id)
    return success(data=User.model_validate(removed).model_dump())


@router.post("/login")
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    user = user_crud.authenticate(db, email=login_data.email, password=login_data.password)
    if not user:
        return fail(message="邮箱或密码错误", code=401)
    token = create_access_token(subject=str(user.id))
    result = LoginResponse(access_token=token, token_type="bearer", user=user)
    return success(data=result.model_dump())
