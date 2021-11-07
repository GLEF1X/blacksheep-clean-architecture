from typing import Optional

from blacksheep import Request
from guardpost import Identity
from guardpost.asynchronous.authentication import AuthenticationHandler

from application.application_services.implementation.security.jwt.exceptions import (
    SecurityException,
)
from application.application_services.interfaces.security.jwt.security_service import (
    SecurityService,
)


class SimpleAuthHandler(AuthenticationHandler):
    def __init__(self, security_service: SecurityService):
        self._security_service = security_service

    async def authenticate(self, context: Request) -> Optional[Identity]:
        auth_header = context.headers.get_first(b"Authorization")
        context.identity = None
        if auth_header is None:
            return None
        string_auth_header = str(auth_header, "utf-8")
        try:
            auth_credentials = await self._security_service.authenticate(
                string_auth_header
            )
        except SecurityException:
            return None
        identity = Identity(auth_credentials.payload, auth_credentials.auth_mode)
        context.identity = identity
        return identity
