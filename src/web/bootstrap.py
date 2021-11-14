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
from src.application.cqrs_lib import MediatorInterface
from src.application.use_cases.background_jobs.send_email import send_email_to_interested_users
from src.infrastructure.implementation.email.email_client import EmailClientImpl
from src.infrastructure.interfaces.email.email_client import EmailClient
from src.web.api import controllers
from src.web.events import on_shutdown, on_startup
from src.web.factories import user_repository_factory, authentication_service_factory, \
    token_issuer_factory, mediator_factory, openapi_docs_factory
from src.web.middlewares.logging_middleware import LoggingMiddleware
from src.web.web_utils.colored_logger import COLORED_LOGGING_CONFIG
from src.web.web_utils.gunicorn_app import StandaloneApplication
from src.web.web_utils.security.handlers.authorization_handler import SimpleAuthHandler
from src.web.web_utils.security.requirements.scope_requirement import ScopeRequirement
from src.web.web_utils.security.requirements.utils import generate_crud_scopes

BASE_DIR = pathlib.Path(__name__).resolve().parent.parent
DISABLED = "-"


class ApplicationBuilder:
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
        # Setup of authentication must be executed exactly after DI installation, because it rely
        # that application services will contain provider of SecurityService
        self._setup_security()
        self._setup_metrics()
        self._setup_background_jobs()
        return self._application

    def _setup_events(self) -> None:
        self._application.on_start += on_startup
        self._application.on_stop += on_shutdown

    def _setup_middlewares(self) -> None:
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
        authorization_strategy += Policy(
            "scoped", ScopeRequirement(scopes=generate_crud_scopes("orders"))
        )

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
            max_overflow=200
        )
        session_pool = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
        self._application.services.add_instance(engine, AsyncEngine)
        self._application.services.add_instance(session_pool, sessionmaker)

        # CQRS
        self._application.services.add_transient_by_factory(mediator_factory, MediatorInterface)

        # infrastructure
        self._application.services.add_scoped(EmailClient, EmailClientImpl)

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
        # overtaking dependencies
        scheduler.ctx._map = self._application.services._map  # noqa
        scheduler.add_job(send_email_to_interested_users, "interval", seconds=120,
                          replace_existing=True)
        scheduler.start()


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
        "workers": 2,
        "worker_class": "uvicorn.workers.UvicornWorker",
        "reload": True,
        "disable_existing_loggers": False,
        "logconfig_dict": COLORED_LOGGING_CONFIG,
        "preload_app": True
    }
    gunicorn_app = StandaloneApplication(application, options)
    gunicorn_app.run()


if __name__ == "__main__":
    run()
