from __future__ import annotations

from src.application.use_cases.order.commands.create_order.command import (
    CreateOrderCommand,
)
from src.application.use_cases.order.commands.create_order.mapper import CreateOrderCommandToQueryMapper
from src.infrastructure.interfaces.database.repositories.order.repository import OrderRepository
from src.infrastructure.interfaces.database.unit_of_work import (
    AbstractUnitOfWork,
)
from src.utils.cqrs_lib.handler import BaseHandler
from src.utils.cqrs_lib.result import Result


class CreateOrderHandler(BaseHandler[CreateOrderCommand, Result[int]]):
    def __init__(
            self,
            order_repository: OrderRepository,
            uow: AbstractUnitOfWork,
    ) -> None:
        self._repository = order_repository
        self._uow = uow
        # TODO fix violation of DIP
        self._mapper = CreateOrderCommandToQueryMapper()

    async def handle(self, event: CreateOrderCommand) -> Result[int]:
        async with self._uow.pipeline:
            order_id = await self._repository.create_order(self._mapper.to_query(event))
            return Result.success(order_id)
