"""add users table

Revision ID: 5bdf6af1ef17
Revises: d1cd89e2cc41
Create Date: 2021-11-06 20:19:00.167391

"""

# revision identifiers, used by Alembic.
from sqlalchemy import delete, true

from infrastructure.implementation.database.orm.tables import UserModel

revision = "5bdf6af1ef17"
down_revision = "d1cd89e2cc41"

import sqlalchemy as sa
from alembic import context, op


def upgrade():
    schema_upgrades()
    if context.get_x_argument(as_dictionary=True).get("data", None):
        data_upgrades()


def downgrade():
    if context.get_x_argument(as_dictionary=True).get("data", None):
        data_downgrades()
    schema_downgrades()


def schema_upgrades():
    """schema upgrade migrations go here."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "users",
        sa.Column(
            "id", sa.INTEGER(), sa.Identity(always=True, cache=5), nullable=False
        ),
        sa.Column("first_name", sa.VARCHAR(length=200), nullable=False),
        sa.Column("last_name", sa.VARCHAR(length=200), nullable=False),
        sa.Column("username", sa.VARCHAR(length=200), nullable=False),
        sa.Column(
            "hashed_password",
            sa.VARCHAR(length=200),
            server_default=sa.text("NULL"),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.alter_column(
        "orders",
        "id",
        existing_type=sa.INTEGER(),
        server_default=sa.Identity(always=True, cache=5),
        existing_nullable=False,
    )
    op.alter_column(
        "products",
        "id",
        existing_type=sa.INTEGER(),
        server_default=sa.Identity(always=True, cache=5),
        existing_nullable=False,
    )
    # ### end Alembic commands ###


def schema_downgrades():
    """schema downgrade migrations go here."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "products",
        "id",
        existing_type=sa.INTEGER(),
        server_default=sa.Identity(
            always=True,
            start=1,
            increment=1,
            minvalue=1,
            maxvalue=2147483647,
            cycle=False,
            cache=1,
        ),
        existing_nullable=False,
    )
    op.alter_column(
        "orders",
        "id",
        existing_type=sa.INTEGER(),
        server_default=sa.Identity(
            always=True,
            start=1,
            increment=1,
            minvalue=1,
            maxvalue=2147483647,
            cycle=False,
            cache=1,
        ),
        existing_nullable=False,
    )
    op.drop_table("users")
    # ### end Alembic commands ###


def data_upgrades():
    """Add any optional data upgrade migrations here!"""
    op.bulk_insert(
        UserModel.__table__,
        [
            {"first_name": "Glib", "last_name": "Garanin", "username": "GLEF1X"},
            {"first_name": "Sasha", "last_name": "Shemetun", "username": "Sasha255"},
        ],
    )


def data_downgrades():
    """Add any optional data downgrade migrations here!"""
    op.execute(delete(UserModel).where(true()))  # type: ignore