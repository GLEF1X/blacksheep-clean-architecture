import dataclasses
from datetime import datetime
from typing import List


@dataclasses.dataclass()
class OrderPosition:
    product_id: int
    quantity: int


@dataclasses.dataclass()
class CreateOrderQuery:
    order_date: datetime
    customer_id: int
    positions: List[OrderPosition]
