"""add_test_cases

Revision ID: f5c8a4d9e2b1
Revises: 9b77ef1e1f30
Create Date: 2026-06-06 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f5c8a4d9e2b1"
down_revision: Union[str, None] = "9b77ef1e1f30"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "test_cases",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=True),
        sa.Column("module_id", sa.Integer(), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=True),
        sa.Column("precondition", sa.String(length=1024), nullable=True),
        sa.Column("expected", sa.String(length=1024), nullable=True),
        sa.Column("steps", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=True,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_test_cases_id"), "test_cases", ["id"], unique=False)
    op.create_index(op.f("ix_test_cases_project_id"), "test_cases", ["project_id"], unique=False)
    op.create_index(op.f("ix_test_cases_module_id"), "test_cases", ["module_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_test_cases_module_id"), table_name="test_cases")
    op.drop_index(op.f("ix_test_cases_project_id"), table_name="test_cases")
    op.drop_index(op.f("ix_test_cases_id"), table_name="test_cases")
    op.drop_table("test_cases")
