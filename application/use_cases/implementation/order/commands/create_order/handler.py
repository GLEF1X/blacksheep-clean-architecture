from __future__ import annotations

from dataclasses import asdict
from typing import Any

from application.use_cases.implementation.interactor.mediatorimpl import BaseHandler
from application.use_cases.implementation.order.commands.create_order.command import \
    CreateOrderCommand
from entities.models.order import Order
from infrastructure.implementation.database.data_access.unit_of_work import AbstractUnitOfWork
from infrastructure.interfaces.database.data_access.repository import AbstractRepository


class CreateOrderHandler(BaseHandler[CreateOrderCommand, int]):

    def __init__(
            self,
            repository: AbstractRepository[Order],
            uow: AbstractUnitOfWork[AbstractRepository[Any]],
    ) -> None:
        self._repository = repository
        self._uow = uow

    async def handle(self, event: CreateOrderCommand) -> int:
        async with self._uow.pipeline:
            self._repository.install(Order)
            payload = asdict(event.create_order_dto)
            order_id = await self._repository.add(**payload)

        return order_id
