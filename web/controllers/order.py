from http import HTTPStatus
from typing import Any, Optional

from blacksheep import Response
from blacksheep.server.bindings import FromJSON

from application.cqrs_lib.result import Result
from application.use_cases.order.commands.create_order.command import CreateOrderCommand
from application.use_cases.order.commands.delete_order.command import DeleteOrderCommand
from application.use_cases.order.dto.order_dto import CreateOrderDto
from application.use_cases.order.queries.get_order_by_id.query import GetOrderByIdQuery
from web.controllers.base import RegistrableApiController

AnyResult = Result[Any]


class OrderController(RegistrableApiController):
    def register(self) -> None:
        self.add_route("GET", "/get/{order_id}", self.get_order)
        self.add_route("PUT", "/create", self.create_order)
        self.add_route("DELETE", "/delete/{order_id}", self.delete_order)

    async def get_order(self, order_id: int) -> Response:
        result: AnyResult = await self._mediator.handle(GetOrderByIdQuery(id=order_id))
        if result.failed:
            return self.status_code(HTTPStatus.NOT_FOUND)
        return self.pretty_json(result.value)

    async def create_order(self, gasket: FromJSON[CreateOrderDto]) -> Response:
        create_order_dto = gasket.value
        result: AnyResult = await self._mediator.handle(
            CreateOrderCommand(create_order_dto=create_order_dto)
        )
        if result.failed:
            return self.status_code(
                HTTPStatus.INTERNAL_SERVER_ERROR, result.error_message
            )
        return self.status_code(HTTPStatus.CREATED)

    async def delete_order(self, order_id: int) -> Response:
        result: AnyResult = await self._mediator.handle(
            DeleteOrderCommand(order_id=order_id)
        )
        if result.failed:
            return self.status_code(
                HTTPStatus.INTERNAL_SERVER_ERROR, result.error_message
            )
        return self.status_code(status=HTTPStatus.OK)

    @classmethod
    def version(cls) -> Optional[str]:
        return "v1"

    @classmethod
    def class_name(cls) -> str:
        return "orders"
