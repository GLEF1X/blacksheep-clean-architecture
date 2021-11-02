from __future__ import annotations

from sqlalchemy import (
    Column,
    Identity,
    TIMESTAMP,
    func,
    SMALLINT,
    INTEGER,
    text,
    Table,
    ForeignKey,
    Integer,
)
from sqlalchemy.orm import registry, relationship

from entities.models.order import Order
from entities.models.order_item import OrderItem
from entities.models.product import Product

mapper_registry = registry()


@mapper_registry.mapped
class OrderModel(Order):
    __table__ = Table(
        "orders",
        mapper_registry.metadata,
        Column(
            "id",
            INTEGER,
            Identity(always=True, cache=5),
            nullable=False,
            primary_key=True,
        ),
        Column(
            "created_at",
            TIMESTAMP(timezone=True),
            server_default=func.now(),
            nullable=False,
        ),
        Column("order_date", TIMESTAMP(timezone=True), nullable=False),
    )

    __mapper_args__ = {  # type: ignore
        "properties": {
            "products": relationship(
                "ProductModel",
                secondary=lambda: OrderItemModel.__table__,
                back_populates="orders",
                enable_typechecks=True,
                lazy="joined",
            )
        }
    }


@mapper_registry.mapped
class ProductModel(Product):
    __table__ = Table(
        "products",
        mapper_registry.metadata,
        Column(
            "id",
            INTEGER,
            Identity(always=True, cache=5),
            nullable=False,
            primary_key=True,
        ),
        Column(
            "created_at",
            TIMESTAMP(timezone=True),
            server_default=func.now(),
            nullable=False,
        ),
        Column("price", INTEGER, nullable=False),  # store price in cents
        Column("weight", SMALLINT, nullable=False, server_default=text("1")),
    )

    __mapper_args__ = {  # type: ignore
        "properties": {
            "orders": relationship(
                "OrderModel",
                secondary=lambda: OrderItemModel.__table__,
                back_populates="products",
                enable_typechecks=True,
            )
        }
    }


@mapper_registry.mapped
class OrderItemModel(OrderItem):
    __table__ = Table(
        "order_items",
        mapper_registry.metadata,
        Column(
            "id",
            INTEGER,
            Identity(always=True, cache=5),
            nullable=False,
            primary_key=True,
        ),
        Column(
            "order_id",
            INTEGER,
            ForeignKey(
                "orders.id",
                ondelete="CASCADE",
                onupdate="CASCADE",
                name="FK__order_items__order_item_order",
            ),
            nullable=False,
            unique=True,
        ),
        Column(
            "product_id",
            Integer,
            ForeignKey(
                "products.id",
                ondelete="CASCADE",
                onupdate="CASCADE",
                name="FK__order_items__order_item_product",
            ),
        ),
        Column("quantity", SMALLINT, nullable=False, server_default=text("1")),
    )
