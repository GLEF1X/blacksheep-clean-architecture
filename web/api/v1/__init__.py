from blacksheep.server.routing import RoutesRegistry
from dynaconf import LazySettings

from .controllers.order import OrderController


def install(route_registry: RoutesRegistry, settings: LazySettings) -> None:
    OrderController(route_registry, settings).register()
