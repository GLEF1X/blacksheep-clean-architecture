from __future__ import annotations

from src.application.cqrs_lib.command import Command
from src.application.use_cases.order.dto.order_dto import CreateOrderDto


class CreateOrderCommand(Command[int]):
    create_order_dto: CreateOrderDto
