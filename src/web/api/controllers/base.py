import abc
import warnings
from collections import Callable
from typing import Any, TypeVar, Optional

from blacksheep.server.authorization import auth
from blacksheep.server.controllers import ApiController
from blacksheep.server.openapi.common import EndpointDocs
from blacksheep.server.openapi.v3 import OpenAPIHandler
from blacksheep.server.routing import RoutesRegistry
from dynaconf import LazySettings

from src.utils.cqrs_lib import MediatorInterface

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
        self,
        *decorators: Callable[[_HandlerType], _HandlerType],
        method: str,
        path: str,
        controller_method: _HandlerType,
        include_in_swagger: bool = True,
        doc: Optional[EndpointDocs] = None,
        scope: str = "authorization",
        disable_authorization: bool = True,
    ) -> None:
        """
        Helps to add new route to router, justify patching controller methods.
        This method must be here, because metaclass of `ApiController` rely on decorators,
        that's why registering a new route is too problematic.

        :param method: HTTP method
        :param path: relative path to endpoint
        :param controller_method:
        :param include_in_swagger:
        :param doc:
        :param scope:
        :param disable_authorization:
        """
        handler_func = controller_method.__func__  # noqa  # type: ignore
        handler = self._mark_handler_as_method_of_controller(handler_func)
        if not disable_authorization:
            handler = auth(policy=scope)(handler)
        if doc is not None and include_in_swagger is False:
            warnings.warn(
                "It's senseless to pass on the doc parameter to the `add_route` "
                "method and do not include an api endpoint in swagger.",
                UserWarning,
                stacklevel=2,
            )
        if not include_in_swagger:
            handler = self._docs.ignore()(handler)
        elif doc is not None:
            handler = self._docs(doc)(handler)

        for decorator in decorators:
            handler = decorator(handler)

        self._router.add(method, path, handler)

    def _mark_handler_as_method_of_controller(self, handler: _HandlerType) -> _HandlerType:
        controller_type = self.__class__
        setattr(handler, "controller_type", controller_type)
        return handler
