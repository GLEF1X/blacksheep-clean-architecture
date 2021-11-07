from datetime import datetime, timedelta
from typing import Any, Dict, Final

import jwt

from application.application_services.dto.auth_response import AuthCredentials
from application.application_services.dto.form_data import FormData
from application.application_services.dto.issued_token import IssuedTokenDto
from application.application_services.dto.user_dto import UserDto
from application.application_services.implementation.security.jwt.exceptions import (
    APITokenOmittedException,
    JWTSubNotExists,
    MalformedAPIToken,
    UserNotRegistered,
    IncorrectPassword,
)
from application.application_services.interfaces.security.jwt.security_service import (
    SecurityService,
)
from infrastructure.implementation.database.orm.tables import UserModel
from infrastructure.interfaces.database.data_access.repository import AbstractRepository
from utils.security.password_hashing import is_password_verified

DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES: Final[float] = 30


def _get_bearer_token_from_header(authorization_header_value: str) -> str:
    return authorization_header_value[7:]


class SecurityServiceImpl(SecurityService):
    """
    Tries to identify a user from a JWT Bearer access token.
    """

    def __init__(
            self,
            user_repository: AbstractRepository[UserModel],
            secret_key: str,
            encoding_algorithm: str,
            token_expires_in_minutes: float = DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES,
    ) -> None:
        self._user_repository = user_repository
        self._secret_key = secret_key
        self._encoding_algorithm = encoding_algorithm
        self._token_expires = timedelta(minutes=token_expires_in_minutes)

    async def issue_token(self, form_data: FormData) -> IssuedTokenDto:
        issuer = await self._user_repository.get_one(
            self._user_repository.model.username == form_data.username
        )
        if issuer is None:
            raise UserNotRegistered(f"User with username={form_data.username} not found.")
        if not is_password_verified(form_data.password, issuer.hashed_password):
            raise IncorrectPassword("Password is incorrect! Try again.")
        return IssuedTokenDto(
            api_token=self._generate_jwt_token(form_data),
            issuer=UserDto(
                id=issuer.id, first_name=issuer.first_name, last_name=issuer.last_name,
                username=issuer.username, email=issuer.email
            )
        )

    async def authenticate(self, authorization_header: str) -> AuthCredentials:
        if not authorization_header:
            raise APITokenOmittedException(f"Authorization header is empty.")
        if not authorization_header.startswith("Bearer "):
            raise APITokenOmittedException(f"Authorization method is not Bearer.")

        jwt_token = authorization_header[7:]
        decoded_payload = self._decode_jwt_token(jwt_token)
        try:
            subject: str = decoded_payload["sub"]
        except KeyError:
            raise JWTSubNotExists('"sub" in encoded jwt token does not exists.')

        user = await self._user_repository.get_one(self._user_repository.model.username == subject)
        if user is None:
            raise UserNotRegistered(
                f"JWT authentication failed. User with username={subject} not found."
            )

        return AuthCredentials(payload=decoded_payload, jwt_token=jwt_token, user=user)

    async def refresh_token(self, refresh_token: str) -> Any:
        raise NotImplementedError

    def _decode_jwt_token(self, token: str) -> Dict[str, Any]:
        try:
            return jwt.decode(
                jwt=token, key=self._secret_key, algorithms=[self._encoding_algorithm]
            )
        except jwt.PyJWTError:
            raise MalformedAPIToken("API token is invalid.")

    def _generate_jwt_token(self, form_data: FormData, **kwargs: Any) -> str:
        payload = {
            "sub": form_data.username,
            "exp": datetime.utcnow() + self._token_expires,
            **kwargs,
        }
        filtered_payload = {k: v for k, v in payload.items() if v is not None}
        return jwt.encode(filtered_payload, self._secret_key, self._encoding_algorithm)
