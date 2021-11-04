from typing import Any

from application.cqrs_lib.handler import BaseHandler
from application.cqrs_lib.result import Result
from application.use_cases.order.dto.order_dto import ObtainedOrderDto
from application.use_cases.order.queries.get_order_by_id.query import (
    GetOrderByIdQuery,
)
from entities.domain_services.interfaces.order_service import (
    OrderDomainServiceInterface,
)
from entities.models.order import Order
from infrastructure.implementation.database.orm.tables import OrderModel
from infrastructure.interfaces.database.data_access.repository import AbstractRepository
from infrastructure.interfaces.database.data_access.unit_of_work import (
    AbstractUnitOfWork,
)


class GetOrderByIdHandler(BaseHandler[GetOrderByIdQuery, Result[ObtainedOrderDto]]):
    def __init__(
        self,
        repository: AbstractRepository[Order],
        order_domain_service: OrderDomainServiceInterface,
        uow: AbstractUnitOfWork[Any],
    ) -> None:
        self._repository = repository
        self._order_domain_service = order_domain_service
        self._uow = uow

    async def handle(self, event: GetOrderByIdQuery) -> Result[ObtainedOrderDto]:
        async with self._uow.pipeline:
            self._repository.with_changed_query_model(OrderModel)
            order = await self._repository.get_one(OrderModel.id == event.id)

        if order is None:
            raise
        return Result.success(
            ObtainedOrderDto(
                id=order.id,
                products=order.products,
                total=self._order_domain_service.get_total(order),
                order_date=order.order_date,
                created_at=order.created_at,
            )
        )
