import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.crud.performance import performance as performance_crud
from app.schemas.performance import (
    PerformanceAnalyzeRequest,
    PerformanceConfigs,
    PerformanceCreate,
    PerformanceOut,
)
from app.core.response import success, fail, paginated
from app.schemas.agent_task import AgentTaskOut
from app.services.agent_task_enqueue import create_and_enqueue_agent_task

router = APIRouter()


def _performance_to_out(item) -> PerformanceOut:
    return PerformanceOut.model_validate(
        {
            "id": item.id,
            "project_id": item.project_id,
            "configs": json.loads(item.configs or "{}"),
            "created_at": item.created_at,
            "updated_at": item.updated_at,
        }
    )


@router.get("/")
def read_performance_records(
    project_id: int | None = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    items = performance_crud.get_multi_by_project(db, project_id=project_id, skip=skip, limit=limit)
    data = [_performance_to_out(i).model_dump() for i in items]
    page = skip // limit + 1 if limit > 0 else 1
    return paginated(items=data, total=len(data), page=page, page_size=limit)


@router.post("/analyze")
def analyze_performance_record(payload: PerformanceAnalyzeRequest, db: Session = Depends(get_db)):
    task = create_and_enqueue_agent_task(
        db,
        agent_key="performance",
        project_id=payload.project_id,
        input_payload=payload.model_dump(),
    )
    return success(data=AgentTaskOut.model_validate(task).model_dump(mode="json"))


@router.get("/{record_id}")
def read_performance_record(record_id: int, db: Session = Depends(get_db)):
    item = performance_crud.get(db, record_id)
    if not item:
        return fail(message="Performance record not found", code=404)
    return success(data=_performance_to_out(item).model_dump())


@router.delete("/{record_id}")
def delete_performance_record(record_id: int, db: Session = Depends(get_db)):
    item = performance_crud.get(db, record_id)
    if not item:
        return fail(message="Performance record not found", code=404)
    removed = performance_crud.remove(db, id=record_id)
    return success(data=_performance_to_out(removed).model_dump())

