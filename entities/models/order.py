from __future__ import annotations

from datetime import datetime
from typing import List

from entities.models.product import Product


class Order:
    id: int
    products: List[Product]
    created_at: datetime
    order_date: datetime

    # GRASP Information Expert pattern
    def get_order_price(self) -> float:
        return sum(product.price for product in self.products)
