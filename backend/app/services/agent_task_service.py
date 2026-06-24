from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.models.agent_task import AgentArtifact, AgentTask, AgentTaskEvent, AgentTaskStatus


TERMINAL_STATUSES = {
    AgentTaskStatus.SUCCEEDED.value,
    AgentTaskStatus.FAILED.value,
    AgentTaskStatus.CANCELLED.value,
}


class AgentTaskService:
    def __init__(self, db: Session):
        self.db = db

    def create_task(
        self,
        *,
        agent_key: str,
        input_payload: dict[str, Any] | None = None,
        project_id: int | None = None,
        user_id: int | None = None,
        priority: int = 0,
    ) -> AgentTask:
        task = AgentTask(
            agent_key=agent_key,
            project_id=project_id,
            user_id=user_id,
            priority=priority,
            input_payload=jsonable_encoder(input_payload or {}),
            status=AgentTaskStatus.CREATED.value,
        )
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def get_task(self, task_id: int) -> AgentTask | None:
        return self.db.get(AgentTask, task_id)

    def list_tasks(
        self,
        *,
        agent_key: str | None = None,
        status: str | None = None,
        project_id: int | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[AgentTask], int]:
        query = self.db.query(AgentTask)
        if agent_key:
            query = query.filter(AgentTask.agent_key == agent_key)
        if status:
            query = query.filter(AgentTask.status == status)
        if project_id is not None:
            query = query.filter(AgentTask.project_id == project_id)
        total = query.count()
        items = query.order_by(AgentTask.id.desc()).offset(skip).limit(limit).all()
        return items, total

    def queue_task(self, task: AgentTask) -> AgentTask:
        task.status = AgentTaskStatus.QUEUED.value
        task.error_message = None
        self.db.add(task)
        self.emit_event(task.id, event_type="queued", message="任务已入队", progress=0, commit=False)
        self.db.commit()
        self.db.refresh(task)
        return task

    def start_task(self, task: AgentTask) -> AgentTask:
        task.status = AgentTaskStatus.RUNNING.value
        task.started_at = datetime.utcnow()
        task.finished_at = None
        task.error_message = None
        self.db.add(task)
        self.emit_event(task.id, event_type="running", message="任务开始执行", progress=5, commit=False)
        self.db.commit()
        self.db.refresh(task)
        return task

    def succeed_task(self, task: AgentTask, result_payload: dict[str, Any]) -> AgentTask:
        task.status = AgentTaskStatus.SUCCEEDED.value
        task.result_payload = jsonable_encoder(result_payload)
        task.finished_at = datetime.utcnow()
        self.db.add(task)
        self.emit_event(task.id, event_type="succeeded", message="任务执行成功", progress=100, commit=False)
        self.db.commit()
        self.db.refresh(task)
        return task

    def fail_task(self, task: AgentTask, error_message: str) -> AgentTask:
        task.status = AgentTaskStatus.FAILED.value
        task.error_message = error_message
        task.finished_at = datetime.utcnow()
        self.db.add(task)
        self.emit_event(
            task.id,
            event_type="failed",
            message=error_message,
            progress=None,
            commit=False,
        )
        self.db.commit()
        self.db.refresh(task)
        return task

    def cancel_task(self, task: AgentTask) -> AgentTask:
        task.status = AgentTaskStatus.CANCELLED.value
        task.finished_at = datetime.utcnow()
        self.db.add(task)
        self.emit_event(task.id, event_type="cancelled", message="任务已取消", commit=False)
        self.db.commit()
        self.db.refresh(task)
        return task

    def retry_task(self, task: AgentTask) -> AgentTask:
        task.retry_count += 1
        task.result_payload = None
        task.error_message = None
        task.started_at = None
        task.finished_at = None
        self.db.add(task)
        self.queue_task(task)
        return task

    def emit_event(
        self,
        task_id: int,
        *,
        event_type: str = "info",
        message: str,
        progress: int | None = None,
        payload: dict[str, Any] | None = None,
        commit: bool = True,
    ) -> AgentTaskEvent:
        event = AgentTaskEvent(
            task_id=task_id,
            event_type=event_type,
            message=message,
            progress=progress,
            payload=jsonable_encoder(payload) if payload is not None else None,
        )
        self.db.add(event)
        if commit:
            self.db.commit()
            self.db.refresh(event)
        return event

    def add_artifact(
        self,
        task_id: int,
        *,
        name: str,
        artifact_type: str,
        storage_path: str,
        mime_type: str | None = None,
        size_bytes: int | None = None,
    ) -> AgentArtifact:
        artifact = AgentArtifact(
            task_id=task_id,
            name=name,
            artifact_type=artifact_type,
            storage_path=storage_path,
            mime_type=mime_type,
            size_bytes=size_bytes,
        )
        self.db.add(artifact)
        self.db.commit()
        self.db.refresh(artifact)
        return artifact

    def list_events(self, task_id: int) -> list[AgentTaskEvent]:
        return (
            self.db.query(AgentTaskEvent)
            .filter(AgentTaskEvent.task_id == task_id)
            .order_by(AgentTaskEvent.id.asc())
            .all()
        )

    def list_artifacts(self, task_id: int) -> list[AgentArtifact]:
        return (
            self.db.query(AgentArtifact)
            .filter(AgentArtifact.task_id == task_id)
            .order_by(AgentArtifact.id.asc())
            .all()
        )
