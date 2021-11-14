import dataclasses

from src.application.application_services.dto.user_dto import UserDto


@dataclasses.dataclass()
class IssuedTokenDto:
    api_token: str
    issuer: UserDto
