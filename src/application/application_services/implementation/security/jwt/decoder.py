from typing import Any, Dict

import jwt

from src.application.application_services.implementation.security.jwt.exceptions import (
    MalformedAPIToken,
)
from src.application.application_services.interfaces.security.jwt.decoder import (
    TokenDecoder,
)


class JWTTokenDecoder(TokenDecoder):
    def __init__(self, secret_key: str, encoding_algorithm: str):
        self._secret_key = secret_key
        self._encoding_algorithm = encoding_algorithm

    def decode_token(self, token: str) -> Dict[str, Any]:
        try:
            return jwt.decode(
                jwt=token, key=self._secret_key, algorithms=[self._encoding_algorithm]
            )
        except jwt.PyJWTError:
            raise MalformedAPIToken("API token is invalid.")
