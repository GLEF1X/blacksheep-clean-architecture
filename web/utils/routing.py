from __future__ import annotations

from typing import Any, AnyStr

from blacksheep.server.routing import Router, Route
from blacksheep.utils import ensure_bytes


class APIRouter(Router):
    def __init__(self, prefix: str = "") -> None:
        super(APIRouter, self).__init__()
        self._prefix = prefix

    def add(self, method: str, pattern: AnyStr, handler: Any) -> None:
        path_with_prefix = self._prefix + pattern
        self.mark_handler(handler)
        method_name = ensure_bytes(method)
        new_route = Route(ensure_bytes(path_with_prefix), handler)
        self._check_duplicate(method_name, new_route)
        self.add_route(method_name, new_route)

    def include_router(self, router: APIRouter) -> None:
        for method, routes in router.routes.items():
            for route in routes:
                self.add_route(
                    method=method,
                    route=Route(self._prefix + route.mustache_pattern, route.handler),
                )
