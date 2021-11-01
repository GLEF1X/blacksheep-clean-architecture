from __future__ import annotations

import dataclasses
from datetime import datetime


@dataclasses.dataclass()
class Product:
    id: int
    price: float
    weight: int
    created_at: datetime
