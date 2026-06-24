from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.crud.test_case import test_case as test_case_crud
from app.schemas.test_case import (
    TestCaseApplyRequest,
    TestCaseCreate,
    TestCaseGenerateRequest,
    TestCaseOut,
    TestCaseUpdate,
)
from app.core.response import success, fail, paginated
from app.schemas.agent_task import AgentTaskOut
from app.services.agent_task_enqueue import create_and_enqueue_agent_task

router = APIRouter()


@router.get("/")
def read_test_cases(
    project_id: int | None = None,
    module_id: int | None = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    items = test_case_crud.get_multi_by_scope(
        db, project_id=project_id, module_id=module_id, skip=skip, limit=limit
    )
    data = [TestCaseOut.model_validate(i).model_dump() for i in items]
    page = skip // limit + 1 if limit > 0 else 1
    return paginated(items=data, total=len(data), page=page, page_size=limit)


@router.post("/")
def create_test_case(test_case_in: TestCaseCreate, db: Session = Depends(get_db)):
    obj = test_case_crud.create(db, obj_in=test_case_in)
    return success(data=TestCaseOut.model_validate(obj).model_dump())


@router.post("/generate")
def generate_cases(payload: TestCaseGenerateRequest, db: Session = Depends(get_db)):
    task = create_and_enqueue_agent_task(
        db,
        agent_key="test_case",
        project_id=payload.project_id,
        input_payload=payload.model_dump(),
    )
    return success(data=AgentTaskOut.model_validate(task).model_dump(mode="json"))


@router.post("/apply")
def apply_cases(payload: TestCaseApplyRequest, db: Session = Depends(get_db)):
    items = [test_case_crud.create(db, obj_in=item) for item in payload.cases]
    return success(data=[TestCaseOut.model_validate(i).model_dump() for i in items])


@router.get("/{test_case_id}")
def read_test_case(test_case_id: int, db: Session = Depends(get_db)):
    item = test_case_crud.get(db, test_case_id)
    if not item:
        return fail(message="Test case not found", code=404)
    return success(data=TestCaseOut.model_validate(item).model_dump())


@router.put("/{test_case_id}")
def update_test_case(
    test_case_id: int,
    test_case_in: TestCaseUpdate,
    db: Session = Depends(get_db),
):
    item = test_case_crud.get(db, test_case_id)
    if not item:
        return fail(message="Test case not found", code=404)
    updated = test_case_crud.update(db, db_obj=item, obj_in=test_case_in)
    return success(data=TestCaseOut.model_validate(updated).model_dump())


@router.delete("/{test_case_id}")
def delete_test_case(test_case_id: int, db: Session = Depends(get_db)):
    item = test_case_crud.get(db, test_case_id)
    if not item:
        return fail(message="Test case not found", code=404)
    removed = test_case_crud.remove(db, id=test_case_id)
    return success(data=TestCaseOut.model_validate(removed).model_dump())

