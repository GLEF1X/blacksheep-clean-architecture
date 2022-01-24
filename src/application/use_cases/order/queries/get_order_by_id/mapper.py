from dataclasses import asdict

from src.application.use_cases.order.dto.order_dto import ObtainedOrderDto, ObtainedProductDto, UserDto
from src.domain.domain_services.interfaces.order_service import OrderDomainServiceInterface
from src.domain.entities.order import Order


class EntityToDtoMapper:

    def __init__(self, order_domain_service: OrderDomainServiceInterface,):
        self._order_domain_service = order_domain_service

    def to_dto(self, order: Order) -> ObtainedOrderDto:
        return ObtainedOrderDto(
            id=order.id,
            products=[
                ObtainedProductDto(**asdict(product)) for product in order.products
            ],
            total=self._order_domain_service.get_total(order),
            order_date=order.order_date,
            created_at=order.created_at,
            customer=UserDto(
                id=order.user.id, username=order.user.username
            ),
        )
