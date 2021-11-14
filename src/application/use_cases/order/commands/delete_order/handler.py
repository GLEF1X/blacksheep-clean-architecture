from __future__ import annotations

from typing import Any

from src.application.cqrs_lib.handler import BaseHandler
from src.application.cqrs_lib.result import Result
from src.application.use_cases.order.commands.delete_order.command import (
    DeleteOrderCommand,
)
from src.entities.models.order import Order
from src.infrastructure.implementation.database.orm.tables import (
    OrderItemModel,
    OrderModel,
)
from src.infrastructure.interfaces.database.data_access.repository import (
    AbstractRepository,
)
from src.infrastructure.interfaces.database.data_access.unit_of_work import (
    AbstractUnitOfWork,
)


class CreateOrderHandler(BaseHandler[DeleteOrderCommand, Result[None]]):
    def __init__(
        self,
        repository: AbstractRepository[Order],
        uow: AbstractUnitOfWork[Any],
    ) -> None:
        self._repository = repository
        self._uow = uow

    async def handle(self, event: DeleteOrderCommand) -> Result[None]:
        async with self._uow.pipeline:
            await self._repository.with_changed_query_model(OrderModel).delete(
                OrderModel.id == event.order_id
            )
            await self._repository.with_changed_query_model(OrderItemModel).delete(
                OrderItemModel.order_id == event.order_id
            )

        return Result.success(None)
