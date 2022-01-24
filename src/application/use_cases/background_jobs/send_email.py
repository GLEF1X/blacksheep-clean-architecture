import asyncio

from src.infrastructure.interfaces.database.repositories.customer.repository import UserRepository
from src.infrastructure.interfaces.integration.email.email_service import EmailService


async def send_email_to_interested_customers(customer_repository: UserRepository,
                                             email_client: EmailService):
    customers = await customer_repository.get_interested_customers()
    tasks = [
        email_client.send_mail(text="Thank you for buying from us")
        for _ in customers
    ]
    await asyncio.gather(*tasks)
