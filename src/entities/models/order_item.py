from __future__ import annotations

import dataclasses


@dataclasses.dataclass()
class OrderItem:
    order_id: int
    product_id: int
    quantity: int
    id: int = dataclasses.field(init=False)
