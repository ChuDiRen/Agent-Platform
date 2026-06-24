from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.models.agent_task import AgentTaskStatus


class AgentTaskCreate(BaseModel):
    agent_key: str = Field(min_length=1, max_length=100)
    project_id: int | None = None
    user_id: int | None = None
    priority: int = 0
    input_payload: dict[str, Any] = Field(default_factory=dict)


class AgentTaskOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    agent_key: str
    project_id: int | None = None
    user_id: int | None = None
    status: AgentTaskStatus
    priority: int
    input_payload: dict[str, Any]
    result_payload: dict[str, Any] | None = None
    error_message: str | None = None
    retry_count: int
    started_at: datetime | None = None
    finished_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class AgentTaskEventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    task_id: int
    event_type: str
    message: str
    progress: int | None = None
    payload: dict[str, Any] | None = None
    created_at: datetime


class AgentArtifactOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    task_id: int
    name: str
    artifact_type: str
    storage_path: str
    mime_type: str | None = None
    size_bytes: int | None = None
    created_at: datetime
