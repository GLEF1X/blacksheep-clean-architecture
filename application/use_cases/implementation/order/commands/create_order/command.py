from __future__ import annotations

import dataclasses

from application.use_cases.base import Command
from application.use_cases.implementation.order.dto.order_dto import CreateOrderDto


@dataclasses.dataclass()
class CreateOrderCommand(Command):
    create_order_dto: CreateOrderDto
