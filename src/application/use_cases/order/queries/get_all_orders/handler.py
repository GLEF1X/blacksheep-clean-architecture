from typing import Union, List

from src.application.use_cases.order.dto.order_dto import ObtainedOrderDto
from src.application.use_cases.order.queries.get_all_orders.query import GetAllOrdersQuery
from src.application.use_cases.order.queries.get_order_by_id.mapper import EntityToDtoMapper
from src.application.use_cases.order.queries.get_order_by_id.query import GetOrderByIdQuery
from src.domain.domain_services.interfaces.order_service import OrderDomainServiceInterface
from src.infrastructure.interfaces.database.repositories.order.repository import OrderRepository
from src.infrastructure.interfaces.database.unit_of_work import AbstractUnitOfWork
from src.utils.cqrs_lib.handler import BaseHandler
from src.utils.cqrs_lib.result import Result, Failure
from src.utils.exceptions import QueryError


class GetAllOrdersHandler(
    BaseHandler[GetAllOrdersQuery, Union[Result[List[ObtainedOrderDto]], Result[None]]]
):
    def __init__(
            self,
            repository: OrderRepository,
            order_domain_service: OrderDomainServiceInterface,
            uow: AbstractUnitOfWork,
    ) -> None:
        self._repository = repository
        self._order_domain_service = order_domain_service
        self._uow = uow
        # TODO fix violation of DIP
        self._mapper = EntityToDtoMapper(self._order_domain_service)

    async def handle(self, event: GetOrderByIdQuery) -> Union[Result[List[ObtainedOrderDto]], Result[None]]:
        async with self._uow.pipeline:
            try:
                bunch_of_orders = await self._repository.get_all_orders()
            except QueryError as ex:
                return Result.fail(Failure(ex.hint))
        return Result.success([self._mapper.to_dto(order) for order in bunch_of_orders])
