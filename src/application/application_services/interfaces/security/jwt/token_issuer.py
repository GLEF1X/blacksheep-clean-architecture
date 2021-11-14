from typing import Protocol

from src.application.application_services.dto.form_data import FormData
from src.application.application_services.dto.issued_token import IssuedTokenDto


class TokenIssuer(Protocol):
    async def issue_token(self, form_data: FormData) -> IssuedTokenDto:
        pass
