from __future__ import annotations

from typing import Protocol, TypeVar, Union

from src.application.cqrs_lib.command import Command
from src.application.cqrs_lib.query import Query

_TProcessingResult = TypeVar("_TProcessingResult")
Event = Union[Command[_TProcessingResult], Query[_TProcessingResult]]


class MediatorInterface(Protocol):
    async def handle(self, event: Event) -> _TProcessingResult:
        ...
