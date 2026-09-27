"""add timestamp defaults

Revision ID: 50eabb5914f8
Revises: 1317f1202b32
Create Date: 2026-09-27 11:29:00.498926

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '50eabb5914f8'
down_revision: Union[str, Sequence[str], None] = '1317f1202b32'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "candidates",
        "created_at",
        server_default=sa.text("now()"),
    )
    op.alter_column(
        "candidates",
        "updated_at",
        server_default=sa.text("now()"),
    )

    op.alter_column(
        "resumes",
        "created_at",
        server_default=sa.text("now()"),
    )
    op.alter_column(
        "resumes",
        "updated_at",
        server_default=sa.text("now()"),
    )

    op.alter_column(
        "screenings",
        "created_at",
        server_default=sa.text("now()"),
    )
    op.alter_column(
        "screenings",
        "updated_at",
        server_default=sa.text("now()"),
    )

    op.alter_column(
        "candidate_processing",
        "created_at",
        server_default=sa.text("now()"),
    )
    op.alter_column(
        "candidate_processing",
        "updated_at",
        server_default=sa.text("now()"),
    )

    op.alter_column(
        "evaluations",
        "created_at",
        server_default=sa.text("now()"),
    )
    op.alter_column(
        "evaluations",
        "updated_at",
        server_default=sa.text("now()"),
    )

    op.alter_column(
        "screening_results",
        "created_at",
        server_default=sa.text("now()"),
    )
    op.alter_column(
        "screening_results",
        "updated_at",
        server_default=sa.text("now()"),
    )

    op.alter_column(
        "domains",
        "created_at",
        server_default=sa.text("now()"),
    )
    op.alter_column(
        "domains",
        "updated_at",
        server_default=sa.text("now()"),
    )

    op.alter_column(
        "hackathons",
        "created_at",
        server_default=sa.text("now()"),
    )
    op.alter_column(
        "hackathons",
        "updated_at",
        server_default=sa.text("now()"),
    )

    op.alter_column(
        "imports",
        "created_at",
        server_default=sa.text("now()"),
    )

    op.alter_column(
        "manual_overrides",
        "created_at",
        server_default=sa.text("now()"),
    )
    op.alter_column(
        "manual_overrides",
        "updated_at",
        server_default=sa.text("now()"),
    )

    op.alter_column(
        "processing_failures",
        "created_at",
        server_default=sa.text("now()"),
    )
    op.alter_column(
        "processing_failures",
        "updated_at",
        server_default=sa.text("now()"),
    )

    op.alter_column(
        "prompts",
        "created_at",
        server_default=sa.text("now()"),
    )
    op.alter_column(
        "prompts",
        "updated_at",
        server_default=sa.text("now()"),
    )

    op.alter_column(
        "rubrics",
        "created_at",
        server_default=sa.text("now()"),
    )
    op.alter_column(
        "rubrics",
        "updated_at",
        server_default=sa.text("now()"),
    )

    op.alter_column(
        "teams",
        "created_at",
        server_default=sa.text("now()"),
    )
    op.alter_column(
        "teams",
        "updated_at",
        server_default=sa.text("now()"),
    )

    op.alter_column(
        "users",
        "created_at",
        server_default=sa.text("now()"),
    )
    op.alter_column(
        "users",
        "updated_at",
        server_default=sa.text("now()"),
    )


def downgrade() -> None:
    op.alter_column("candidates", "created_at", server_default=None)
    op.alter_column("candidates", "updated_at", server_default=None)

    op.alter_column("resumes", "created_at", server_default=None)
    op.alter_column("resumes", "updated_at", server_default=None)

    op.alter_column("screenings", "created_at", server_default=None)
    op.alter_column("screenings", "updated_at", server_default=None)

    op.alter_column("candidate_processing", "created_at", server_default=None)
    op.alter_column("candidate_processing", "updated_at", server_default=None)

    op.alter_column("evaluations", "created_at", server_default=None)
    op.alter_column("evaluations", "updated_at", server_default=None)

    op.alter_column("screening_results", "created_at", server_default=None)
    op.alter_column("screening_results", "updated_at", server_default=None)

    op.alter_column("domains", "created_at", server_default=None)
    op.alter_column("domains", "updated_at", server_default=None)

    op.alter_column("hackathons", "created_at", server_default=None)
    op.alter_column("hackathons", "updated_at", server_default=None)

    op.alter_column("imports", "created_at", server_default=None)

    op.alter_column("manual_overrides", "created_at", server_default=None)
    op.alter_column("manual_overrides", "updated_at", server_default=None)

    op.alter_column("processing_failures", "created_at", server_default=None)
    op.alter_column("processing_failures", "updated_at", server_default=None)

    op.alter_column("prompts", "created_at", server_default=None)
    op.alter_column("prompts", "updated_at", server_default=None)

    op.alter_column("rubrics", "created_at", server_default=None)
    op.alter_column("rubrics", "updated_at", server_default=None)

    op.alter_column("teams", "created_at", server_default=None)
    op.alter_column("teams", "updated_at", server_default=None)

    op.alter_column("users", "created_at", server_default=None)
    op.alter_column("users", "updated_at", server_default=None)