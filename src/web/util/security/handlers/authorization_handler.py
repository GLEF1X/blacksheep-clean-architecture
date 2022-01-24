from typing import Optional

from blacksheep import Request
from guardpost import Identity
from guardpost.asynchronous.authentication import AuthenticationHandler

from src.application.application_services.interfaces.security.jwt.authentication_service import (
    AuthenticationService,
)
from src.utils.exceptions import ProcessError


class SimpleAuthHandler(AuthenticationHandler):
    def __init__(self, authentication_service: AuthenticationService):
        self._authentication_service = authentication_service

    async def authenticate(self, context: Request) -> Optional[Identity]:
        auth_header = context.headers.get_first(b"Authorization")
        context.identity = None
        if auth_header is None:
            return None
        string_auth_header = str(auth_header, "utf-8")
        try:
            auth_credentials = await self._authentication_service.authenticate(string_auth_header)
        except ProcessError:
            return None
        identity = Identity(auth_credentials.raw_payload, auth_credentials.auth_mode)
        context.identity = identity
        return identity

    @property
    def scheme(self) -> str:
        return "authorization"
