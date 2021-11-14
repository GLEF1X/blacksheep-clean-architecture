from typing import Protocol

from src.application.application_services.dto.auth_response import AuthCredentials


class AuthenticationService(Protocol):
    async def authenticate(self, authorization_header: str) -> AuthCredentials:
        ...
