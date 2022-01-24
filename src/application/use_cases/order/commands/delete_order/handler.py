from __future__ import annotations

from src.application.use_cases.order.commands.delete_order.command import (
    DeleteOrderCommand,
)
from src.infrastructure.interfaces.database.repositories.order.repository import OrderRepository
from src.infrastructure.interfaces.database.unit_of_work import (
    AbstractUnitOfWork,
)
from src.utils.cqrs_lib.handler import BaseHandler
from src.utils.cqrs_lib.result import Result


class CreateOrderHandler(BaseHandler[DeleteOrderCommand, Result[None]]):
    def __init__(
            self,
            repository: OrderRepository,
            uow: AbstractUnitOfWork,
    ) -> None:
        self._repository = repository
        self._uow = uow

    async def handle(self, event: DeleteOrderCommand) -> Result[None]:
        async with self._uow.pipeline:
            await self._repository.delete_order_by_id(order_id=event.order_id)

            return Result.success(None)
