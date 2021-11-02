from http import HTTPStatus
from typing import Optional

from blacksheep import Response
from blacksheep.server.bindings import FromJSON
from blacksheep.utils import join_fragments

from application.use_cases.implementation.order.commands.create_order.command import \
    CreateOrderCommand
from application.use_cases.implementation.order.dto.order_dto import ObtainedOrderDto, \
    CreateOrderDto
from application.use_cases.implementation.order.queries.get_order_by_id.query import (
    GetOrderByIdQuery,
)
from web.controllers.base import RegistrableApiController


class OrderController(RegistrableApiController):
    def register(self) -> None:
        self.add_route("GET", "/get/{order_id}", self.get_order)
        self.add_route("PUT", "/create", self.create_order)

    async def get_order(self, order_id: int) -> Response:
        order: ObtainedOrderDto = await self._mediator.handle(GetOrderByIdQuery(id=order_id))
        return self.pretty_json(order)

    async def create_order(self, gasket: FromJSON[CreateOrderDto]) -> Response:
        create_order_dto = gasket.value
        await self._mediator.handle(CreateOrderCommand(create_order_dto=create_order_dto))
        return self.status_code(status=HTTPStatus.CREATED)

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
