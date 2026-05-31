import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.crud.test_data_template import test_data_template as template_crud
from app.schemas.test_data import (
    TestDataField,
    TestDataGenerateRequest,
    TestDataGenerateResponse,
    TestDataTemplateCreate,
    TestDataTemplateOut,
    TestDataTemplateUpdate,
)
from app.services.test_data_agent import generate_test_data_response

router = APIRouter()


def _template_to_out(template) -> TestDataTemplateOut:
    data = {
        "id": template.id,
        "project_id": template.project_id,
        "name": template.name,
        "description": template.description,
        "fields": json.loads(template.fields or "[]"),
        "hint": template.hint,
        "count": template.count,
        "format": template.format,
        "lang": template.lang,
        "created_at": template.created_at,
        "updated_at": template.updated_at,
    }
    return TestDataTemplateOut.model_validate(data)


@router.post("/generate", response_model=TestDataGenerateResponse)
def generate_test_data(payload: TestDataGenerateRequest):
    return generate_test_data_response(payload)


@router.get("/templates/", response_model=list[TestDataTemplateOut])
def read_templates(
    project_id: int | None = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    templates = template_crud.get_multi_by_project(
        db, project_id=project_id, skip=skip, limit=limit
    )
    return [_template_to_out(template) for template in templates]


@router.post("/templates/", response_model=TestDataTemplateOut)
def create_template(template_in: TestDataTemplateCreate, db: Session = Depends(get_db)):
    template = template_crud.create(db, obj_in=template_in)
    return _template_to_out(template)


@router.get("/templates/{template_id}", response_model=TestDataTemplateOut)
def read_template(template_id: int, db: Session = Depends(get_db)):
    template = template_crud.get(db, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return _template_to_out(template)


@router.put("/templates/{template_id}", response_model=TestDataTemplateOut)
def update_template(
    template_id: int,
    template_in: TestDataTemplateUpdate,
    db: Session = Depends(get_db),
):
    template = template_crud.get(db, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    updated = template_crud.update(db, db_obj=template, obj_in=template_in)
    return _template_to_out(updated)


@router.delete("/templates/{template_id}", response_model=TestDataTemplateOut)
def delete_template(template_id: int, db: Session = Depends(get_db)):
    template = template_crud.get(db, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    removed = template_crud.remove(db, id=template_id)
    return _template_to_out(removed)
