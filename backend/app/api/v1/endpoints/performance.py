import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.crud.performance import performance as performance_crud
from app.schemas.performance import (
    PerformanceAnalyzeRequest,
    PerformanceAnalyzeResponse,
    PerformanceConfigs,
    PerformanceCreate,
    PerformanceOut,
)
from app.agents.performance.service import analyze_performance
from app.core.response import success, fail, paginated

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
    metrics, analysis, elapsed_ms = analyze_performance(payload)
    record = performance_crud.create(
        db,
        obj_in=PerformanceCreate(
            project_id=payload.project_id,
            configs=PerformanceConfigs(
                name=payload.name,
                source="ai-analysis",
                scenario=payload.scenario,
                raw_text=payload.raw_text,
                metrics=metrics,
                analysis=analysis,
            ),
        ),
    )
    result = PerformanceAnalyzeResponse(record=_performance_to_out(record), analysis=analysis, elapsed_ms=elapsed_ms)
    return success(data=result.model_dump())


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

