"""add_api_documents

Revision ID: 9b77ef1e1f30
Revises: d37c2e910f21
Create Date: 2026-06-05 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "9b77ef1e1f30"
down_revision: Union[str, None] = "d37c2e910f21"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "api_documents",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("parent_id", sa.Integer(), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("created_by", sa.String(length=100), nullable=True),
        sa.Column("is_directory", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ai_suggest", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_api_documents_id"), "api_documents", ["id"], unique=False)
    op.create_index(op.f("ix_api_documents_project_id"), "api_documents", ["project_id"], unique=False)
    op.create_index(op.f("ix_api_documents_parent_id"), "api_documents", ["parent_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_api_documents_parent_id"), table_name="api_documents")
    op.drop_index(op.f("ix_api_documents_project_id"), table_name="api_documents")
    op.drop_index(op.f("ix_api_documents_id"), table_name="api_documents")
    op.drop_table("api_documents")
