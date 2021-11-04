from __future__ import annotations

import dataclasses
from datetime import datetime
from typing import List

from entities.models.product import Product


@dataclasses.dataclass()
class Order:
    products: List[Product]
    created_at: datetime
    order_date: datetime
    id: int = dataclasses.field(init=False)

    # GRASP Information Expert pattern
    def get_order_price(self) -> float:
        return sum(product.price for product in self.products)
