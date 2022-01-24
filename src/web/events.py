from blacksheep.server import Application
from sqlalchemy.ext.asyncio import AsyncEngine


async def on_startup(application: Application) -> None:
    pass


async def on_shutdown(application: Application) -> None:
    engine = application.services.build_provider().get(AsyncEngine, default=None)
    if engine is None:
        return None
    await engine.dispose()
