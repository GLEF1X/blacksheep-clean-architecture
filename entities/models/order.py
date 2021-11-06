from __future__ import annotations

import dataclasses
from datetime import datetime
from typing import List

from entities.models.product import Product


# Anemic model, avoid creating rich model
@dataclasses.dataclass()
class Order:
    products: List[Product]
    created_at: datetime
    order_date: datetime
    id: int = dataclasses.field(init=False)
