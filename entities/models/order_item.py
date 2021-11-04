from __future__ import annotations

import dataclasses

from entities.models.order import Order
from entities.models.product import Product


@dataclasses.dataclass()
class OrderItem:
    id: int
    order_id: int
    product_id: int
    quantity: int
    product: Product
    order: Order
