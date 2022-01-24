from typing import Protocol, List

from src.domain.entities.order import Order
from src.infrastructure.implementation.database.repositories.order.queries import CreateOrderQuery


class OrderRepository(Protocol):

    async def get_order_by_id(self, order_id: int) -> Order: ...

    async def create_order(self, query: CreateOrderQuery) -> int: ...

    async def delete_order_by_id(self, order_id: int) -> None: ...

    async def get_all_orders(self) -> List[Order]: ...
