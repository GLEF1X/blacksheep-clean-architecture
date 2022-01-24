from __future__ import annotations

import dataclasses

from src.utils.cqrs_lib import Command
from src.utils.cqrs_lib.result import Result


@dataclasses.dataclass()
class DeleteOrderCommand(Command[Result[None]]):
    order_id: int
