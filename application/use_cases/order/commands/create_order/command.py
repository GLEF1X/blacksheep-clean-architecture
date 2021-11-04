from __future__ import annotations

import dataclasses

from application.cqrs_lib.command import Command
from application.use_cases.order.dto.order_dto import CreateOrderDto


@dataclasses.dataclass()
class CreateOrderCommand(Command[int]):
    create_order_dto: CreateOrderDto
