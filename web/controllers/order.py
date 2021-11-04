from http import HTTPStatus
from typing import Optional

from blacksheep import Response
from blacksheep.server.bindings import FromJSON

from application.use_cases.order.commands.create_order.command import (
    CreateOrderCommand,
)
from application.use_cases.order.commands.delete_order.command import DeleteOrderCommand
from application.use_cases.order.dto.order_dto import CreateOrderDto, ObtainedOrderDto
from application.use_cases.order.queries.get_order_by_id.query import (
    GetOrderByIdQuery,
)
from web.controllers.base import RegistrableApiController


class OrderController(RegistrableApiController):
    def register(self) -> None:
        self.add_route("GET", "/get/{order_id}", self.get_order)
        self.add_route("PUT", "/create", self.create_order)
        self.add_route("DELETE", "/delete/{order_id}", self.delete_order)

    async def get_order(self, order_id: int) -> Response:
        order: ObtainedOrderDto = await self._mediator.handle(GetOrderByIdQuery(id=order_id))
        return self.pretty_json(order)

    async def create_order(self, gasket: FromJSON[CreateOrderDto]) -> Response:
        create_order_dto = gasket.value
        await self._mediator.handle(
            CreateOrderCommand(create_order_dto=create_order_dto)
        )
        return self.status_code(status=HTTPStatus.CREATED)

    async def delete_order(self, order_id: int) -> Response:
        await self._mediator.handle(DeleteOrderCommand(order_id=order_id))
        return self.status_code(status=HTTPStatus.OK)

    @classmethod
    def version(cls) -> Optional[str]:
        return "v1"

    @classmethod
    def class_name(cls) -> str:
        return "orders"
