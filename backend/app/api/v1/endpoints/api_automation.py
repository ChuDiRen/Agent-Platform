import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.crud.api_test_cases_exec import api_test_cases_exec as exec_crud
from app.schemas.api_automation import (
    ApiAutomationCase,
    ApiTestExecCreate,
    ApiTestExecOut,
    ApiTestExecRunRequest,
)
from app.services.api_automation_agent import (
    build_execution_details,
    get_api_automation_case,
    list_api_automation_cases,
)

router = APIRouter()


def _exec_to_out(item) -> ApiTestExecOut:
    data = {
        "id": item.id,
        "project_id": item.project_id,
        "name": item.name,
        "exec_type": item.exec_type,
        "case_ids": json.loads(item.case_ids or "[]"),
        "details": json.loads(item.details or "{}") or None,
        "desc": item.desc,
        "exec_param": json.loads(item.exec_param or "{}"),
        "exec_status": item.exec_status,
        "created_at": item.created_at,
        "updated_at": item.updated_at,
    }
    return ApiTestExecOut.model_validate(data)


@router.get("/cases", response_model=list[ApiAutomationCase])
def read_api_automation_cases(
    project_id: int | None = None,
    name: str | None = None,
    priority: int | None = None,
    module_id: int | None = None,
    exec_type: str | None = None,
):
    return list_api_automation_cases(
        project_id=project_id,
        name=name,
        priority=priority,
        module_id=module_id,
        exec_type=exec_type,
    )


@router.get("/cases/{case_id}", response_model=ApiAutomationCase)
def read_api_automation_case(case_id: int):
    item = get_api_automation_case(case_id)
    if not item:
        raise HTTPException(status_code=404, detail="API automation case not found")
    return item


@router.get("/execs", response_model=list[ApiTestExecOut])
def read_api_automation_execs(
    project_id: int | None = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    return [
        _exec_to_out(item)
        for item in exec_crud.get_multi_by_project(db, project_id=project_id, skip=skip, limit=limit)
    ]


@router.post("/execs", response_model=ApiTestExecOut)
def create_api_automation_exec(payload: ApiTestExecRunRequest, db: Session = Depends(get_db)):
    missing = [case_id for case_id in payload.case_ids if not get_api_automation_case(case_id)]
    if missing:
        raise HTTPException(status_code=404, detail=f"API automation case not found: {missing[0]}")
    details = build_execution_details(case_ids=payload.case_ids, exec_param=payload.exec_param)
    created = exec_crud.create(
        db,
        obj_in=ApiTestExecCreate(
            project_id=payload.project_id,
            name=payload.name,
            exec_type=payload.exec_type,
            case_ids=payload.case_ids,
            details=details,
            desc=payload.desc,
            exec_param=payload.exec_param,
            exec_status="已完成",
        ),
    )
    return _exec_to_out(created)


@router.get("/execs/{exec_id}", response_model=ApiTestExecOut)
def read_api_automation_exec(exec_id: int, db: Session = Depends(get_db)):
    item = exec_crud.get(db, exec_id)
    if not item:
        raise HTTPException(status_code=404, detail="API automation execution not found")
    return _exec_to_out(item)


@router.post("/execs/{exec_id}/copy", response_model=ApiTestExecOut)
def copy_api_automation_exec(exec_id: int, db: Session = Depends(get_db)):
    item = exec_crud.get(db, exec_id)
    if not item:
        raise HTTPException(status_code=404, detail="API automation execution not found")
    copied = exec_crud.create(
        db,
        obj_in=ApiTestExecCreate(
            project_id=item.project_id,
            name=f"{item.name}-复制执行",
            exec_type=item.exec_type,
            case_ids=json.loads(item.case_ids or "[]"),
            details=json.loads(item.details or "{}") or None,
            desc=item.desc,
            exec_param=json.loads(item.exec_param or "{}"),
            exec_status="已完成",
        ),
    )
    return _exec_to_out(copied)


@router.delete("/execs/{exec_id}", response_model=ApiTestExecOut)
def delete_api_automation_exec(exec_id: int, db: Session = Depends(get_db)):
    item = exec_crud.get(db, exec_id)
    if not item:
        raise HTTPException(status_code=404, detail="API automation execution not found")
    removed = exec_crud.remove(db, id=exec_id)
    return _exec_to_out(removed)
