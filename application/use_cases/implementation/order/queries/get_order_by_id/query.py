import dataclasses

from application.use_cases.base import Query


@dataclasses.dataclass()
class GetOrderByIdQuery(Query):
    id: int
