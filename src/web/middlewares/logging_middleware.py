import time
from typing import Awaitable, Callable

import structlog
from blacksheep.messages import Request, Response

from src.utils.type_casts import bytes_to_string


class LoggingMiddleware:
    def __init__(self):
        self._logger: structlog.stdlib.BoundLogger = structlog.get_logger()

    async def __call__(
            self, request: Request, next_handler: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        handling_start_time = time.monotonic()
        response = await next_handler(request)
        elapsed_for_handling_http_request = time.monotonic() - handling_start_time
        await self._logger.info(
            'Request "%s  %s" body: {%s} -> %s processed for %.2f seconds',
            request.method,
            bytes_to_string(request.url.path),
            await request.read(),
            response.status,
            elapsed_for_handling_http_request,
        )
        return response
