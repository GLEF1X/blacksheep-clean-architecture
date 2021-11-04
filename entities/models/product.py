from __future__ import annotations

import dataclasses
from datetime import datetime


@dataclasses.dataclass()
class Product:
    price: float
    weight: int
    created_at: datetime
    id: int = dataclasses.field(init=False)
