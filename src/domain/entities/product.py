from __future__ import annotations

import dataclasses
from datetime import datetime

from src.domain.entities.base import Entity


@dataclasses.dataclass()
class Product(Entity):
    price: float
    weight: int
    created_at: datetime
