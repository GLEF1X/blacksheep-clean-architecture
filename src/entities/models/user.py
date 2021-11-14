import dataclasses
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from src.entities.models.order import Order


@dataclasses.dataclass()
class User:
    first_name: str
    last_name: str
    username: str
    hashed_password: str
    orders: List["Order"]
    email: Optional[str] = None
    id: int = dataclasses.field(init=False)

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
