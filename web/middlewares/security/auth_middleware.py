from typing import Awaitable, Callable

from blacksheep.messages import Request, Response
from blacksheep.server.responses import unauthorized

from application.application_services.implementation.security.jwt.exceptions import (
    SecurityException,
)
from application.application_services.interfaces.security.jwt.security_service import (
    SecurityService,
)
from web.constants import SKIP_AUTH_KEY

DEFAULT_OMIT_AUTHENTICATION = ("docs", "openapi.json", "openapi.yaml")


class AuthenticationMiddleware:
    def __init__(self, security_service: SecurityService) -> None:
        self._security_service = security_service

    async def __call__(
        self, request: Request, handler: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        path = str(request.url.path, "utf-8")
        if any(omitted_path in path for omitted_path in DEFAULT_OMIT_AUTHENTICATION):
            return await handler(request)
        if getattr(handler, SKIP_AUTH_KEY, False) is True:
            return await handler(request)
        auth_header = str(request.headers.get_first(b"Authorization"))
        try:
            auth_credentials = await self._security_service.authenticate(auth_header)
        except SecurityException as ex:
            return unauthorized(message=ex.message)

        return await handler(request)
