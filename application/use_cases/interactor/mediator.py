import abc
import logging
from collections import deque
from typing import Generic, TypeVar, Dict, Type, List, Callable, Any, Union, Deque

from application.use_cases.base import Command, Query

logger = logging.getLogger(__name__)

_EventType = TypeVar("_EventType")
_ResultType = TypeVar("_ResultType")


class BaseHandler(abc.ABC, Generic[_EventType, _ResultType]):
    @abc.abstractmethod
    async def handle(self, event: _EventType) -> _ResultType:
        ...

    async def __call__(self, *args, **kwargs) -> None:
        await self.handle(*args, **kwargs)


Event = Union[Command, Query]


class Mediator:

    def __init__(
            self,
            query_handlers: Dict[Type[Query], List[Callable[..., Any]]],
            command_handlers: Dict[Type[Command], Callable[..., Any]],
    ) -> None:
        self._query_handlers = query_handlers
        self._command_handlers = command_handlers
        self._deque: Deque[Event] = deque()

    async def handle(self, event: Event) -> Any:
        self._deque.append(event)
        while self._deque:
            event = self._deque.popleft()
            if isinstance(event, Query):
                return await self.handle_query(event)
            elif isinstance(event, Command):
                return await self.handle_command(event)
            else:
                raise Exception(f"{event} was not an Event or Command")

    async def handle_query(self, event: Query) -> Any:
        for handler in self._query_handlers[type(event)]:
            try:
                logger.debug("handling event %s with handler %s", event, handler)
                return await handler(event)
            except Exception as ex:
                logger.exception("Exception %s handling event %s", repr(ex), event)
                continue

    async def handle_command(self, command: Command) -> Any:
        logger.debug("handling command %s", command)
        try:
            handler = self._command_handlers[type(command)]
            return await handler(command)
        except Exception:
            logger.exception("Exception handling command %s", command)
            raise
