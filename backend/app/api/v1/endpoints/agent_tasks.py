from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.response import fail, paginated, success
from app.models.agent_task import AgentTaskStatus
from app.schemas.agent_task import AgentArtifactOut, AgentTaskCreate, AgentTaskEventOut, AgentTaskOut
from app.services.agent_task_enqueue import create_and_enqueue_agent_task
from app.services.agent_task_service import AgentTaskService
from app.workers.tasks import run_agent_task

router = APIRouter()


def _task_data(task):
    return AgentTaskOut.model_validate(task).model_dump(mode="json")


@router.post("/")
def create_agent_task(payload: AgentTaskCreate, db: Session = Depends(get_db)):
    task = create_and_enqueue_agent_task(
        db,
        agent_key=payload.agent_key,
        project_id=payload.project_id,
        user_id=payload.user_id,
        priority=payload.priority,
        input_payload=payload.input_payload,
    )
    return success(data=_task_data(task))


@router.get("/")
def read_agent_tasks(
    agent_key: str | None = None,
    status: str | None = None,
    project_id: int | None = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    service = AgentTaskService(db)
    items, total = service.list_tasks(
        agent_key=agent_key,
        status=status,
        project_id=project_id,
        skip=skip,
        limit=limit,
    )
    page = skip // limit + 1 if limit > 0 else 1
    return paginated(
        items=[_task_data(item) for item in items],
        total=total,
        page=page,
        page_size=limit,
    )


@router.get("/{task_id}")
def read_agent_task(task_id: int, db: Session = Depends(get_db)):
    task = AgentTaskService(db).get_task(task_id)
    if not task:
        return fail(message="Agent task not found", code=404)
    return success(data=_task_data(task))


@router.get("/{task_id}/events")
def read_agent_task_events(task_id: int, db: Session = Depends(get_db)):
    service = AgentTaskService(db)
    if not service.get_task(task_id):
        return fail(message="Agent task not found", code=404)
    events = [AgentTaskEventOut.model_validate(item).model_dump(mode="json") for item in service.list_events(task_id)]
    return success(data=events)


@router.get("/{task_id}/artifacts")
def read_agent_task_artifacts(task_id: int, db: Session = Depends(get_db)):
    service = AgentTaskService(db)
    if not service.get_task(task_id):
        return fail(message="Agent task not found", code=404)
    artifacts = [
        AgentArtifactOut.model_validate(item).model_dump(mode="json")
        for item in service.list_artifacts(task_id)
    ]
    return success(data=artifacts)


@router.post("/{task_id}/cancel")
def cancel_agent_task(task_id: int, db: Session = Depends(get_db)):
    service = AgentTaskService(db)
    task = service.get_task(task_id)
    if not task:
        return fail(message="Agent task not found", code=404)
    if task.status in {
        AgentTaskStatus.SUCCEEDED.value,
        AgentTaskStatus.FAILED.value,
        AgentTaskStatus.CANCELLED.value,
    }:
        return fail(message="Only active tasks can be cancelled", code=400)
    service.cancel_task(task)
    return success(data=_task_data(task))


@router.post("/{task_id}/retry")
def retry_agent_task(task_id: int, db: Session = Depends(get_db)):
    service = AgentTaskService(db)
    task = service.get_task(task_id)
    if not task:
        return fail(message="Agent task not found", code=404)
    if task.status != AgentTaskStatus.FAILED.value:
        return fail(message="Only failed tasks can be retried", code=400)
    service.retry_task(task)
    run_agent_task.delay(task.id)
    return success(data=_task_data(task))
