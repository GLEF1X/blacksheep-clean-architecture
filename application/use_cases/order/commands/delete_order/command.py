from __future__ import annotations

import dataclasses

from application.cqrs_lib.command import Command


@dataclasses.dataclass()
class DeleteOrderCommand(Command[None]):
    order_id: int
