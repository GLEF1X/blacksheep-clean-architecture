from __future__ import annotations

import dataclasses
from typing import List

from entities.models.product import Product


@dataclasses.dataclass()
class Order:
    id: int
    products: List[Product]

