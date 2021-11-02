from __future__ import annotations

from typing import Protocol, Union, Any

from application.use_cases.base import Command, Query


class MediatorInterface(Protocol):
    async def handle(self, event: Union[Command, Query]) -> Any:
        ...
