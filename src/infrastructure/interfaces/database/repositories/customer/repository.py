from typing import Protocol, List

from src.domain.entities.user import User


class UserRepository(Protocol):
    async def get_by_username(self, username: str) -> User: ...

    async def get_interested_customers(self) -> List[User]: ...

    async def update_password_hash(self, new_pwd_hash: str, user_id: int) -> None: ...
