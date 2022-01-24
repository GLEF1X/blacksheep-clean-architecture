import pathlib

from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.schedulers.base import BaseScheduler
from apscheduler_di import ContextSchedulerDecorator
from blacksheep.server import Application
from blacksheep.server.openapi.v3 import OpenAPIHandler
from blacksheep.server.routing import RoutesRegistry
from blacksheep_prometheus import metrics, PrometheusMiddleware
from dynaconf import Dynaconf, LazySettings
from guardpost import Policy
from guardpost.common import AuthenticatedRequirement
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, AsyncEngine
from sqlalchemy.orm import sessionmaker

from src.application.application_services.interfaces.security.jwt.authentication_service import (
    AuthenticationService,
)
from src.application.use_cases.background_jobs.send_email import send_email_to_interested_customers
from src.infrastructure.implementation.integrations.email.email_service import EmailServiceImpl
from src.infrastructure.interfaces.integration.email.email_service import EmailService
from src.utils.cqrs_lib import MediatorInterface
from src.utils.logging import configure_logging, LoggingConfig
from src.web.api import controllers
from src.web.events import on_shutdown, on_startup
from src.web.factories import user_repository_factory, authentication_service_factory, \
    token_issuer_factory, mediator_factory, openapi_docs_factory
from src.web.middlewares.logging_middleware import LoggingMiddleware
from src.web.util.blacksheep_context import plugins
from src.web.util.blacksheep_context.integration.structlog import StructlogContextVarBindMiddleware
from src.web.util.blacksheep_context.middleware import RawContextMiddleware
from src.web.util.gunicorn_app import StandaloneApplication
from src.web.util.security.handlers.authorization_handler import SimpleAuthHandler
from src.web.util.security.requirements.utils import generate_crud_policies


class ApplicationBuilder:
    __slots__ = ("_root_route_registry", "_settings", "_application")

    def __init__(self, settings: LazySettings):
        self._root_route_registry = RoutesRegistry()
        self._settings = settings
        self._application = Application(
            debug=settings.web.is_production,
            show_error_details=settings.web.show_error_details,
        )
        self._application.controllers_router = self._root_route_registry

    def build(self) -> Application:
        self._setup_events()
        self._setup_dependency_injection()
        self._setup_routes()
        self._setup_middlewares()
        # Setup of security must be executed exactly after DI installation, because it rely on some services
        self._setup_security()
        self._setup_metrics()
        self._setup_background_jobs()
        return self._application

    def _setup_events(self) -> None:
        self._application.on_start += on_startup
        self._application.on_stop += on_shutdown

    def _setup_middlewares(self) -> None:
        self._application.middlewares.append(RawContextMiddleware(plugins=(
            plugins.RequestIdPlugin(),
            plugins.CorrelationIdPlugin()
        )))
        self._application.middlewares.append(StructlogContextVarBindMiddleware())
        self._application.middlewares.append(LoggingMiddleware())

    def _setup_metrics(self) -> None:
        self._application.middlewares.append(PrometheusMiddleware())
        self._application.router.add_get("/metrics", metrics)

    def _setup_security(self) -> None:
        security_service = self._application.services.build_provider().get(
            AuthenticationService
        )
        self._application.use_authentication().add(SimpleAuthHandler(security_service))
        authorization_strategy = self._application.use_authorization()
        authorization_strategy += Policy("authenticated", AuthenticatedRequirement())
        authorization_strategy.policies.extend(generate_crud_policies("orders"))

    def _setup_dependency_injection(self) -> None:
        # controller dependencies(singletones)
        self._application.services.add_instance(self._root_route_registry, RoutesRegistry)
        self._application.services.add_instance(self._settings, LazySettings)

        # database
        engine = create_async_engine(
            url=self._settings.db.connection_uri,
            future=True,
            query_cache_size=1200,
            pool_size=100,
            max_overflow=200,
            echo=True,
            echo_pool=True
        )
        session_pool = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
        self._application.services.add_instance(engine, AsyncEngine)
        self._application.services.add_instance(session_pool, sessionmaker)

        # CQRS
        self._application.services.add_transient_by_factory(mediator_factory, MediatorInterface)

        # infrastructure
        self._application.services.add_scoped(EmailService, EmailServiceImpl)

        # application services
        self._application.services.add_transient_by_factory(authentication_service_factory)
        self._application.services.add_transient_by_factory(user_repository_factory)
        self._application.services.add_transient_by_factory(token_issuer_factory)

        # Miscellaneous
        self._application.services.add_singleton_by_factory(openapi_docs_factory)

    def _setup_routes(self) -> None:
        docs = self._application.services.build_provider().get(OpenAPIHandler)
        controllers.install(self._application.controllers_router, self._settings, docs)
        current_api_version = self._settings.web.api_version
        docs.include = lambda path, _: path.startswith(f"/api/{current_api_version}/")
        docs.bind_app(self._application)

    def _setup_background_jobs(self) -> None:
        redis_job_store = RedisJobStore()
        job_defaults = {"default": redis_job_store}
        job_stores = {"default": redis_job_store}
        base_async_scheduler = AsyncIOScheduler(jobstores=job_stores, job_defaults=job_defaults)
        scheduler = ContextSchedulerDecorator(base_async_scheduler)
        self._application.services.add_instance(scheduler, BaseScheduler)
        scheduler.ctx._map = self._application.services._map  # noqa
        scheduler.add_job(send_email_to_interested_customers, "interval", seconds=120,
                          replace_existing=True)
        scheduler.start()


def get_settings() -> LazySettings:
    base_directory = pathlib.Path(__name__).resolve().parent.parent
    return Dynaconf(
        settings_files=["settings.toml", ".secrets.toml"],
        redis=True,
        preload=[base_directory / "settings.toml"],
        environments=["development", "production", "testing"],
        load_dotenv=False,
        auto_cast=True,
    )


def run() -> None:
    settings = get_settings()
    log_config = configure_logging(LoggingConfig())
    application = ApplicationBuilder(settings).build()
    options = {
        "bind": "%s:%s" % (settings.web.host, settings.web.port),
        "worker_class": "uvicorn.workers.UvicornWorker",
        "reload": True,
        "disable_existing_loggers": False,
        "preload_app": True,
        "logconfig_dict": log_config
    }
    gunicorn_app = StandaloneApplication(application, options)
    gunicorn_app.run()


if __name__ == "__main__":
    run()
