"""Add optional account ownership to journal entries.

Revision ID: 0100_account_owned_bet_journal
Revises: ff58a0d2c3e1
"""

from alembic import op
import sqlalchemy as sa

from migrations.guards import (
    add_column_if_missing,
    constraint_names,
    create_index_if_missing,
    has_column,
    index_names,
)


revision = "0100_account_owned_bet_journal"
down_revision = "d2e4a6c8b0f1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    add_column_if_missing("bets", sa.Column("user_id", sa.Integer(), nullable=True))
    if "fk_bets_user_id_users" not in constraint_names("bets"):
        op.create_foreign_key(
            "fk_bets_user_id_users",
            "bets",
            "users",
            ["user_id"],
            ["id"],
            ondelete="SET NULL",
        )
    create_index_if_missing("ix_bets_user_id", "bets", ["user_id"])


def downgrade() -> None:
    if "ix_bets_user_id" in index_names("bets"):
        op.drop_index("ix_bets_user_id", table_name="bets")
    if "fk_bets_user_id_users" in constraint_names("bets"):
        op.drop_constraint("fk_bets_user_id_users", "bets", type_="foreignkey")
    if has_column("bets", "user_id"):
        op.drop_column("bets", "user_id")
