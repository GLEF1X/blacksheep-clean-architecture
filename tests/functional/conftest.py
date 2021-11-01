from __future__ import annotations

import asyncio

import pytest
from blacksheep.server import Application
from blacksheep.testing import TestClient
from dynaconf import LazySettings

from web.bootstrap import configure_application, get_settings


@pytest.fixture(scope="module")
def event_loop() -> asyncio.AbstractEventLoop:
    """
    This fixture fixes problem with scopes of fixture.

    Traceback: You tried to access the 'function' scoped fixture 'event_loop'
               with a 'module' scoped request object, involved factories
    """
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module")
def settings() -> LazySettings:
    return get_settings()


@pytest.mark.asyncio
@pytest.fixture(scope="module")
async def app(settings: LazySettings) -> Application:
    app = configure_application(settings)
    await app.start()
    yield app
    await app.stop()


@pytest.mark.usefixtures("start_application")
@pytest.fixture(scope="module")
def test_client(app: Application) -> TestClient:
    return TestClient(app)
