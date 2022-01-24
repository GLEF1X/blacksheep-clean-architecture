import dataclasses
from typing import Optional, List, TYPE_CHECKING

from src.domain.entities.base import Entity

if TYPE_CHECKING:
    from src.domain.entities.order import Order


@dataclasses.dataclass()
class User(Entity):
    first_name: str
    last_name: str
    username: str
    password_hash: str
    orders: List["Order"]
    email: Optional[str] = None

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
