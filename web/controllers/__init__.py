from typing import List

from blacksheep.server.routing import RoutesRegistry
from dynaconf import LazySettings

from web.controllers.base import RegistrableApiController
from .order import OrderController


def install(route_registry: RoutesRegistry, settings: LazySettings) -> None:
    # for registering controller don't need any other dependencies, so filled None
    controllers: List[RegistrableApiController] = [
        OrderController(route_registry, settings, None)  # type: ignore  # noqa
    ]
    for controller in controllers:
        controller.register()
