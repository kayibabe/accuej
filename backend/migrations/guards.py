"""Idempotent DDL helpers for migrations.

The initial revision (``3d52766f0fb9``) builds the schema from
``Base.metadata``, which means a fresh database already contains every table,
column, index and constraint declared by the current models. Migrations that
follow it would otherwise fail with "already exists" errors on a fresh
install. These helpers make those migrations safe on both fresh databases and
databases upgraded from older revisions.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op


def _inspector() -> sa.Inspector:
    return sa.inspect(op.get_bind())


def has_table(table: str) -> bool:
    return table in _inspector().get_table_names()


def columns(table: str) -> set[str]:
    inspector = _inspector()
    if table not in inspector.get_table_names():
        return set()
    return {column["name"] for column in inspector.get_columns(table)}


def has_column(table: str, column: str) -> bool:
    return column in columns(table)


def add_column_if_missing(table: str, column: sa.Column) -> None:
    if has_table(table) and not has_column(table, column.name):
        op.add_column(table, column)


def create_table_if_missing(table: str, *columns: sa.Column, **kwargs) -> None:
    if not has_table(table):
        op.create_table(table, *columns, **kwargs)


def index_names(table: str) -> set[str]:
    inspector = _inspector()
    if table not in inspector.get_table_names():
        return set()
    return {index["name"] for index in inspector.get_indexes(table)}


def create_index_if_missing(name: str, table: str, columns: list[str], **kwargs) -> None:
    if has_table(table) and name not in index_names(table):
        op.create_index(name, table, columns, **kwargs)


def constraint_names(table: str) -> set[str]:
    inspector = _inspector()
    if table not in inspector.get_table_names():
        return set()
    names = {item["name"] for item in inspector.get_unique_constraints(table)}
    names.update(item["name"] for item in inspector.get_foreign_keys(table))
    names.update(item["name"] for item in inspector.get_check_constraints(table))
    return names


def create_unique_constraint_if_missing(name: str, table: str, columns: list[str]) -> None:
    if has_table(table) and name not in constraint_names(table):
        op.create_unique_constraint(name, table, columns)
