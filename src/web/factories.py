from typing import Any

from blacksheep.server.openapi.v3 import OpenAPIHandler
from dynaconf import LazySettings
from openapidocs.v3 import Info
from rodi import GetServiceContext
from sqlalchemy.orm import sessionmaker

from src.application.application_services.implementation.security.jwt.authentication import \
    JWTAuthenticationService
from src.application.application_services.implementation.security.jwt.decoder import JWTTokenDecoder
from src.application.application_services.implementation.security.jwt.token_issuer import \
    JWTTokenIssuer
from src.application.application_services.interfaces.security.jwt.authentication_service import \
    AuthenticationService
from src.application.application_services.interfaces.security.jwt.token_issuer import TokenIssuer
from src.application.cqrs_lib import MediatorInterface, MediatorImpl
from src.application.use_cases.order.commands.create_order.command import CreateOrderCommand
from src.application.use_cases.order.commands.create_order.handler import CreateOrderHandler
from src.application.use_cases.order.queries.get_order_by_id.handler import GetOrderByIdHandler
from src.application.use_cases.order.queries.get_order_by_id.query import GetOrderByIdQuery
from src.application.use_cases.validation.validation_decorator import \
    ValidationQueryHandlerDecorator
from src.entities.domain_services.implementation.order_service import OrderServiceImpl
from src.entities.models.user import User
from src.infrastructure.implementation.database.data_access.repository import SQLAlchemyRepository
from src.infrastructure.implementation.database.data_access.unit_of_work import SQLAlchemyUnitOfWork
from src.infrastructure.implementation.database.orm.tables import UserModel
from src.infrastructure.implementation.delivery.delivery_service import DeliveryServiceImpl
from src.infrastructure.interfaces.database.data_access.repository import AbstractRepository


def user_repository_factory(services: GetServiceContext) -> AbstractRepository[User]:
    session = services.provider.get(sessionmaker)()
    return SQLAlchemyRepository(session, UserModel)


def authentication_service_factory(services: GetServiceContext) -> AuthenticationService:
    settings = services.provider.get(LazySettings)
    user_repository = services.provider.get(AbstractRepository[User])
    return JWTAuthenticationService(
        token_decoder=JWTTokenDecoder(
            secret_key=settings.web.auth.secret_key,
            encoding_algorithm=settings.web.auth.algorithm,
        ),
        user_repository=user_repository,
    )


def token_issuer_factory(services: GetServiceContext) -> TokenIssuer:
    settings = services.provider.get(LazySettings)
    user_repository = services.provider.get(AbstractRepository[User])
    return JWTTokenIssuer(
        user_repository=user_repository,
        secret_key=settings.web.auth.secret_key,
        encoding_algorithm=settings.web.auth.algorithm,
    )


def mediator_factory(services: GetServiceContext) -> MediatorInterface:
    session = services.provider.get(sessionmaker)()
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


def openapi_docs_factory(services: GetServiceContext) -> OpenAPIHandler:
    settings = services.provider.get(LazySettings)
    return OpenAPIHandler(
        info=Info(
            title=settings.web.docs.title,
            version=settings.web.docs.version,
        ),
        ui_path=settings.web.docs.path,
        json_spec_path=settings.web.docs.json_spec_path,
        yaml_spec_path=settings.web.docs.yaml_spec_path,
    )