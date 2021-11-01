from typing import List

from blacksheep.server.routing import RoutesRegistry
from dynaconf import LazySettings

from .controllers.base import RegistrableApiController
from .controllers.order import OrderController


def install(route_registry: RoutesRegistry, settings: LazySettings) -> None:
    controllers: List[RegistrableApiController] = [
        OrderController(route_registry, settings)
    ]
    for controller in controllers:
        controller.register()
