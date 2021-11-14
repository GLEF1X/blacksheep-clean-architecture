from __future__ import annotations

import dataclasses

from src.application.cqrs_lib.command import Command
from src.application.cqrs_lib.result import Result


@dataclasses.dataclass()
class DeleteOrderCommand(Command[Result[None]]):
    order_id: int
