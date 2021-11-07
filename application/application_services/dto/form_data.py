import dataclasses
from typing import List


@dataclasses.dataclass()
class FormData:
    username: str
    password: str
    scopes: List[str]
