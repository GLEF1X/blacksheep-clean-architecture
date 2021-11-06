from typing import Any, Protocol

from application.application_services.dto.auth_response import AuthCredentials
from application.application_services.dto.form_data import FormData
from application.application_services.dto.issued_token import IssuedTokenDto


class ContextInterface(Protocol):
    ...


class SecurityService(Protocol):
    async def issue_token(self, form_data: FormData) -> IssuedTokenDto:
        ...

    async def refresh_token(self, refresh_token: str) -> Any:
        ...

    async def authenticate(self, authorization_header: str) -> AuthCredentials:
        ...
