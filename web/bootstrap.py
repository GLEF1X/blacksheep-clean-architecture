import pathlib
from typing import Any

from blacksheep.server import Application
from blacksheep.server.openapi.v3 import OpenAPIHandler
from blacksheep.server.routing import RoutesRegistry
from dynaconf import Dynaconf, LazySettings
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
from application.cqrs_lib import MediatorImpl, MediatorInterface
from application.use_cases.order.commands.create_order.command import CreateOrderCommand
from application.use_cases.order.commands.create_order.handler import CreateOrderHandler
from application.use_cases.order.queries.get_order_by_id.handler import (
    GetOrderByIdHandler,
)
from application.use_cases.order.queries.get_order_by_id.query import GetOrderByIdQuery
from entities.domain_services.implementation.order_service import OrderServiceImpl
from infrastructure.implementation.database.data_access.repository import (
    SQLAlchemyRepository,
)
from infrastructure.implementation.database.data_access.unit_of_work import (
    SQLAlchemyUnitOfWork,
)
from infrastructure.implementation.database.orm.tables import UserModel
from infrastructure.implementation.delivery.delivery_service import DeliveryServiceImpl
from utils.logging.gunicorn import (
    StubbedGunicornLogger,
    configure_gunicorn_logger_adapter,
)
from utils.validation.validation_decorator import ValidationQueryHandlerDecorator
from web import controllers
from web.events import on_shutdown, on_startup
from web.middlewares.logging_middleware import LoggingMiddleware
from web.middlewares.security.auth_middleware import AuthenticationMiddleware
from web.web_utils.gunicorn_app import StandaloneApplication, number_of_workers
from web.web_utils.routing import PrefixedRouter

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
        debug=settings.web.is_production,
        show_error_details=settings.web.show_error_details,
    )
    application.on_start += on_startup
    application.on_stop += on_shutdown
    application.controllers_router = controllers_router
    _setup_dependency_injection(application, settings)
    _setup_routes(application, settings)
    # Setup of middlewares must be executed exactly after DI installation, because it rely
    # that application services will contain provider of SecurityService
    _setup_middlewares(application)
    return application


def _setup_middlewares(application: Application):
    provider = application.services.build_provider()
    security_service = provider.get(SecurityService)
    application.middlewares.append(LoggingMiddleware())
    application.middlewares.append(AuthenticationMiddleware(security_service))


def _setup_dependency_injection(
    application: Application, settings: LazySettings
) -> None:
    # controller dependencies
    application.services.add_instance(application.controllers_router, RoutesRegistry)
    application.services.add_instance(settings, LazySettings)

    # database
    engine = create_async_engine(
        url=make_url(settings.db.connection_uri),
        future=True,
        query_cache_size=1200,
        pool_size=100,
        max_overflow=200,
        poolclass=AsyncAdaptedQueuePool,
    )
    session_pool = sessionmaker(
        bind=engine, class_=AsyncSession, expire_on_commit=False
    )

    # mediator
    application.services.register_factory(
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
        secret_key=settings.web.auth.secret_key,
        encoding_algorithm=settings.web.auth.algorithm,
    )
    application.services.add_instance(security_service, SecurityService)

    # OpenAPI
    docs = OpenAPIHandler(
        info=Info(title=settings.web.docs.title, version=settings.web.docs.version),
        ui_path=settings.web.docs.path,
        json_spec_path=settings.web.docs.json_spec_path,
        yaml_spec_path=settings.web.docs.yaml_spec_path,
    )
    application.services.add_instance(docs, OpenAPIHandler)


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


def _setup_routes(
    application: ApplicationWithPrefixedRouter, settings: LazySettings
) -> None:
    controllers.install(application.controllers_router, settings)
    docs = application.services.build_provider().get(OpenAPIHandler)
    docs.bind_app(application)


def run() -> None:
    settings = get_settings()
    application = configure_application(settings)
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
