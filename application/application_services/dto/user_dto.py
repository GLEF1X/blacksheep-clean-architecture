import dataclasses
from typing import Optional


@dataclasses.dataclass()
class UserDto:
    id: int
    first_name: str
    last_name: str
    username: str
    email: Optional[str] = None
