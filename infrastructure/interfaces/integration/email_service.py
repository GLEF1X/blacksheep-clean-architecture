from typing import Protocol


class EmailService(Protocol):
    async def send_mail(self, text: str) -> None:
        ...
