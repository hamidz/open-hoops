"""create jobs table

Revision ID: 0001
Revises:
Create Date: 2026-05-03

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "jobs",
        sa.Column("job_id", sa.Text(), primary_key=True),
        sa.Column("schema_version", sa.String(10), nullable=False, server_default="1.0"),
        sa.Column("status", sa.String(30), nullable=False),
        sa.Column("progress_pct", sa.SmallInteger(), nullable=False, server_default="0"),
        sa.Column("label", sa.Text(), nullable=True),
        sa.Column("sport", sa.String(30), nullable=False, server_default="basketball"),
        sa.Column("original_filename", sa.Text(), nullable=False),
        sa.Column("file_size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("video_url", sa.Text(), nullable=False),
        sa.Column("frame_zero_url", sa.Text(), nullable=True),
        sa.Column(
            "calibration_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column("telemetry_url", sa.Text(), nullable=True),
        sa.Column("analytics_summary_url", sa.Text(), nullable=True),
        sa.Column("report_url", sa.Text(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "jobs_created_at_idx",
        "jobs",
        [sa.text("created_at DESC")],
    )


def downgrade() -> None:
    op.drop_index("jobs_created_at_idx", table_name="jobs")
    op.drop_table("jobs")
