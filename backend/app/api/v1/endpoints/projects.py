from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.crud.project import project as project_crud
from app.schemas.project import Project, ProjectCreate, ProjectUpdate

router = APIRouter()


@router.post("/", response_model=Project)
def create_project(project_in: ProjectCreate, db: Session = Depends(get_db)):
    return project_crud.create(db, obj_in=project_in)


@router.get("/{project_id}", response_model=Project)
def read_project(project_id: int, db: Session = Depends(get_db)):
    proj = project_crud.get(db, project_id)
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")
    return proj


@router.get("/", response_model=list[Project])
def read_projects(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return project_crud.get_multi(db, skip=skip, limit=limit)


@router.put("/{project_id}", response_model=Project)
def update_project(project_id: int, project_in: ProjectUpdate, db: Session = Depends(get_db)):
    proj = project_crud.get(db, project_id)
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")
    return project_crud.update(db, db_obj=proj, obj_in=project_in)


@router.delete("/{project_id}", response_model=Project)
def delete_project(project_id: int, db: Session = Depends(get_db)):
    proj = project_crud.get(db, project_id)
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")
    return project_crud.remove(db, id=project_id)
