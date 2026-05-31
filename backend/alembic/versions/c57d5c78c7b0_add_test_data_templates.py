"""add_test_data_templates

Revision ID: c57d5c78c7b0
Revises: afc3a55ec7de
Create Date: 2026-05-31 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c57d5c78c7b0"
down_revision: Union[str, None] = "afc3a55ec7de"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "test_data_templates",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("fields", sa.Text(), nullable=False),
        sa.Column("hint", sa.String(length=1000), nullable=True),
        sa.Column("count", sa.Integer(), nullable=True),
        sa.Column("format", sa.String(length=45), nullable=True),
        sa.Column("lang", sa.String(length=45), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=True,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_test_data_templates_id"), "test_data_templates", ["id"], unique=False)
    op.create_index(
        op.f("ix_test_data_templates_project_id"),
        "test_data_templates",
        ["project_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_test_data_templates_project_id"), table_name="test_data_templates")
    op.drop_index(op.f("ix_test_data_templates_id"), table_name="test_data_templates")
    op.drop_table("test_data_templates")
