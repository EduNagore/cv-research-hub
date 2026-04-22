"""Add ingestion status table.

Revision ID: 002_add_ingestion_statuses
Revises: 001_initial
Create Date: 2026-04-22
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "002_add_ingestion_statuses"
down_revision = "001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "ingestion_statuses",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("scope_key", sa.String(length=255), nullable=False),
        sa.Column("source", sa.String(length=100), nullable=False),
        sa.Column("category_slug", sa.String(length=100), nullable=True),
        sa.Column("last_started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_status", sa.String(length=32), nullable=False),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("last_result", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_ingestion_statuses_category_slug"), "ingestion_statuses", ["category_slug"], unique=False)
    op.create_index(op.f("ix_ingestion_statuses_id"), "ingestion_statuses", ["id"], unique=False)
    op.create_index(op.f("ix_ingestion_statuses_scope_key"), "ingestion_statuses", ["scope_key"], unique=True)
    op.create_index(op.f("ix_ingestion_statuses_source"), "ingestion_statuses", ["source"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_ingestion_statuses_source"), table_name="ingestion_statuses")
    op.drop_index(op.f("ix_ingestion_statuses_scope_key"), table_name="ingestion_statuses")
    op.drop_index(op.f("ix_ingestion_statuses_id"), table_name="ingestion_statuses")
    op.drop_index(op.f("ix_ingestion_statuses_category_slug"), table_name="ingestion_statuses")
    op.drop_table("ingestion_statuses")
