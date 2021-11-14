import dataclasses
import time
from datetime import datetime
from typing import Dict, Any, List

from src.application.application_services.dto.auth_response import AuthCredentials
from src.application.application_services.dto.user_dto import UserDto
from src.application.application_services.implementation.security.jwt.exceptions import (
    APITokenOmittedException,
    UserNotRegistered,
    TokenExpiredException,
)
from src.application.application_services.interfaces.security.jwt.authentication_service import (
    AuthenticationService,
)
from src.application.application_services.interfaces.security.jwt.decoder import (
    TokenDecoder,
)
from src.entities.models.user import User
from src.infrastructure.interfaces.database.data_access.repository import (
    AbstractRepository,
)


@dataclasses.dataclass()
class JWTTokenPayload:
    username: str
    expire_at: int
    full: Dict[Any, Any]
    raw_jwt_token: str
    scopes: List[str]


class JWTAuthenticationService(AuthenticationService):
    def __init__(
        self, token_decoder: TokenDecoder, user_repository: AbstractRepository[User]
    ):
        self._token_decoder = token_decoder
        self._user_repository = user_repository

    async def authenticate(self, authorization_header: str) -> AuthCredentials:
        if not authorization_header:
            raise APITokenOmittedException(f"Authorization header is empty.")
        if not authorization_header.startswith("Bearer "):
            raise APITokenOmittedException(f"Authorization method is not Bearer.")
        payload = self._extract_jwt_payload(authorization_header)
        if payload.expire_at < time.mktime(datetime.utcnow().utctimetuple()):
            raise TokenExpiredException("API access token was expired!")

        user = await self._user_repository.get_one(
            self._user_repository.model.username == payload.username
        )
        if user is None:
            raise UserNotRegistered(
                f"JWT authentication failed. User with username={payload.username} not found."
            )

        return AuthCredentials(
            raw_payload=payload.full,
            jwt_token=payload.raw_jwt_token,
            user=UserDto(
                id=user.id,
                first_name=user.first_name,
                last_name=user.last_name,
                username=user.username,
                email=user.email,
            ),
            scopes=payload.scopes,
        )

    def _extract_jwt_payload(self, authorization_header: str) -> JWTTokenPayload:
        jwt_token = authorization_header[7:]
        decoded_payload = self._token_decoder.decode_token(jwt_token)
        username: str = decoded_payload["sub"]
        token_expire_at = decoded_payload["exp"]
        scopes: List[str] = decoded_payload["scopes"]

        return JWTTokenPayload(
            username=username,
            expire_at=token_expire_at,
            full=decoded_payload,
            raw_jwt_token=jwt_token,
            scopes=scopes,
        )
