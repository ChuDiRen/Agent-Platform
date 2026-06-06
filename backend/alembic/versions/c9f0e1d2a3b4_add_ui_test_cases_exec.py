"""add_ui_test_cases_exec

Revision ID: c9f0e1d2a3b4
Revises: b8e1d4c2a9f0
Create Date: 2026-06-06 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c9f0e1d2a3b4"
down_revision: Union[str, None] = "b8e1d4c2a9f0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "ui_test_cases_exec",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("exec_type", sa.String(length=255), nullable=False),
        sa.Column("case_ids", sa.Text(), nullable=False),
        sa.Column("details", sa.Text(), nullable=True),
        sa.Column("desc", sa.String(length=1024), nullable=True),
        sa.Column("exec_param", sa.Text(), nullable=True),
        sa.Column("exec_status", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_ui_test_cases_exec_id"), "ui_test_cases_exec", ["id"], unique=False)
    op.create_index(op.f("ix_ui_test_cases_exec_project_id"), "ui_test_cases_exec", ["project_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_ui_test_cases_exec_project_id"), table_name="ui_test_cases_exec")
    op.drop_index(op.f("ix_ui_test_cases_exec_id"), table_name="ui_test_cases_exec")
    op.drop_table("ui_test_cases_exec")
