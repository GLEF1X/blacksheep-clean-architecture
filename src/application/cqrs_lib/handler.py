from __future__ import annotations

import abc
from typing import Generic, TypeVar

from src.application.cqrs_lib.result import Result

_EventType = TypeVar("_EventType")
_ResultType = TypeVar("_ResultType", bound=Result)


class BaseHandler(abc.ABC, Generic[_EventType, _ResultType]):
    @abc.abstractmethod
    async def handle(self, event: _EventType) -> _ResultType:
        ...

    async def __call__(self, *args, **kwargs) -> _ResultType:
        return await self.handle(*args, **kwargs)
