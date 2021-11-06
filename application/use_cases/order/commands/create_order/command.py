from __future__ import annotations

from application.cqrs_lib.command import Command
from application.use_cases.order.dto.order_dto import CreateOrderDto


class CreateOrderCommand(Command[int]):
    create_order_dto: CreateOrderDto
