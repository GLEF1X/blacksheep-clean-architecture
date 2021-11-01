import pathlib

from blacksheep.server import Application
from blacksheep.server.openapi.v3 import OpenAPIHandler
from blacksheep.server.routing import RoutesRegistry, Route
from dynaconf import Dynaconf, LazySettings
from openapidocs.v3 import Info
from rodi import ServiceLifeStyle
from entities.domain_services.implementation.order_service import OrderServiceImpl
from entities.domain_services.interfaces.order_service import OrderServiceInterface
from infrastructure.implementation.delivery.delivery_service import DeliveryServiceImpl
from web import api
from web.utils.gunicorn_app import StandaloneApplication, number_of_workers
from web.utils.routing import PrefixedRouter

BASE_DIR = pathlib.Path(__name__).resolve().parent.parent


class ApplicationWithPrefixedRouter(Application):
    router: PrefixedRouter


def get_settings() -> LazySettings:
    return Dynaconf(
        settings_files=["settings.toml", ".secrets.toml"],
        redis=True,
        preload=[BASE_DIR / "settings.toml"],
        environments=["development", "production", "testing"],
        load_dotenv=False,
        auto_cast=True,
    )


def configure_application(settings: LazySettings) -> Application:
    controllers_router = RoutesRegistry()
    application = ApplicationWithPrefixedRouter(
        debug=settings.web.debug, show_error_details=settings.web.show_error_details
    )
    application.controllers_router = controllers_router
    _setup_dependency_injection(application, settings)
    _setup_routes(application, settings)
    return application


def _setup_dependency_injection(
    application: Application, settings: LazySettings
) -> None:
    application.services.add_instance(application.controllers_router, RoutesRegistry)
    application.services.add_instance(settings, LazySettings)

    # domain services
    application.services.register_factory(
        lambda: OrderServiceImpl(DeliveryServiceImpl()),
        life_style=ServiceLifeStyle.SCOPED,
        return_type=OrderServiceInterface
    )


def _setup_routes(
    application: ApplicationWithPrefixedRouter, settings: LazySettings
) -> None:
    api.v1.install(application.controllers_router, settings)
    docs = OpenAPIHandler(
        info=Info(title=settings.web.docs.title, version=settings.web.docs.version),
        ui_path=settings.web.docs.path,
        json_spec_path=settings.web.docs.json_spec_path,
        yaml_spec_path=settings.web.docs.yaml_spec_path,
    )
    docs.bind_app(application)


def run() -> None:
    settings = get_settings()
    application = configure_application(settings)
    options = {
        "bind": "%s:%s" % (settings.web.host, settings.web.port),
        "workers": number_of_workers(),
        "worker_class": "uvicorn.workers.UvicornWorker",
    }
    gunicorn_app = StandaloneApplication(application, options)
    gunicorn_app.run()


if __name__ == "__main__":
    run()
