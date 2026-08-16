from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, get_db
from app.crud.project import project as project_crud
from app.models.user import User as UserModel
from app.schemas.project import (
    ProjectCreate,
    ProjectOut,
    ProjectUpdate,
    ProjectVerifyRequest,
    ProjectVerifyResponse,
)
from app.core.response import success, fail

router = APIRouter()


def _can_access(project, user: UserModel) -> bool:
    """管理员或项目创建者可访问。"""
    return user.is_superuser or (project.owner_id is not None and project.owner_id == user.id)


@router.post("/")
def create_project(
    project_in: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user),
):
    obj = project_crud.create(db, obj_in=project_in)
    # 归属当前创建者
    obj.owner_id = current_user.id
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return success(data=ProjectOut.model_validate(obj).model_dump())


@router.get("/{project_id}")
def read_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user),
):
    proj = project_crud.get(db, project_id)
    if not proj:
        return fail(message="Project not found", code=404)
    if not _can_access(proj, current_user):
        return fail(message="无权访问该项目", code=403)
    return success(data=ProjectOut.model_validate(proj).model_dump())


@router.get("/")
def read_projects(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user),
):
    if current_user.is_superuser:
        items = project_crud.get_multi(db, skip=skip, limit=limit)
    else:
        items = (
            db.query(project_crud.model)
            .filter(project_crud.model.owner_id == current_user.id)
            .offset(skip)
            .limit(limit)
            .all()
        )
    return success(data=[ProjectOut.model_validate(p).model_dump() for p in items])


@router.put("/{project_id}")
def update_project(
    project_id: int,
    project_in: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user),
):
    proj = project_crud.get(db, project_id)
    if not proj:
        return fail(message="Project not found", code=404)
    if not _can_access(proj, current_user):
        return fail(message="无权修改该项目", code=403)
    updated = project_crud.update(db, db_obj=proj, obj_in=project_in)
    return success(data=ProjectOut.model_validate(updated).model_dump())


@router.delete("/{project_id}")
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user),
):
    proj = project_crud.get(db, project_id)
    if not proj:
        return fail(message="Project not found", code=404)
    if not _can_access(proj, current_user):
        return fail(message="无权删除该项目", code=403)
    removed = project_crud.remove(db, id=project_id)
    return success(data=ProjectOut.model_validate(removed).model_dump())


@router.post("/{project_id}/verify-password")
def verify_project_password(
    project_id: int,
    payload: ProjectVerifyRequest,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user),
):
    proj = project_crud.get(db, project_id)
    if not proj:
        return fail(message="Project not found", code=404)
    if not _can_access(proj, current_user):
        return fail(message="无权访问该项目", code=403)
    valid = project_crud.verify_password(db, project=proj, password=payload.password)
    return success(data=ProjectVerifyResponse(valid=valid).model_dump())
