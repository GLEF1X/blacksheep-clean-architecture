from dataclasses import asdict
from typing import Any, Union

from src.application.cqrs_lib.handler import BaseHandler
from src.application.cqrs_lib.result import Failure, Result
from src.application.use_cases.order.dto.order_dto import (
    ObtainedOrderDto,
    ObtainedProductDto,
    CustomerDto,
)
from src.application.use_cases.order.queries.get_order_by_id.query import (
    GetOrderByIdQuery,
)
from src.entities.domain_services.interfaces.order_service import (
    OrderDomainServiceInterface,
)
from src.entities.models.order import Order
from src.infrastructure.implementation.database.orm.tables import OrderModel
from src.infrastructure.interfaces.database.data_access.repository import (
    AbstractRepository,
)
from src.infrastructure.interfaces.database.data_access.unit_of_work import (
    AbstractUnitOfWork,
)


class GetOrderByIdHandler(
    BaseHandler[GetOrderByIdQuery, Union[Result[ObtainedOrderDto], Result[None]]]
):
    def __init__(
        self,
        repository: AbstractRepository[Order],
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
                customer=CustomerDto(
                    id=order.customer.id, username=order.customer.username
                ),
            )
        )
