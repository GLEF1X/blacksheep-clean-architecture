import dataclasses

from application.application_services.dto.user_dto import UserDto


@dataclasses.dataclass()
class IssuedTokenDto:
    api_token: str
    issuer: UserDto

    def generate_authorization_header(self, prefix: str = "Bearer") -> str:
        return f"{prefix} {self.api_token}"
