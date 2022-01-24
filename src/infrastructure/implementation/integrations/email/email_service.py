import asyncio


class EmailServiceImpl:
    async def send_mail(self, text: str) -> None:
        # mock realization
        await asyncio.sleep(.5)
