from __future__ import annotations

import dataclasses
from datetime import datetime
from typing import List, Optional

from src.domain.entities.base import Entity
from src.domain.entities.user import User
from src.domain.entities.product import Product


@dataclasses.dataclass()
class Order(Entity):
    order_date: datetime
    created_at: datetime
    products: List[Product]
    user: User


@dataclasses.dataclass()
class OrderItem(Entity):
    order_id: int
    product_id: int
    quantity: int
