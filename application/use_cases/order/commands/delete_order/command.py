from __future__ import annotations

import dataclasses

from application.cqrs_lib.command import Command
from application.cqrs_lib.result import Result


@dataclasses.dataclass()
class DeleteOrderCommand(Command[Result[None]]):
    order_id: int
