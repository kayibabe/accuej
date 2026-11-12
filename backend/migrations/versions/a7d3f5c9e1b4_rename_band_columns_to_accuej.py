"""rename model probability band columns to Accuej

Revision ID: a7d3f5c9e1b4
Revises: 0100_account_owned_bet_journal

Databases created before the Accuej rename still carry the old
``qwantej_band`` column. This migration renames it in place so an existing
database can be upgraded without a dump/restore. Fresh databases already
create ``accuej_band`` and this migration is a no-op.
"""

from alembic import op
import sqlalchemy as sa


revision = "a7d3f5c9e1b4"
down_revision = "0100_account_owned_bet_journal"
branch_labels = None
depends_on = None


TABLES = (
    "band_mix_pair_states",
    "band_mix_lifecycle_events",
    "band_mix_daily_picks",
)

OLD_COLUMN = "qwantej_band"
NEW_COLUMN = "accuej_band"


def _rename_column(old_name: str, new_name: str) -> None:
    inspector = sa.inspect(op.get_bind())
    tables = set(inspector.get_table_names())
    for table in TABLES:
        if table not in tables:
            continue
        columns = {column["name"] for column in inspector.get_columns(table)}
        if old_name in columns and new_name not in columns:
            op.alter_column(table, old_name, new_column_name=new_name)


def upgrade() -> None:
    _rename_column(OLD_COLUMN, NEW_COLUMN)


def downgrade() -> None:
    _rename_column(NEW_COLUMN, OLD_COLUMN)
