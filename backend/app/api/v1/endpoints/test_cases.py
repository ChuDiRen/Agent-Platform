from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.crud.test_case import test_case as test_case_crud
from app.schemas.test_case import (
    TestCaseApplyRequest,
    TestCaseCreate,
    TestCaseGenerateRequest,
    TestCaseGenerateResponse,
    TestCaseOut,
    TestCaseUpdate,
)
from app.services.test_case_agent import generate_test_cases

router = APIRouter()


@router.get("/", response_model=list[TestCaseOut])
def read_test_cases(
    project_id: int | None = None,
    module_id: int | None = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    return test_case_crud.get_multi_by_scope(
        db, project_id=project_id, module_id=module_id, skip=skip, limit=limit
    )


@router.post("/", response_model=TestCaseOut)
def create_test_case(test_case_in: TestCaseCreate, db: Session = Depends(get_db)):
    return test_case_crud.create(db, obj_in=test_case_in)


@router.post("/generate", response_model=TestCaseGenerateResponse)
def generate_cases(payload: TestCaseGenerateRequest):
    cases, elapsed_ms = generate_test_cases(payload)
    return TestCaseGenerateResponse(cases=cases, elapsed_ms=elapsed_ms)


@router.post("/apply", response_model=list[TestCaseOut])
def apply_cases(payload: TestCaseApplyRequest, db: Session = Depends(get_db)):
    return [test_case_crud.create(db, obj_in=item) for item in payload.cases]


@router.get("/{test_case_id}", response_model=TestCaseOut)
def read_test_case(test_case_id: int, db: Session = Depends(get_db)):
    item = test_case_crud.get(db, test_case_id)
    if not item:
        raise HTTPException(status_code=404, detail="Test case not found")
    return item


@router.put("/{test_case_id}", response_model=TestCaseOut)
def update_test_case(
    test_case_id: int,
    test_case_in: TestCaseUpdate,
    db: Session = Depends(get_db),
):
    item = test_case_crud.get(db, test_case_id)
    if not item:
        raise HTTPException(status_code=404, detail="Test case not found")
    return test_case_crud.update(db, db_obj=item, obj_in=test_case_in)


@router.delete("/{test_case_id}", response_model=TestCaseOut)
def delete_test_case(test_case_id: int, db: Session = Depends(get_db)):
    item = test_case_crud.get(db, test_case_id)
    if not item:
        raise HTTPException(status_code=404, detail="Test case not found")
    return test_case_crud.remove(db, id=test_case_id)
