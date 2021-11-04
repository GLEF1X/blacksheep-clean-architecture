import dataclasses

from application.cqrs_lib.query import Query
from application.use_cases.order.dto.order_dto import ObtainedOrderDto


@dataclasses.dataclass()
class GetOrderByIdQuery(Query[ObtainedOrderDto]):
    id: int
