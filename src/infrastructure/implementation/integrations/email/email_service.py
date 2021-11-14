import asyncio

from src.infrastructure.interfaces.integration.email.email_service import EmailService


class EmailServiceImpl(EmailService):
    async def send_mail(self, text: str) -> None:
        # mock realization
        await asyncio.sleep(.5)
