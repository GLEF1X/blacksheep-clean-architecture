import dataclasses
from typing import Any, Dict, List

from src.application.application_services.dto.user_dto import UserDto


@dataclasses.dataclass()
class AuthCredentials:
    raw_payload: Dict[str, Any]
    jwt_token: str
    user: UserDto
    scopes: List[str]
    auth_mode: str = "JWT"

    def __hash__(self) -> int:
        return hash(self.jwt_token) + hash(self.auth_mode)
