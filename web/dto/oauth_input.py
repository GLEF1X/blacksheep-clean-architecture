import dataclasses


@dataclasses.dataclass()
class OauthFormInput:
    username: str
    password: str
