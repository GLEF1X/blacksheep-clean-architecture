import asyncio

from sqlalchemy import func

from src.entities.models.user import User
from src.infrastructure.implementation.database.orm.tables import UserModel
from src.infrastructure.interfaces.database.data_access.repository import AbstractRepository
from src.infrastructure.interfaces.email.email_client import EmailClient


async def send_email_to_interested_users(user_repository: AbstractRepository[User],
                                         email_client: EmailClient):
    users = await user_repository.get_all(func.count(UserModel.orders) >= 2)
    tasks = [
        email_client.send_message(text="Thank you for buying from us")
        for _ in users
    ]
    await asyncio.gather(*tasks)
