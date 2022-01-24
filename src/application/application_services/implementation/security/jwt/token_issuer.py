from datetime import datetime, timedelta
from typing import Any, Final

import jwt
from argon2.exceptions import VerificationError

from src.application.application_services.dto.form_data import FormData
from src.application.application_services.dto.issued_token import IssuedTokenDto
from src.application.application_services.dto.user_dto import UserDto
from src.application.application_services.implementation.security.jwt.exceptions import (
    SecurityExceptionCatalog,
)
from src.application.application_services.interfaces.security.jwt.token_issuer import (
    TokenIssuer,
)
from src.infrastructure.interfaces.database.repositories.customer.repository import UserRepository
from src.utils.password_hashing.protocol import PasswordHasherProto

DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES: Final[float] = 30


def _extract_bearer_token_from_header(authorization_header_value: str) -> str:
    return authorization_header_value[7:]


class JWTTokenIssuer(TokenIssuer):
    def __init__(
            self,
            user_repository: UserRepository,
            secret_key: str,
            encoding_algorithm: str,
            password_hasher: PasswordHasherProto,
            token_expires_in_minutes: float = DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES
    ):
        self._token_expires = timedelta(minutes=token_expires_in_minutes)
        self._user_repository = user_repository
        self._secret_key = secret_key
        self._encoding_algorithm = encoding_algorithm
        self._password_hasher = password_hasher

    async def issue_token(self, form_data: FormData) -> IssuedTokenDto:
        user = await self._user_repository.get_by_username(form_data.username)
        if user is None:
            raise SecurityExceptionCatalog.USER_NOT_REGISTERED.with_params(username=form_data.username)
        if not self._is_password_trusted(user.password_hash, form_data.password):
            raise SecurityExceptionCatalog.INCORRECT_PASSWORD.with_params(username=form_data.username)

        if self._password_hasher.check_needs_rehash(user.password_hash):
            await self._user_repository.update_password_hash(
                new_pwd_hash=self._password_hasher.hash(form_data.password),
                user_id=user.id
            )

        return IssuedTokenDto(
            api_token=self._generate_jwt_token(form_data),
            issuer=UserDto(
                id=user.id,
                first_name=user.first_name,
                last_name=user.last_name,
                username=user.username,
                email=user.email,
            ),
        )

    def _is_password_trusted(self, password_hash: str, plain_password: str) -> bool:
        try:
            return self._password_hasher.verify(password_hash, plain_password)
        except VerificationError:
            raise SecurityExceptionCatalog.INCORRECT_PASSWORD.with_params(pwd_hash=password_hash,
                                                                          plain_password=plain_password)

    def _generate_jwt_token(self, form_data: FormData, **kwargs: Any) -> str:
        payload = {
            "sub": form_data.username,
            "exp": datetime.utcnow() + self._token_expires,
            "scopes": form_data.scopes,
            **kwargs,
        }
        filtered_payload = {k: v for k, v in payload.items() if v is not None}
        return jwt.encode(filtered_payload, self._secret_key, self._encoding_algorithm)
