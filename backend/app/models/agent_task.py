from __future__ import annotations

from datetime import datetime
from enum import Enum

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.types import JSON

from app.db.base_class import Base


class AgentTaskStatus(str, Enum):
    CREATED = "created"
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AgentTask(Base):
    __tablename__ = "agent_tasks"

    id = Column(Integer, primary_key=True, index=True)
    agent_key = Column(String(100), nullable=False, index=True)
    project_id = Column(Integer, nullable=True, index=True)
    user_id = Column(Integer, nullable=True, index=True)
    status = Column(String(20), nullable=False, default=AgentTaskStatus.CREATED.value, index=True)
    priority = Column(Integer, nullable=False, default=0)
    input_payload = Column(JSON, nullable=False, default=dict)
    result_payload = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, nullable=False, default=0)
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class AgentTaskEvent(Base):
    __tablename__ = "agent_task_events"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("agent_tasks.id"), nullable=False, index=True)
    event_type = Column(String(50), nullable=False, default="info")
    message = Column(Text, nullable=False)
    progress = Column(Integer, nullable=True)
    payload = Column(JSON, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class AgentArtifact(Base):
    __tablename__ = "agent_artifacts"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("agent_tasks.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    artifact_type = Column(String(50), nullable=False)
    storage_path = Column(String(1024), nullable=False)
    mime_type = Column(String(255), nullable=True)
    size_bytes = Column(Integer, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
