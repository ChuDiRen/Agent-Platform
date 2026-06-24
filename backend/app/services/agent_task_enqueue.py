from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.services.agent_task_service import AgentTaskService
from app.workers.tasks import run_agent_task


def create_and_enqueue_agent_task(
    db: Session,
    *,
    agent_key: str,
    input_payload: dict[str, Any],
    project_id: int | None = None,
    user_id: int | None = None,
    priority: int = 0,
):
    service = AgentTaskService(db)
    task = service.create_task(
        agent_key=agent_key,
        input_payload=input_payload,
        project_id=project_id,
        user_id=user_id,
        priority=priority,
    )
    try:
        service.queue_task(task)
        run_agent_task.delay(task.id)
    except Exception as exc:
        service.fail_task(task, f"任务入队失败: {exc}")
    return task
