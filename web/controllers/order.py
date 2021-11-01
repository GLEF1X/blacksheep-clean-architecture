from typing import Optional

from blacksheep import Response
from blacksheep.utils import join_fragments

from application.use_cases.order import OrderDto
from application.use_cases.order.queries.get_order_by_id.query import GetOrderByIdQuery
from web.controllers.base import RegistrableApiController


class OrderController(RegistrableApiController):

    def register(self) -> None:
        self.add_route("/get/{order_id}", self.get_order)

    async def get_order(self, order_id: int) -> Response:
        order: OrderDto = await self._mediator.handle(GetOrderByIdQuery(id=order_id))
        return self.pretty_json(order)

    @classmethod
    def version(cls) -> Optional[str]:
        return "v1"

    @classmethod
    def route(cls) -> str:
        cls_name = "orders"
        cls_version = cls.version() or ""
        if cls_version and cls_name.endswith(cls_version.lower()):
            cls_name = cls_name[: -len(cls_version)]
        return join_fragments("api", cls_version, cls_name)
