import dataclasses


@dataclasses.dataclass()
class TokenRequestDto:
    username: str
    password: str
