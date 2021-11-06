import abc
from typing import Any

from application.cqrs_lib.handler import BaseHandler, _EventType, _ResultType


class HandlerDecorator(BaseHandler[_EventType, _ResultType], abc.ABC):
    def __init__(self, handler: BaseHandler[_EventType, _ResultType]) -> None:
        self._wrapped_handler = handler

    @abc.abstractmethod
    async def handle(self, event: _EventType) -> Any:  # type: ignore
        pass
