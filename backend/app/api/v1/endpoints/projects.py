from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.crud.project import project as project_crud
from app.schemas.project import Project, ProjectCreate, ProjectUpdate
from app.core.response import success, fail

router = APIRouter()


@router.post("/")
def create_project(project_in: ProjectCreate, db: Session = Depends(get_db)):
    obj = project_crud.create(db, obj_in=project_in)
    return success(data=Project.model_validate(obj).model_dump())


@router.get("/{project_id}")
def read_project(project_id: int, db: Session = Depends(get_db)):
    proj = project_crud.get(db, project_id)
    if not proj:
        return fail(message="Project not found", code=404)
    return success(data=Project.model_validate(proj).model_dump())


@router.get("/")
def read_projects(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = project_crud.get_multi(db, skip=skip, limit=limit)
    return success(data=[Project.model_validate(p).model_dump() for p in items])


@router.put("/{project_id}")
def update_project(project_id: int, project_in: ProjectUpdate, db: Session = Depends(get_db)):
    proj = project_crud.get(db, project_id)
    if not proj:
        return fail(message="Project not found", code=404)
    updated = project_crud.update(db, db_obj=proj, obj_in=project_in)
    return success(data=Project.model_validate(updated).model_dump())


@router.delete("/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db)):
    proj = project_crud.get(db, project_id)
    if not proj:
        return fail(message="Project not found", code=404)
    removed = project_crud.remove(db, id=project_id)
    return success(data=Project.model_validate(removed).model_dump())
