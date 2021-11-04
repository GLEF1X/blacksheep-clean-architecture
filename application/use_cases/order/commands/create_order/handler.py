from __future__ import annotations

from typing import Any

from application.cqrs_lib.handler import BaseHandler
from application.cqrs_lib.result import Result
from application.use_cases.order.commands.create_order.command import (
    CreateOrderCommand,
)
from entities.models.order import Order
from infrastructure.implementation.database.orm.tables import OrderModel, OrderItemModel
from infrastructure.interfaces.database.data_access.repository import AbstractRepository
from infrastructure.interfaces.database.data_access.unit_of_work import (
    AbstractUnitOfWork,
)


class CreateOrderHandler(BaseHandler[CreateOrderCommand, Result[int]]):
    def __init__(
        self,
        repository: AbstractRepository[Order],
        uow: AbstractUnitOfWork[Any],
    ) -> None:
        self._repository = repository
        self._uow = uow

    async def handle(self, event: CreateOrderCommand) -> Result[int]:
        async with self._uow.pipeline:
            order_id = await self._repository.with_changed_query_model(OrderModel).add(
                order_date=event.create_order_dto.order_date
            )
            for product_dto in event.create_order_dto.products:
                models_to_insert_in_m2m = [
                    OrderItemModel(
                        product_id=product_dto.id,
                        order_id=order_id,
                        quantity=product_dto.quantity,
                    )
                ]
            await self._repository.with_changed_query_model(OrderItemModel).add_many(
                *models_to_insert_in_m2m
            )

        return Result.success(order_id)
