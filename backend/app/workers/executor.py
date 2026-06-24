from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from app.models.agent_task import AgentTaskStatus
from app.services.agent_task_service import AgentTaskService


@dataclass
class AgentExecutionResult:
    summary: str
    output: dict[str, Any] = field(default_factory=dict)
    artifacts: list[dict[str, Any]] = field(default_factory=list)


class AgentExecutionContext:
    def __init__(self, task_id: int, project_id: int | None, user_id: int | None, service: AgentTaskService):
        self.task_id = task_id
        self.project_id = project_id
        self.user_id = user_id
        self.service = service

    @property
    def db(self):
        return self.service.db

    def emit_event(self, message: str, progress: int | None = None, payload: dict[str, Any] | None = None):
        return self.service.emit_event(
            self.task_id,
            event_type="progress",
            message=message,
            progress=progress,
            payload=payload,
        )

    def add_artifact(
        self,
        name: str,
        artifact_type: str,
        storage_path: str,
        mime_type: str | None = None,
        size_bytes: int | None = None,
    ):
        return self.service.add_artifact(
            self.task_id,
            name=name,
            artifact_type=artifact_type,
            storage_path=storage_path,
            mime_type=mime_type,
            size_bytes=size_bytes,
        )

    def is_cancelled(self) -> bool:
        self.service.db.expire_all()
        task = self.service.get_task(self.task_id)
        return task is not None and task.status == AgentTaskStatus.CANCELLED.value


AgentExecutor = Callable[[dict[str, Any], AgentExecutionContext], AgentExecutionResult]
