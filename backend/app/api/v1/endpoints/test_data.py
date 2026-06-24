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
from app.core.response import success, fail, paginated
from app.schemas.agent_task import AgentTaskOut
from app.services.agent_task_enqueue import create_and_enqueue_agent_task

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


@router.post("/generate")
def generate_test_data(payload: TestDataGenerateRequest, db: Session = Depends(get_db)):
    task = create_and_enqueue_agent_task(
        db,
        agent_key="test_data",
        project_id=None,
        input_payload=payload.model_dump(),
    )
    return success(data=AgentTaskOut.model_validate(task).model_dump(mode="json"))


@router.get("/templates/")
def read_templates(
    project_id: int | None = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    templates = template_crud.get_multi_by_project(
        db, project_id=project_id, skip=skip, limit=limit
    )
    items = [_template_to_out(t).model_dump() for t in templates]
    page = skip // limit + 1 if limit > 0 else 1
    return paginated(items=items, total=len(items), page=page, page_size=limit)


@router.post("/templates/")
def create_template(template_in: TestDataTemplateCreate, db: Session = Depends(get_db)):
    template = template_crud.create(db, obj_in=template_in)
    return success(data=_template_to_out(template).model_dump())


@router.get("/templates/{template_id}")
def read_template(template_id: int, db: Session = Depends(get_db)):
    template = template_crud.get(db, template_id)
    if not template:
        return fail(message="Template not found", code=404)
    return success(data=_template_to_out(template).model_dump())


@router.put("/templates/{template_id}")
def update_template(
    template_id: int,
    template_in: TestDataTemplateUpdate,
    db: Session = Depends(get_db),
):
    template = template_crud.get(db, template_id)
    if not template:
        return fail(message="Template not found", code=404)
    updated = template_crud.update(db, db_obj=template, obj_in=template_in)
    return success(data=_template_to_out(updated).model_dump())


@router.delete("/templates/{template_id}")
def delete_template(template_id: int, db: Session = Depends(get_db)):
    template = template_crud.get(db, template_id)
    if not template:
        return fail(message="Template not found", code=404)
    removed = template_crud.remove(db, id=template_id)
    return success(data=_template_to_out(removed).model_dump())

