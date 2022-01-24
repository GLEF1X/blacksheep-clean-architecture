from __future__ import annotations

from src.application.use_cases.order.dto.order_dto import CreateOrderDto
from src.utils.cqrs_lib import Command


class CreateOrderCommand(Command[int]):
    create_order_dto: CreateOrderDto
