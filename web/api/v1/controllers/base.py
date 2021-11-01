import abc
import types
from collections import Callable
from typing import Any, TypeVar

from blacksheep.server.controllers import ApiController
from blacksheep.server.routing import RoutesRegistry
from dynaconf import LazySettings

_HandlerType = TypeVar("_HandlerType", bound=Callable[..., Any])


class RegistrableApiController(ApiController):
    def __init__(self, router: RoutesRegistry, settings: LazySettings) -> None:
        self._router = router
        self._settings = settings

    @abc.abstractmethod
    def register(self) -> None:
        ...

    def add_route(self, path: str, controller_method: Callable[..., Any]) -> None:
        handler_func = controller_method.__func__  # noqa  # type: ignore
        self._router.add_get(
            path, self._mark_handler_as_method_of_controller(handler_func)
        )

    def _mark_handler_as_method_of_controller(
        self, handler: _HandlerType
    ) -> _HandlerType:
        controller_type = self.__class__
        setattr(handler, "controller_type", controller_type)
        return handler
