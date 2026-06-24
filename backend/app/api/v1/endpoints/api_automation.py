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
from app.agents.api_automation.service import (
    get_api_automation_case,
    list_api_automation_cases,
)
from app.core.response import success, fail, paginated
from app.schemas.agent_task import AgentTaskOut
from app.services.agent_task_enqueue import create_and_enqueue_agent_task

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


@router.get("/cases")
def read_api_automation_cases(
    project_id: int | None = None,
    name: str | None = None,
    priority: int | None = None,
    module_id: int | None = None,
    exec_type: str | None = None,
):
    items = list_api_automation_cases(
        project_id=project_id,
        name=name,
        priority=priority,
        module_id=module_id,
        exec_type=exec_type,
    )
    return success(data=[ApiAutomationCase.model_validate(i).model_dump() for i in items])


@router.get("/cases/{case_id}")
def read_api_automation_case(case_id: int):
    item = get_api_automation_case(case_id)
    if not item:
        return fail(message="API automation case not found", code=404)
    return success(data=ApiAutomationCase.model_validate(item).model_dump())


@router.get("/execs")
def read_api_automation_execs(
    project_id: int | None = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    items = exec_crud.get_multi_by_project(db, project_id=project_id, skip=skip, limit=limit)
    data = [_exec_to_out(i).model_dump() for i in items]
    page = skip // limit + 1 if limit > 0 else 1
    return paginated(items=data, total=len(data), page=page, page_size=limit)


@router.post("/execs")
def create_api_automation_exec(payload: ApiTestExecRunRequest, db: Session = Depends(get_db)):
    missing = [case_id for case_id in payload.case_ids if not get_api_automation_case(case_id)]
    if missing:
        return fail(message=f"API automation case not found: {missing[0]}", code=404)
    task = create_and_enqueue_agent_task(
        db,
        agent_key="api_automation",
        project_id=payload.project_id,
        input_payload=payload.model_dump(),
    )
    return success(data=AgentTaskOut.model_validate(task).model_dump(mode="json"))


@router.get("/execs/{exec_id}")
def read_api_automation_exec(exec_id: int, db: Session = Depends(get_db)):
    item = exec_crud.get(db, exec_id)
    if not item:
        return fail(message="API automation execution not found", code=404)
    return success(data=_exec_to_out(item).model_dump())


@router.post("/execs/{exec_id}/copy")
def copy_api_automation_exec(exec_id: int, db: Session = Depends(get_db)):
    item = exec_crud.get(db, exec_id)
    if not item:
        return fail(message="API automation execution not found", code=404)
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
    return success(data=_exec_to_out(copied).model_dump())


@router.delete("/execs/{exec_id}")
def delete_api_automation_exec(exec_id: int, db: Session = Depends(get_db)):
    item = exec_crud.get(db, exec_id)
    if not item:
        return fail(message="API automation execution not found", code=404)
    removed = exec_crud.remove(db, id=exec_id)
    return success(data=_exec_to_out(removed).model_dump())

