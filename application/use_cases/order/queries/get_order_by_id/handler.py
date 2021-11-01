from entities.domain_services.interfaces.order_service import OrderDomainServiceInterface
from entities.models.order import Order
from infrastructure.implementation.database.data_access.unit_of_work import AbstractUnitOfWork
from infrastructure.implementation.database.orm.tables import OrderModel
from infrastructure.interfaces.database.data_access.repository import AbstractRepository
from application.use_cases.interactor.mediator import BaseHandler
from application.use_cases.order.dto.order_dto import OrderDto
from application.use_cases.order.queries.get_order_by_id.query import GetOrderByIdQuery


class GetOrderByIdHandler(BaseHandler[GetOrderByIdQuery, OrderDto]):

    def __init__(self, repository: AbstractRepository[Order],
                 order_domain_service: OrderDomainServiceInterface, uow: AbstractUnitOfWork) -> None:
        self._repository = repository
        self._order_domain_service = order_domain_service
        self._uow = uow

    async def handle(self, event: GetOrderByIdQuery) -> OrderDto:
        async with self._uow.acquire:
            self._repository.install(OrderModel)
            order = await self._repository.get_one()

        if order is None:
            raise

        return OrderDto(id=order.id, products=order.products)
