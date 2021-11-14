from datetime import datetime
from http import HTTPStatus
from typing import Any, Optional

from blacksheep import Response
from blacksheep.server.bindings import FromJSON
from blacksheep.server.openapi.common import EndpointDocs, ResponseInfo, ContentInfo

from src.application.cqrs_lib.result import Result
from src.application.use_cases.order.commands.create_order.command import (
    CreateOrderCommand,
)
from src.application.use_cases.order.commands.delete_order.command import (
    DeleteOrderCommand,
)
from src.application.use_cases.order.dto.order_dto import (
    CreateOrderDto,
    ObtainedOrderDto,
    ObtainedProductDto,
    CustomerDto,
)
from src.application.use_cases.order.queries.get_order_by_id.query import (
    GetOrderByIdQuery,
)
from src.web.api.controllers.base import RegistrableApiController

AnyResult = Result[Any]


class OrderController(RegistrableApiController):

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
        return self.status_code(status=HTTPStatus.NO_CONTENT)

    @classmethod
    def version(cls) -> Optional[str]:
        return "v1"

    @classmethod
    def class_name(cls) -> str:
        return "orders"

    def register(self) -> None:
        self.add_route(
            "GET",
            "/{order_id}",
            self.get_order,
            doc=EndpointDocs(
                responses={
                    200: ResponseInfo(
                        "Info about concrete order.",
                        content=[
                            ContentInfo(
                                ObtainedOrderDto,
                                examples=[
                                    ObtainedOrderDto(
                                        id=1,
                                        products=[
                                            ObtainedProductDto(
                                                price=50, weight=50, id=1
                                            )
                                        ],
                                        total=500,
                                        order_date=datetime.now(),
                                        created_at=datetime.now(),
                                        customer=CustomerDto(id=1, username="GLEF1X"),
                                    )
                                ],
                            )
                        ],
                    ),
                    404: ResponseInfo("Order was not found."),
                }
            ),
            scope="orders:all",
        )
        self.add_route(
            "PUT",
            "/create",
            self.create_order,
            doc=EndpointDocs(
                responses={201: ResponseInfo("Order was successfully created!")}
            ),
        )
        self.add_route(
            "DELETE",
            "/delete/{order_id}",
            self.delete_order,
            doc=EndpointDocs(
                responses={204: ResponseInfo("Order was successfully deleted!")}
            ),
        )
