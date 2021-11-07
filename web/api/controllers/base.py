import abc
from collections import Callable
from typing import Any, TypeVar

from blacksheep.server.authorization import auth
from blacksheep.server.controllers import ApiController
from blacksheep.server.openapi.v3 import OpenAPIHandler
from blacksheep.server.routing import RoutesRegistry
from dynaconf import LazySettings

from application.cqrs_lib import MediatorInterface

_HandlerType = TypeVar("_HandlerType", bound=Callable[..., Any])


class RegistrableApiController(ApiController):
    def __init__(
            self,
            router: RoutesRegistry,
            settings: LazySettings,
            mediator: MediatorInterface,
            docs: OpenAPIHandler,
    ) -> None:
        self._router = router
        self._settings = settings
        self._mediator = mediator
        self._docs = docs

    @abc.abstractmethod
    def register(self) -> None:
        """
        There is the place, where you can register your routes.
        The main goal of creating this method is getting rid of global variables and decorators.
        To my mind, It's descriptive to register routes exactly in controller.

        """
        ...

    def add_route(
            self, method: str, path: str, controller_method: Callable[..., Any],
            require_auth: bool = True, include_in_swagger: bool = True
    ) -> None:
        """
        Helps to add new route to router, justify patching controller methods.
        This method must be here, because metaclass of `ApiController` rely on decorators,
        that's why registering a new route is too problematic.

        :param method: HTTP method
        :param path: relative path to endpoint
        :param controller_method:
        :param require_auth:
        :param include_in_swagger:
        """
        handler_func = controller_method.__func__  # noqa  # type: ignore
        patched_method = self._mark_handler_as_method_of_controller(handler_func)
        if require_auth:
            patched_method = auth()(patched_method)
        if not include_in_swagger:
            patched_method = self._docs.ignore()(patched_method)
        self._router.add(method, path, patched_method)

    def _mark_handler_as_method_of_controller(
            self, handler: _HandlerType
    ) -> _HandlerType:
        controller_type = self.__class__
        setattr(handler, "controller_type", controller_type)
        return handler
