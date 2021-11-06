import dataclasses


@dataclasses.dataclass()
class FormData:
    username: str
    password: str
