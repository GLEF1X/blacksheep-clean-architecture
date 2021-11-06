import dataclasses

from entities.models.user import User


@dataclasses.dataclass()
class IssuedTokenDto:
    token: str
    issuer: User

    def generate_authorization_header(self, prefix: str = "Bearer") -> str:
        return f"{prefix} {self.token}"
