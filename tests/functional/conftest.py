from __future__ import annotations

import asyncio

import pytest
from blacksheep.server import Application
from blacksheep.testing import TestClient
from dynaconf import LazySettings

from tests.functional.stubs.insecure_app_builder import InsecureApplicationBuilder
from src.web import get_settings


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


@pytest.fixture(scope="module", autouse=True)
def set_test_settings(settings: LazySettings):
    settings.configure(FORCE_ENV_FOR_DYNACONF="testing")


@pytest.mark.asyncio
@pytest.fixture(scope="module")
async def insecure_app(settings: LazySettings) -> Application:
    app = InsecureApplicationBuilder(settings).build()
    await app.start()
    yield app
    await app.stop()


@pytest.fixture(scope="module")
def base_api_path(settings) -> str:
    return settings.web.api_path


@pytest.mark.usefixtures("start_application")
@pytest.fixture(scope="module")
def insecure_test_client(insecure_app: Application) -> TestClient:
    return TestClient(insecure_app)
