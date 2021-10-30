from __future__ import annotations

import dataclasses

from sqlalchemy import Column, Identity, TIMESTAMP, func, SMALLINT, INTEGER, text, Table
from sqlalchemy.orm import registry, relationship

from entities.models.order import Order
from entities.models.product import Product

mapper_registry = registry()


@mapper_registry.mapped
@dataclasses.dataclass()
class OrderModel(Order):
    __table__ = Table(
        "products",
        mapper_registry.metadata,
        Column("id", INTEGER, Identity(always=True), nullable=False, primary_key=True),
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
        Column("id", INTEGER, Identity(always=True), nullable=False, primary_key=True),
        Column("created_at", TIMESTAMP(timezone=True), server_default=func.now(), nullable=False),
        Column("order_date", TIMESTAMP(timezone=True), nullable=False)
    )
