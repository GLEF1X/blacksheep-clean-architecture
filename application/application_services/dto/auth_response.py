import dataclasses
from typing import Any, Dict

from infrastructure.implementation.database.orm.tables import UserModel


@dataclasses.dataclass()
class AuthCredentials:
    payload: Dict[str, Any]
    jwt_token: str
    user: UserModel
    auth_mode: str = "JWT"
