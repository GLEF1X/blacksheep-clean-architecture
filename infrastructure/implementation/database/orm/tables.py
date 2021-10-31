from __future__ import annotations

import dataclasses

from sqlalchemy import Column, Identity, TIMESTAMP, func, SMALLINT, INTEGER, text, Table, \
    ForeignKey, Integer
from sqlalchemy.orm import registry, relationship

from entities.models.order import Order
from entities.models.product import Product
from entities.models.order_item import OrderItem

mapper_registry = registry()


@mapper_registry.mapped
@dataclasses.dataclass()
class OrderModel(Order):
    __table__ = Table(
        "products",
        mapper_registry.metadata,
        Column("id", INTEGER, Identity(always=True, cache=5), nullable=False, primary_key=True),
        Column("price", INTEGER, nullable=False),  # store price in cents
        Column("weight", SMALLINT, nullable=False, server_default=text("1"))
    )

    __mapper_args__ = {  # type: ignore
        "properties": {
            "products": relationship("ProductModel")
        }
    }


@mapper_registry.mapped
@dataclasses.dataclass()
class ProductModel(Product):
    __table__ = Table(
        "orders",
        mapper_registry.metadata,
        Column("id", INTEGER, Identity(always=True, cache=5), nullable=False, primary_key=True),
        Column("created_at", TIMESTAMP(timezone=True), server_default=func.now(), nullable=False),
        Column("order_date", TIMESTAMP(timezone=True), nullable=False)
    )


@mapper_registry.mapped
@dataclasses.dataclass()
class OrderItemModel(OrderItem):
    __table__ = Table(
        "order_items",
        mapper_registry.metadata,
        Column("id", INTEGER, Identity(always=True, cache=5), nullable=False, primary_key=True),
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
            unique=True
        ),
        Column(
            "product_id",
            Integer,
            ForeignKey(
                "products.id",
                ondelete="CASCADE",
                onupdate="CASCADE",
                name="FK__order_items__order_item_product",
            )
        ),
        Column("quantity", SMALLINT, nullable=False, server_default=text("1"))
    )

    __mapper_args__ = {
        "properties": {
            "product": relationship(
                "Product",
                uselist=False,
                primaryjoin="OrderItemModel.product_id == ProductModel.id",
                enable_typechecks=True,
            ),
            "order": relationship(
                "Order",
                uselist=False,
                enable_typechecks=True,
                primaryjoin="OrderItemModel.order_id == OrderModel.id",
            )
        }
    }
