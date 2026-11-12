"""allow one leg per fixture in each personal accumulator

Revision ID: a197c4e8d2f1
Revises: ff58a0d2c3e1
"""

from alembic import op
import sqlalchemy as sa


revision = "a197c4e8d2f1"
down_revision = "ff58a0d2c3e1"
branch_labels = None
depends_on = None

CONSTRAINT = "uq_custom_accumulator_one_leg_per_match"


def _constraint_exists() -> bool:
    inspector = sa.inspect(op.get_bind())
    if "custom_accumulator_legs" not in inspector.get_table_names():
        return False
    return any(
        constraint["name"] == CONSTRAINT
        for constraint in inspector.get_unique_constraints("custom_accumulator_legs")
    )


def upgrade() -> None:
    # The initial migration builds the schema from Base.metadata, which
    # already declares this constraint on fresh databases.
    if _constraint_exists():
        return
    op.create_unique_constraint(
        CONSTRAINT,
        "custom_accumulator_legs",
        ["accumulator_id", "match_id"],
    )


def downgrade() -> None:
    if not _constraint_exists():
        return
    op.drop_constraint(
        CONSTRAINT,
        "custom_accumulator_legs",
        type_="unique",
    )
