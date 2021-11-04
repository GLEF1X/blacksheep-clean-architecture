from __future__ import annotations

from typing import Any

from application.cqrs_lib.handler import BaseHandler
from application.use_cases.order.commands.delete_order.command import DeleteOrderCommand
from entities.models.order import Order
from infrastructure.implementation.database.orm.tables import OrderModel, OrderItemModel
from infrastructure.interfaces.database.data_access.repository import AbstractRepository
from infrastructure.interfaces.database.data_access.unit_of_work import (
    AbstractUnitOfWork,
)


class CreateOrderHandler(BaseHandler[DeleteOrderCommand, None]):
    def __init__(
        self,
        repository: AbstractRepository[Order],
        uow: AbstractUnitOfWork[Any],
    ) -> None:
        self._repository = repository
        self._uow = uow

    async def handle(self, event: DeleteOrderCommand) -> None:
        async with self._uow.pipeline:
            await self._repository.with_changed_query_model(OrderModel).delete(
                OrderModel.id == event
            )
            await self._repository.with_changed_query_model(OrderItemModel).delete(
                OrderItemModel.order_id == event.order_id
            )
