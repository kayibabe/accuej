"""Add provider and market mapping provenance to immutable odds captures.

Revision ID: d1b7c4e6a2f8
Revises: b208d5e9f3a2, c3f8a1d9e2b7
"""

from alembic import op
import sqlalchemy as sa


revision = "d1b7c4e6a2f8"
down_revision = ("b208d5e9f3a2", "c3f8a1d9e2b7")
branch_labels = None
depends_on = None


COLUMNS = (
    ("source_provider", sa.String(50)),
    ("provider_market_id", sa.Integer()),
    ("provider_selection_raw", sa.String(200)),
    ("provider_line_raw", sa.String(50)),
    ("market_catalog_version", sa.String(40)),
    ("market_contract_version", sa.String(40)),
    ("market_mapping_version", sa.String(40)),
)


def _existing_columns() -> set[str]:
    inspector = sa.inspect(op.get_bind())
    if "odds_snapshots" not in inspector.get_table_names():
        return set()
    return {column["name"] for column in inspector.get_columns("odds_snapshots")}


def upgrade():
    # Leave existing normalized-only snapshots NULL; their provider payloads
    # cannot be reconstructed reliably from legacy market and selection keys.
    # The initial migration builds the schema from Base.metadata, so these
    # columns already exist on fresh databases.
    existing = _existing_columns()
    for name, type_ in COLUMNS:
        if name not in existing:
            op.add_column("odds_snapshots", sa.Column(name, type_, nullable=True))


def downgrade():
    existing = _existing_columns()
    for name, _ in reversed(COLUMNS):
        if name in existing:
            op.drop_column("odds_snapshots", name)
