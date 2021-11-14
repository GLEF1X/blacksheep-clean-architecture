from __future__ import annotations

import dataclasses
from datetime import datetime
from typing import List

from src.entities.models.product import Product
from src.entities.models.user import User


@dataclasses.dataclass()
class Order:
    """Anemic model, avoid creating rich model"""

    products: List[Product]
    created_at: datetime
    order_date: datetime
    customer: User
    id: int = dataclasses.field(init=False)
