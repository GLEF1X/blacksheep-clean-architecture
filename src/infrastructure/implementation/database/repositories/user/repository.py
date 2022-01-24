from typing import cast, List

from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.user import User
from src.infrastructure.implementation.database.orm.models import UserModel
from src.infrastructure.implementation.database.repositories.crud_repository import SQLAlchemyCRUDRepository


class UserRepositoryImpl:

    def __init__(self, session: AsyncSession):
        self._crud_repository = SQLAlchemyCRUDRepository(session, model=UserModel)

    async def get_by_username(self, username: str) -> User:
        customer = await self._crud_repository.get_one(
            UserModel.username == username
        )
        return cast(User, customer)

    async def get_interested_customers(self) -> List[User]:
        customers = await self._crud_repository.get_all(
            func.count(UserModel.orders) > 2
        )
        return cast(List[User], customers)

    async def update_password_hash(self, new_pwd_hash: str, user_id: int) -> None:
        await self._crud_repository.update(UserModel.id == user_id, password_hash=new_pwd_hash)
