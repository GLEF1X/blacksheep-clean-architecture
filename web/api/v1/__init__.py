from blacksheep.server.routing import RoutesRegistry

from .controllers.order import OrderController


def install(route_registry: RoutesRegistry) -> None:
    OrderController(router=route_registry).register()
