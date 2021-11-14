from src.application.cqrs_lib.query import Query
from src.application.use_cases.order.dto.order_dto import ObtainedOrderDto


class GetOrderByIdQuery(Query[ObtainedOrderDto]):
    id: int
