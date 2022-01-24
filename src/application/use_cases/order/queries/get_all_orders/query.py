from typing import List

from src.application.use_cases.order.dto.order_dto import ObtainedOrderDto
from src.utils.cqrs_lib import Query


class GetAllOrdersQuery(Query[List[ObtainedOrderDto]]):
    pass
