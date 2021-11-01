import pathlib

from blacksheep.server import Application
from blacksheep.server.openapi.v3 import OpenAPIHandler
from blacksheep.server.routing import RoutesRegistry
from dynaconf import Dynaconf, LazySettings
from openapidocs.v3 import Info

from entities.domain_services.implementation.order_service import OrderServiceImpl
from entities.domain_services.interfaces.order_service import OrderServiceInterface
from infrastructure.implementation.delivery.delivery_service import DeliveryServiceImpl
from web import api
from web.utils.gunicorn_app import StandaloneApplication, number_of_workers
from web.utils.routing import APIRouter

BASE_DIR = pathlib.Path(__name__).resolve().parent.parent


class ApplicationWithCustomRouter(Application):
    router: APIRouter


def get_settings() -> LazySettings:
    return Dynaconf(
        settings_files=['settings.toml', '.secrets.toml'],
        redis=True,
        preload=[BASE_DIR / "settings.toml"],
        environments=["development", "production", "testing"],
        load_dotenv=False,
    )


def configure_application(settings: LazySettings) -> Application:
    controllers_router = RoutesRegistry()
    application = ApplicationWithCustomRouter()
    application.controllers_router = controllers_router
    _setup_dependency_injection(application, settings)
    _setup_routes(application, settings)
    return application


def _setup_dependency_injection(application: Application, settings: LazySettings) -> None:
    application.services.add_instance(application.controllers_router, RoutesRegistry)
    application.services.add_instance(
        OrderServiceImpl(DeliveryServiceImpl()),
        OrderServiceInterface
    )
    application.services.add_instance(settings, LazySettings)


def _setup_routes(application: ApplicationWithCustomRouter, settings: LazySettings) -> None:
    api.v1.install(application.controllers_router, settings)
    docs = OpenAPIHandler(
        info=Info(
            title=settings.server.docs.title,
            version=settings.server.docs.version
        ),
        ui_path=settings.server.docs.path,
        json_spec_path=settings.server.docs.json_spec_path,
        yaml_spec_path=settings.server.docs.yaml_spec_path,
    )
    docs.bind_app(application)


def run() -> None:
    settings = get_settings()
    application = configure_application(settings)
    options = {
        'bind': '%s:%s' % (settings.server.host, settings.server.port),
        'workers': number_of_workers(),
        'worker_class': 'uvicorn.workers.UvicornWorker'
    }
    gunicorn_app = StandaloneApplication(application, options)
    gunicorn_app.run()


if __name__ == '__main__':
    run()
