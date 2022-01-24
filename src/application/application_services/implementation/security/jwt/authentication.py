import dataclasses
import time
from datetime import datetime
from typing import Dict, Any, List

from src.application.application_services.dto.auth_response import AuthCredentials
from src.application.application_services.dto.user_dto import UserDto
from src.application.application_services.implementation.security.jwt.exceptions import (
    SecurityExceptionCatalog,
)
from src.application.application_services.interfaces.security.jwt.decoder import (
    TokenDecoder,
)
from src.infrastructure.interfaces.database.repositories.customer.repository import UserRepository


@dataclasses.dataclass()
class JWTTokenPayload:
    username: str
    expire_at: int
    full: Dict[Any, Any]
    raw_jwt_token: str
    scopes: List[str]


class JWTAuthenticationService:
    def __init__(
            self, token_decoder: TokenDecoder, customer_repository: UserRepository
    ):
        self._token_decoder = token_decoder
        self._customer_repository = customer_repository

    async def authenticate(self, authorization_header: str) -> AuthCredentials:
        if not authorization_header:
            raise SecurityExceptionCatalog.MISSING_API_TOKEN
        if not authorization_header.startswith("Bearer "):
            raise SecurityExceptionCatalog.INVALID_AUTHORIZATION_METHOD.with_params(required_schema="Bearer")
        payload = self._extract_jwt_payload(authorization_header)
        if payload.expire_at < time.mktime(datetime.utcnow().utctimetuple()):
            raise SecurityExceptionCatalog.TOKEN_EXPIRED

        customer = await self._customer_repository.get_by_username(payload.username)
        if customer is None:
            raise SecurityExceptionCatalog.USER_NOT_REGISTERED.with_params(username=payload.username)

        return AuthCredentials(
            raw_payload=payload.full,
            jwt_token=payload.raw_jwt_token,
            user=UserDto(
                id=customer.id,
                first_name=customer.first_name,
                last_name=customer.last_name,
                username=customer.username,
                email=customer.email,
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
