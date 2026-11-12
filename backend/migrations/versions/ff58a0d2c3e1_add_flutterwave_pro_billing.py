"""add Flutterwave Pro billing records

Revision ID: ff58a0d2c3e1
Revises: fe46b8d3c012

The initial migration builds the schema from ``Base.metadata``, so a fresh
database already has ``users.plan_source`` and the billing tables. Every
operation here is guarded so the migration is safe on both fresh and
pre-existing databases.
"""

from alembic import op
import sqlalchemy as sa


revision = "ff58a0d2c3e1"
down_revision = "fe46b8d3c012"
branch_labels = None
depends_on = None


def _inspector():
    return sa.inspect(op.get_bind())


def upgrade() -> None:
    inspector = _inspector()
    tables = set(inspector.get_table_names())

    if "users" in tables:
        columns = {column["name"] for column in inspector.get_columns("users")}
        if "plan_source" not in columns:
            op.add_column(
                "users",
                sa.Column("plan_source", sa.String(length=32), nullable=False, server_default="manual"),
            )

    if "billing_orders" not in tables:
        op.create_table(
            "billing_orders",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
            sa.Column("tx_ref", sa.String(length=64), nullable=False, unique=True),
            sa.Column("amount", sa.Numeric(12, 2), nullable=False),
            sa.Column("currency", sa.String(length=3), nullable=False, server_default="MWK"),
            sa.Column("status", sa.String(length=24), nullable=False, server_default="initiating"),
            sa.Column("checkout_url", sa.Text()),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.Column("completed_at", sa.DateTime(timezone=True)),
        )
        op.create_index("ix_billing_orders_user_id", "billing_orders", ["user_id"])

    if "billing_payments" not in tables:
        op.create_table(
            "billing_payments",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
            sa.Column("order_id", sa.Integer(), sa.ForeignKey("billing_orders.id", ondelete="SET NULL")),
            sa.Column("provider_transaction_id", sa.String(length=80), nullable=False, unique=True),
            sa.Column("tx_ref", sa.String(length=64), nullable=False),
            sa.Column("amount", sa.Numeric(12, 2), nullable=False),
            sa.Column("currency", sa.String(length=3), nullable=False),
            sa.Column("payment_type", sa.String(length=32)),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        )
        op.create_index("ix_billing_payments_user_id", "billing_payments", ["user_id"])
        op.create_index("ix_billing_payments_order_id", "billing_payments", ["order_id"])
        op.create_index("ix_billing_payments_tx_ref", "billing_payments", ["tx_ref"])

    if "billing_subscriptions" not in tables:
        op.create_table(
            "billing_subscriptions",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
            sa.Column("provider", sa.String(length=32), nullable=False, server_default="flutterwave"),
            sa.Column("provider_plan_id", sa.String(length=64), nullable=False),
            sa.Column("provider_customer_id", sa.String(length=80)),
            sa.Column("status", sa.String(length=24), nullable=False, server_default="active"),
            sa.Column("started_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.Column("last_paid_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.Column("cancelled_at", sa.DateTime(timezone=True)),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.UniqueConstraint("user_id", "provider", name="uq_billing_subscription_user_provider"),
        )
        op.create_index("ix_billing_subscriptions_user_id", "billing_subscriptions", ["user_id"])
        op.create_index(
            "ix_billing_subscriptions_provider_customer_id",
            "billing_subscriptions",
            ["provider_customer_id"],
        )


def downgrade() -> None:
    inspector = _inspector()
    tables = set(inspector.get_table_names())

    if "billing_subscriptions" in tables:
        op.drop_table("billing_subscriptions")
    if "billing_payments" in tables:
        op.drop_table("billing_payments")
    if "billing_orders" in tables:
        op.drop_table("billing_orders")
    if "users" in tables:
        columns = {column["name"] for column in inspector.get_columns("users")}
        if "plan_source" in columns:
            op.drop_column("users", "plan_source")
