"""add_agent_tasks

Revision ID: e4a2b7c9d1f0
Revises: c9f0e1d2a3b4
Create Date: 2026-06-24 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "e4a2b7c9d1f0"
down_revision: Union[str, None] = "c9f0e1d2a3b4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "agent_tasks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("agent_key", sa.String(length=100), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=False),
        sa.Column("input_payload", sa.JSON(), nullable=False),
        sa.Column("result_payload", sa.JSON(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("retry_count", sa.Integer(), nullable=False),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("finished_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_agent_tasks_id"), "agent_tasks", ["id"], unique=False)
    op.create_index(op.f("ix_agent_tasks_agent_key"), "agent_tasks", ["agent_key"], unique=False)
    op.create_index(op.f("ix_agent_tasks_project_id"), "agent_tasks", ["project_id"], unique=False)
    op.create_index(op.f("ix_agent_tasks_user_id"), "agent_tasks", ["user_id"], unique=False)
    op.create_index(op.f("ix_agent_tasks_status"), "agent_tasks", ["status"], unique=False)

    op.create_table(
        "agent_task_events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("task_id", sa.Integer(), nullable=False),
        sa.Column("event_type", sa.String(length=50), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("progress", sa.Integer(), nullable=True),
        sa.Column("payload", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["task_id"], ["agent_tasks.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_agent_task_events_id"), "agent_task_events", ["id"], unique=False)
    op.create_index(op.f("ix_agent_task_events_task_id"), "agent_task_events", ["task_id"], unique=False)

    op.create_table(
        "agent_artifacts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("task_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("artifact_type", sa.String(length=50), nullable=False),
        sa.Column("storage_path", sa.String(length=1024), nullable=False),
        sa.Column("mime_type", sa.String(length=255), nullable=True),
        sa.Column("size_bytes", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["task_id"], ["agent_tasks.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_agent_artifacts_id"), "agent_artifacts", ["id"], unique=False)
    op.create_index(op.f("ix_agent_artifacts_task_id"), "agent_artifacts", ["task_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_agent_artifacts_task_id"), table_name="agent_artifacts")
    op.drop_index(op.f("ix_agent_artifacts_id"), table_name="agent_artifacts")
    op.drop_table("agent_artifacts")
    op.drop_index(op.f("ix_agent_task_events_task_id"), table_name="agent_task_events")
    op.drop_index(op.f("ix_agent_task_events_id"), table_name="agent_task_events")
    op.drop_table("agent_task_events")
    op.drop_index(op.f("ix_agent_tasks_status"), table_name="agent_tasks")
    op.drop_index(op.f("ix_agent_tasks_user_id"), table_name="agent_tasks")
    op.drop_index(op.f("ix_agent_tasks_project_id"), table_name="agent_tasks")
    op.drop_index(op.f("ix_agent_tasks_agent_key"), table_name="agent_tasks")
    op.drop_index(op.f("ix_agent_tasks_id"), table_name="agent_tasks")
    op.drop_table("agent_tasks")
