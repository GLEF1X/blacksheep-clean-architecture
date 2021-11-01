import abc
import logging
from typing import Generic, TypeVar, Dict, Type, List, Callable, Any, Union

logger = logging.getLogger(__name__)

_EventType = TypeVar("_EventType")


class BaseHandler(abc.ABC, Generic[_EventType]):
    @abc.abstractmethod
    def __call__(self, event: _EventType) -> None:
        ...


Message = Union[Command, Query]


class Mediator:

    def __init__(
            self,
            query_handlers: Dict[Type[Query], List[Callable[..., Any]]],
            command_handlers: Dict[Type[Command], Callable[..., Any]],
    ):
        self._query_handlers = query_handlers
        self._command_handlers = command_handlers

    def handle(self, message: Message):
        self.queue = [message]
        while self.queue:
            message = self.queue.pop(0)
            if isinstance(message, Query):
                self.handle_query(message)
            elif isinstance(message, Command):
                self.handle_command(message)
            else:
                raise Exception(f"{message} was not an Event or Command")

    def handle_query(self, event: Query):
        for handler in self._query_handlers[type(event)]:
            try:
                logger.debug("handling event %s with handler %s", event, handler)
                handler(event)
            except Exception:
                logger.exception("Exception handling event %s", event)
                continue

    def handle_command(self, command: Command):
        logger.debug("handling command %s", command)
        try:
            handler = self._command_handlers[type(command)]
            handler(command)
        except Exception:
            logger.exception("Exception handling command %s", command)
            raise
