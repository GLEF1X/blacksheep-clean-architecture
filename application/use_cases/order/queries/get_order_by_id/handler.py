from dataclasses import asdict
from typing import Any, Union

from application.cqrs_lib.handler import BaseHandler
from application.cqrs_lib.result import Failure, Result
from application.use_cases.order.dto.order_dto import (
    ObtainedOrderDto,
    ObtainedProductDto,
)
from application.use_cases.order.queries.get_order_by_id.query import GetOrderByIdQuery
from entities.domain_services.interfaces.order_service import (
    OrderDomainServiceInterface,
)
from infrastructure.implementation.database.orm.tables import OrderModel
from infrastructure.interfaces.database.data_access.repository import AbstractRepository
from infrastructure.interfaces.database.data_access.unit_of_work import (
    AbstractUnitOfWork,
)


class GetOrderByIdHandler(
    BaseHandler[GetOrderByIdQuery, Union[Result[ObtainedOrderDto], Result[None]]]
):
    def __init__(
        self,
        repository: AbstractRepository[OrderModel],
        order_domain_service: OrderDomainServiceInterface,
        uow: AbstractUnitOfWork[Any],
    ) -> None:
        self._repository = repository
        self._order_domain_service = order_domain_service
        self._uow = uow

    async def handle(
        self, event: GetOrderByIdQuery
    ) -> Union[Result[ObtainedOrderDto], Result[None]]:
        async with self._uow.pipeline:
            order_repository = self._repository.with_changed_query_model(OrderModel)
            order = await order_repository.get_one(OrderModel.id == event.id)

        if order is None:
            return Result.fail(Failure("Order was not found"))
        return Result.success(
            ObtainedOrderDto(
                id=order.id,
                # TODO create mapper
                products=[
                    ObtainedProductDto(**asdict(product)) for product in order.products
                ],
                total=self._order_domain_service.get_total(order),
                order_date=order.order_date,
                created_at=order.created_at,
            )
        )
