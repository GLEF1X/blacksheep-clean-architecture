import time
from typing import Awaitable, Callable

from blacksheep.messages import Request, Response
from loguru import logger


class LoggingMiddleware:
    async def __call__(
        self, request: Request, handler: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        # Request will be also logged by gunicorn or uvicorn, so I don't care about it

        handling_start_time = time.monotonic()
        response = await handler(request)
        elapsed_for_handling_http_request = time.monotonic() - handling_start_time
        logger.debug(
            'Request "{0} {1} " -> {2} processed for {3:.2f} seconds',
            request.method,
            request.url.path,
            response.status,
            elapsed_for_handling_http_request,
        )
        return response
