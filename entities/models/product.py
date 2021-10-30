from __future__ import annotations

import dataclasses


@dataclasses.dataclass()
class Product:
    id: int
    price: float
    weight: int
