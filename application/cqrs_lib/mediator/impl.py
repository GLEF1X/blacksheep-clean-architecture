from typing import Any, Callable, Coroutine, Dict, List, Type

from loguru import logger

from application.cqrs_lib.command import Command
from application.cqrs_lib.exceptions import EventOrCommandNotFound
from application.cqrs_lib.mediator.interface import Event
from application.cqrs_lib.query import Query


class MediatorImpl:
    def __init__(
        self,
        query_handlers: Dict[
            Type[Query], List[Callable[..., Coroutine[Any, Any, Any]]]
        ],
        command_handlers: Dict[Type[Command], Callable[..., Coroutine[Any, Any, Any]]],
    ) -> None:
        self._query_handlers = query_handlers
        self._command_handlers = command_handlers

    async def handle(self, event: Event) -> Any:
        if isinstance(event, Query):
            return await self.handle_query(event)
        elif isinstance(event, Command):
            return await self.handle_command(event)
        else:
            raise EventOrCommandNotFound(f"{event} not found")

    async def handle_query(self, event: Query) -> Any:
        for handler in self._query_handlers[type(event)]:
            try:
                logger.debug("handling event {0} with handler {1}", event, handler)
                return await handler(event)
            except Exception as ex:
                logger.exception("Exception {0} handling event {1}", repr(ex), event)
                continue

    async def handle_command(self, command: Command) -> Any:
        logger.debug("handling command %s", command)
        try:
            handler = self._command_handlers[type(command)]
            return await handler(command)
        except Exception:
            logger.exception("Exception handling command {0}", command)
            raise
