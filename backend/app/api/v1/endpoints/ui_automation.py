import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.crud.ui_test_cases_exec import ui_test_cases_exec as exec_crud
from app.schemas.ui_automation import (
    UiAutomationCase,
    UiTestExecCreate,
    UiTestExecOut,
    UiTestExecRunRequest,
)
from app.agents.ui_automation.service import (
    build_ui_execution_details,
    get_ui_automation_case,
    list_ui_automation_cases,
)
from app.core.response import success, fail, paginated

router = APIRouter()


def _exec_to_out(item) -> UiTestExecOut:
    return UiTestExecOut.model_validate(
        {
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
    )


@router.get("/cases")
def read_ui_automation_cases(
    project_id: int | None = None,
    name: str | None = None,
    priority: int | None = None,
    module_id: int | None = None,
    exec_type: str | None = None,
):
    items = list_ui_automation_cases(project_id=project_id, name=name, priority=priority, module_id=module_id, exec_type=exec_type)
    return success(data=[UiAutomationCase.model_validate(i).model_dump() for i in items])


@router.get("/cases/{case_id}")
def read_ui_automation_case(case_id: int):
    item = get_ui_automation_case(case_id)
    if not item:
        return fail(message="UI automation case not found", code=404)
    return success(data=UiAutomationCase.model_validate(item).model_dump())


@router.get("/execs")
def read_ui_automation_execs(project_id: int | None = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = exec_crud.get_multi_by_project(db, project_id=project_id, skip=skip, limit=limit)
    data = [_exec_to_out(i).model_dump() for i in items]
    page = skip // limit + 1 if limit > 0 else 1
    return paginated(items=data, total=len(data), page=page, page_size=limit)


@router.post("/execs")
def create_ui_automation_exec(payload: UiTestExecRunRequest, db: Session = Depends(get_db)):
    missing = [case_id for case_id in payload.case_ids if not get_ui_automation_case(case_id)]
    if missing:
        return fail(message=f"UI automation case not found: {missing[0]}", code=404)
    details = build_ui_execution_details(case_ids=payload.case_ids, exec_param=payload.exec_param)
    created = exec_crud.create(
        db,
        obj_in=UiTestExecCreate(
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
    return success(data=_exec_to_out(created).model_dump())


@router.get("/execs/{exec_id}")
def read_ui_automation_exec(exec_id: int, db: Session = Depends(get_db)):
    item = exec_crud.get(db, exec_id)
    if not item:
        return fail(message="UI automation execution not found", code=404)
    return success(data=_exec_to_out(item).model_dump())


@router.post("/execs/{exec_id}/copy")
def copy_ui_automation_exec(exec_id: int, db: Session = Depends(get_db)):
    item = exec_crud.get(db, exec_id)
    if not item:
        return fail(message="UI automation execution not found", code=404)
    copied = exec_crud.create(
        db,
        obj_in=UiTestExecCreate(
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
    return success(data=_exec_to_out(copied).model_dump())


@router.delete("/execs/{exec_id}")
def delete_ui_automation_exec(exec_id: int, db: Session = Depends(get_db)):
    item = exec_crud.get(db, exec_id)
    if not item:
        return fail(message="UI automation execution not found", code=404)
    removed = exec_crud.remove(db, id=exec_id)
    return success(data=_exec_to_out(removed).model_dump())

