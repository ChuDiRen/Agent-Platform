"""add_api_test_cases_exec

Revision ID: a7d9c3e4f6b2
Revises: f5c8a4d9e2b1
Create Date: 2026-06-06 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a7d9c3e4f6b2"
down_revision: Union[str, None] = "f5c8a4d9e2b1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "api_test_cases_exec",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("exec_type", sa.String(length=255), nullable=False),
        sa.Column("case_ids", sa.Text(), nullable=False),
        sa.Column("details", sa.Text(), nullable=True),
        sa.Column("desc", sa.String(length=1024), nullable=True),
        sa.Column("exec_param", sa.Text(), nullable=True),
        sa.Column("exec_status", sa.String(length=255), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=True,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_api_test_cases_exec_id"), "api_test_cases_exec", ["id"], unique=False)
    op.create_index(op.f("ix_api_test_cases_exec_project_id"), "api_test_cases_exec", ["project_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_api_test_cases_exec_project_id"), table_name="api_test_cases_exec")
    op.drop_index(op.f("ix_api_test_cases_exec_id"), table_name="api_test_cases_exec")
    op.drop_table("api_test_cases_exec")
