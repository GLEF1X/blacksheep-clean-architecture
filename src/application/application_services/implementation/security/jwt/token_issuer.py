from datetime import datetime, timedelta
from typing import Any, Final, Dict

import jwt

from src.application.application_services.dto.form_data import FormData
from src.application.application_services.dto.issued_token import IssuedTokenDto
from src.application.application_services.dto.user_dto import UserDto
from src.application.application_services.implementation.security.jwt.exceptions import (
    UserNotRegistered,
    IncorrectPassword,
    InvalidScopeName,
)
from src.application.application_services.interfaces.security.jwt.token_issuer import (
    TokenIssuer,
)
from src.entities.models.user import User
from src.infrastructure.interfaces.database.data_access.repository import (
    AbstractRepository,
)
from src.utils.password_hashing import is_password_verified

DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES: Final[float] = 30


def _get_bearer_token_from_header(authorization_header_value: str) -> str:
    return authorization_header_value[7:]


class JWTTokenIssuer(TokenIssuer):
    def __init__(
        self,
        user_repository: AbstractRepository[User],
        secret_key: str,
        encoding_algorithm: str,
        token_expires_in_minutes: float = DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES,
    ):
        self._token_expires = timedelta(minutes=token_expires_in_minutes)
        self._user_repository = user_repository
        self._secret_key = secret_key
        self._encoding_algorithm = encoding_algorithm

    async def issue_token(self, form_data: FormData) -> IssuedTokenDto:
        issuer = await self._user_repository.get_one(
            self._user_repository.model.username == form_data.username
        )
        if issuer is None:
            raise UserNotRegistered(
                f"User with username={form_data.username} not found."
            )
        if not is_password_verified(form_data.password, issuer.hashed_password):
            raise IncorrectPassword("Password is incorrect! Try again.")
        return IssuedTokenDto(
            api_token=self._generate_jwt_token(form_data),
            issuer=UserDto(
                id=issuer.id,
                first_name=issuer.first_name,
                last_name=issuer.last_name,
                username=issuer.username,
                email=issuer.email,
            ),
        )

    def _generate_jwt_token(self, form_data: FormData, **kwargs: Any) -> str:
        payload = {
            "sub": form_data.username,
            "exp": datetime.utcnow() + self._token_expires,
            "scopes": form_data.scopes,
            **kwargs,
        }
        filtered_payload = {k: v for k, v in payload.items() if v is not None}
        return jwt.encode(filtered_payload, self._secret_key, self._encoding_algorithm)
