from __future__ import annotations

import dataclasses
from datetime import datetime
from typing import List

from entities.models.product import Product


@dataclasses.dataclass()
class ObtainedOrderDto:
    id: int
    products: List[Product]
    total: float
    order_date: datetime
    created_at: datetime


@dataclasses.dataclass()
class CreateOrderDto:
    products: List[int]
    order_date: datetime
