import pathlib
from typing import Any

from blacksheep.server import Application
from blacksheep.server.openapi.v3 import OpenAPIHandler
from blacksheep.server.routing import RoutesRegistry
from blacksheep_prometheus import metrics, PrometheusMiddleware
from dynaconf import Dynaconf, LazySettings
from guardpost import Policy
from guardpost.common import AuthenticatedRequirement
from openapidocs.v3 import Info
from rodi import ServiceLifeStyle
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import AsyncAdaptedQueuePool

from application.application_services.implementation.security.jwt.security_service import (
    SecurityServiceImpl,
)
from application.application_services.interfaces.security.jwt.security_service import (
    SecurityService,
)
from application.cqrs_lib import MediatorInterface, MediatorImpl
from application.use_cases.order.commands.create_order.command import CreateOrderCommand
from application.use_cases.order.commands.create_order.handler import CreateOrderHandler
from application.use_cases.order.queries.get_order_by_id.handler import GetOrderByIdHandler
from application.use_cases.order.queries.get_order_by_id.query import GetOrderByIdQuery
from application.use_cases.validation.validation_decorator import ValidationQueryHandlerDecorator
from entities.domain_services.implementation.order_service import OrderServiceImpl
from infrastructure.implementation.database.data_access.repository import (
    SQLAlchemyRepository,
)
from infrastructure.implementation.database.data_access.unit_of_work import SQLAlchemyUnitOfWork
from infrastructure.implementation.database.orm.tables import UserModel
from infrastructure.implementation.delivery.delivery_service import DeliveryServiceImpl
from utils.logging.gunicorn import (
    StubbedGunicornLogger,
    configure_gunicorn_logger_adapter,
)
from web.api import controllers
from web.events import on_shutdown, on_startup
from web.middlewares.logging_middleware import LoggingMiddleware
from web.security.handlers.authorization_handler import SimpleAuthHandler
from web.web_utils.gunicorn_app import StandaloneApplication, number_of_workers
from web.web_utils.routing import PrefixedRouter

BASE_DIR = pathlib.Path(__name__).resolve().parent.parent


class ApplicationWithPrefixedRouter(Application):
    router: PrefixedRouter


def _create_mediator(pool: sessionmaker) -> MediatorInterface:
    session = pool()
    repository: SQLAlchemyRepository[Any] = SQLAlchemyRepository(session)
    uow = SQLAlchemyUnitOfWork(session)
    order_domain_service = OrderServiceImpl(DeliveryServiceImpl())
    return MediatorImpl(
        query_handlers={
            GetOrderByIdQuery: [
                GetOrderByIdHandler(repository, order_domain_service, uow)
            ]
        },
        command_handlers={
            CreateOrderCommand: ValidationQueryHandlerDecorator(
                CreateOrderHandler(repository, uow)
            )
        },
    )


class ApplicationBuilder:

    def __init__(self, settings: LazySettings):
        self._controller_router = RoutesRegistry()
        self._settings = settings
        self._application = ApplicationWithPrefixedRouter(
            debug=settings.web.is_production,
            show_error_details=settings.web.show_error_details,
        )
        self._application.controllers_router = self._controller_router

    def build(self) -> Application:
        self._setup_events()
        self._setup_dependency_injection()
        self._setup_routes()
        self._setup_middlewares()
        # Setup of security must be executed exactly after DI installation, because it rely
        # that application services will contain provider of SecurityService
        self._setup_security()
        self._setup_metrics()
        return self._application

    def _setup_events(self) -> None:
        self._application.on_start += on_startup
        self._application.on_stop += on_shutdown

    def _setup_middlewares(self) -> None:
        self._application.middlewares.append(LoggingMiddleware())

    def _setup_metrics(self) -> None:
        self._application.middlewares.append(PrometheusMiddleware())
        self._application.router.add_get("/metrics", metrics)

    def _setup_security(self):
        security_service = self._application.services.build_provider().get(SecurityService)
        self._application.use_authentication().add(SimpleAuthHandler(security_service))
        self._application.use_authorization().add(
            Policy("authenticated", AuthenticatedRequirement())
        )

    def _setup_dependency_injection(self) -> None:
        # controller dependencies
        self._application.services.add_instance(self._controller_router, RoutesRegistry)
        self._application.services.add_instance(self._settings, LazySettings)

        # database
        engine = create_async_engine(
            url=make_url(self._settings.db.connection_uri),
            future=True,
            query_cache_size=1200,
            pool_size=100,
            max_overflow=200,
            poolclass=AsyncAdaptedQueuePool,
        )
        session_pool = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

        # mediator
        self._application.services.register_factory(
            lambda: _create_mediator(session_pool),
            MediatorInterface,
            ServiceLifeStyle.SCOPED,
        )

        # application services
        user_repository: SQLAlchemyRepository[UserModel] = SQLAlchemyRepository(
            session_pool, UserModel
        )
        security_service = SecurityServiceImpl(
            user_repository=user_repository,
            secret_key=self._settings.web.auth.secret_key,
            encoding_algorithm=self._settings.web.auth.algorithm,
        )
        self._application.services.add_instance(security_service, SecurityService)

        # OpenAPI
        docs = OpenAPIHandler(
            info=Info(title=self._settings.web.docs.title, version=self._settings.web.docs.version),
            ui_path=self._settings.web.docs.path,
            json_spec_path=self._settings.web.docs.json_spec_path,
            yaml_spec_path=self._settings.web.docs.yaml_spec_path,
        )
        self._application.services.add_instance(docs, OpenAPIHandler)

    def _setup_routes(self) -> None:
        docs = self._application.services.build_provider().get(OpenAPIHandler)
        controllers.install(self._application.controllers_router, self._settings, docs)
        current_api_version = self._settings.web.api_version
        # include only endpoints whose path starts with "/api/"
        docs.include = lambda path, _: path.startswith(f"/api/{current_api_version}/")
        docs.bind_app(self._application)


def get_settings() -> LazySettings:
    return Dynaconf(
        settings_files=["settings.toml", ".secrets.toml"],
        redis=True,
        preload=[BASE_DIR / "settings.toml"],
        environments=["development", "production", "testing"],
        load_dotenv=False,
        auto_cast=True,
    )


def run() -> None:
    settings = get_settings()
    application = ApplicationBuilder(settings).build()
    options = {
        "bind": "%s:%s" % (settings.web.host, settings.web.port),
        "workers": number_of_workers(),
        "worker_class": "uvicorn.workers.UvicornWorker",
        "accesslog": "-",
        "errorlog": "-",
        "logger_class": StubbedGunicornLogger,
        "reload": True,
        "access_log_format": "%(h)s %(l)s %(u)s %(t)s %(r)s %(s)s %(b)s %(f)s %(a)s",
    }
    configure_gunicorn_logger_adapter(
        logging_level=settings.web.logs.logging_level,
        serialize_records=settings.web.is_production,
    )
    gunicorn_app = StandaloneApplication(application, options)
    gunicorn_app.run()


if __name__ == "__main__":
    run()
