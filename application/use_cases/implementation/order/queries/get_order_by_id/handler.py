from typing import Any

from application.use_cases.implementation.interactor.mediatorimpl import BaseHandler
from application.use_cases.implementation.order.dto.order_dto import ObtainedOrderDto
from application.use_cases.implementation.order.queries.get_order_by_id.query import (
    GetOrderByIdQuery,
)
from entities.domain_services.interfaces.order_service import (
    OrderDomainServiceInterface,
)
from entities.models.order import Order
from infrastructure.implementation.database.data_access.unit_of_work import (
    AbstractUnitOfWork,
)
from infrastructure.implementation.database.orm.tables import OrderModel
from infrastructure.interfaces.database.data_access.repository import AbstractRepository


class GetOrderByIdHandler(BaseHandler[GetOrderByIdQuery, ObtainedOrderDto]):
    def __init__(
        self,
        repository: AbstractRepository[Order],
        order_domain_service: OrderDomainServiceInterface,
        uow: AbstractUnitOfWork[AbstractRepository[Any]],
    ) -> None:
        self._repository = repository
        self._order_domain_service = order_domain_service
        self._uow = uow

    async def handle(self, event: GetOrderByIdQuery) -> ObtainedOrderDto:
        async with self._uow.pipeline:
            self._repository.install(OrderModel)
            order = await self._repository.get_one(OrderModel.id == event.id)

        if order is None:
            raise
        return ObtainedOrderDto(
            id=order.id,
            products=order.products,
            total=self._order_domain_service.get_total(order),
            order_date=order.order_date,
            created_at=order.created_at
        )
