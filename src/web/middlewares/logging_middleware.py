import logging
import time
from typing import Awaitable, Callable

from blacksheep.messages import Request, Response

from src.utils.type_casts import bytes_to_string


class LoggingMiddleware:
    def __init__(self):
        self._logger = logging.getLogger("web")

    async def __call__(
        self, request: Request, handler: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        # Request will be also logged by gunicorn or uvicorn, so I don't care about it

        handling_start_time = time.monotonic()
        response = await handler(request)
        elapsed_for_handling_http_request = time.monotonic() - handling_start_time
        self._logger.debug(
            'Request "%s  %s" -> %s processed for %d seconds',
            request.method,
            bytes_to_string(request.url.path),
            response.status,
            elapsed_for_handling_http_request,
        )
        return response
