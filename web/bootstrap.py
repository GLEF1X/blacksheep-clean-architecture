import pathlib

import uvicorn
from blacksheep.server import Application
from blacksheep.server.openapi.v3 import OpenAPIHandler
from blacksheep.server.routing import RoutesRegistry
from dynaconf import Dynaconf, LazySettings
from openapidocs.v3 import Info

from utils.routing import APIRouter
from web import api

BASE_DIR = pathlib.Path(__name__).resolve().parent.parent


class ApplicationWithCustomRouter(Application):
    router: APIRouter


def configure_application() -> Application:
    settings = Dynaconf(
        settings_files=['settings.toml', '.secrets.toml'],
        redis=True,
        preload=[BASE_DIR / "settings.toml"],
        environments=["development", "production", "testing"],
        load_dotenv=False,
    )
    controllers_router = RoutesRegistry()
    application = ApplicationWithCustomRouter()
    application.controllers_router = controllers_router
    _setup_dependency_injection(application, settings)
    _setup_routes(application, settings)
    return application


def _setup_dependency_injection(application: Application, settings: LazySettings) -> None:
    application.services.add_instance(application.controllers_router, RoutesRegistry)


def _setup_routes(application: ApplicationWithCustomRouter, settings: LazySettings) -> None:
    api.v1.install(application.controllers_router)
    docs = OpenAPIHandler(info=Info(title=settings.docs.title, version=settings.docs.version))
    docs.bind_app(application)


app = configure_application()

if __name__ == '__main__':
    # not for production
    uvicorn.run(app)
