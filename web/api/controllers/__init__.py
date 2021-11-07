from typing import List

from blacksheep.server.openapi.v3 import OpenAPIHandler
from blacksheep.server.routing import RoutesRegistry
from dynaconf import LazySettings

from web.api.controllers.base import RegistrableApiController

from .oauth import OauthController
from .order import OrderController


def install(route_registry: RoutesRegistry, settings: LazySettings, docs: OpenAPIHandler) -> None:
    # for registering controller don't need any other dependencies, so filled None
    controllers: List[RegistrableApiController] = [
        OrderController(route_registry, settings, None, docs),  # type: ignore  # noqa
        OauthController(None, route_registry, settings, None, docs),  # type: ignore  # noqa
    ]
    for controller in controllers:
        controller.register()
