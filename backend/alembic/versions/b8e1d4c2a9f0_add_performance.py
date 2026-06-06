"""add_performance

Revision ID: b8e1d4c2a9f0
Revises: a7d9c3e4f6b2
Create Date: 2026-06-06 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b8e1d4c2a9f0"
down_revision: Union[str, None] = "a7d9c3e4f6b2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "performance",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=True),
        sa.Column("project_id", sa.Integer(), nullable=True),
        sa.Column("configs", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_performance_id"), "performance", ["id"], unique=False)
    op.create_index(op.f("ix_performance_project_id"), "performance", ["project_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_performance_project_id"), table_name="performance")
    op.drop_index(op.f("ix_performance_id"), table_name="performance")
    op.drop_table("performance")
