from typing import Callable, Awaitable

import structlog.contextvars
from blacksheep import Response, Request

from src.web.util.blacksheep_context import context


class StructlogContextVarBindMiddleware:

    async def __call__(
            self, request: Request, next_handler: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        copied_context = context.data.copy()
        structlog.contextvars.bind_contextvars(**copied_context)
        try:
            return await next_handler(request)
        finally:
            structlog.contextvars.unbind_contextvars(*copied_context.keys())
