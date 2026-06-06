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
from app.services.performance_agent import analyze_performance

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


@router.get("/", response_model=list[PerformanceOut])
def read_performance_records(
    project_id: int | None = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    return [
        _performance_to_out(item)
        for item in performance_crud.get_multi_by_project(db, project_id=project_id, skip=skip, limit=limit)
    ]


@router.post("/analyze", response_model=PerformanceAnalyzeResponse)
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
    return PerformanceAnalyzeResponse(record=_performance_to_out(record), analysis=analysis, elapsed_ms=elapsed_ms)


@router.get("/{record_id}", response_model=PerformanceOut)
def read_performance_record(record_id: int, db: Session = Depends(get_db)):
    item = performance_crud.get(db, record_id)
    if not item:
        raise HTTPException(status_code=404, detail="Performance record not found")
    return _performance_to_out(item)


@router.delete("/{record_id}", response_model=PerformanceOut)
def delete_performance_record(record_id: int, db: Session = Depends(get_db)):
    item = performance_crud.get(db, record_id)
    if not item:
        raise HTTPException(status_code=404, detail="Performance record not found")
    removed = performance_crud.remove(db, id=record_id)
    return _performance_to_out(removed)
