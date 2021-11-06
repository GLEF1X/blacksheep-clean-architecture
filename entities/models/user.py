import dataclasses
from typing import Optional


@dataclasses.dataclass()
class User:
    first_name: str
    last_name: str
    username: str
    password_hash: str
    email: Optional[str] = None
    id: int = dataclasses.field(init=False)

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
