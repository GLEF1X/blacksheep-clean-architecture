"""data migrations

Revision ID: d1cd89e2cc41
Revises: 2df077842216
Create Date: 2021-11-02 08:09:16.896949

"""

# revision identifiers, used by Alembic.
from datetime import datetime

from sqlalchemy import delete, true

from infrastructure.implementation.database.orm.tables import (
    ProductModel,
    OrderModel,
    OrderItemModel,
)

revision = "d1cd89e2cc41"
down_revision = "2df077842216"

from alembic import context
from alembic import op


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
    pass


def schema_downgrades():
    """schema downgrade migrations go here."""
    pass


def data_upgrades():
    """Add any optional data upgrade migrations here!"""
    op.bulk_insert(
        ProductModel.__table__,
        [
            {"price": 5000, "weight": 5},
            {"price": 6000, "weight": 8},
            {"price": 1000, "weight": 1},
        ],
    )
    op.bulk_insert(
        OrderModel.__table__,
        [
            {"order_date": datetime.now()},
            {"order_date": datetime.now()},
            {"order_date": datetime.now()},
        ],
    )
    op.bulk_insert(
        OrderItemModel.__table__,
        [
            {"order_id": 1, "product_id": 1, "quantity": 5},
            {"order_id": 2, "product_id": 2, "quantity": 7},
            {"order_id": 3, "product_id": 3, "quantity": 1},
        ],
    )


def data_downgrades():
    """Add any optional data downgrade migrations here!"""
    op.execute(delete(ProductModel).where(true()))  # type: ignore
    op.execute(delete(OrderModel).where(true()))
    op.execute(delete(OrderItemModel).where(true()))
