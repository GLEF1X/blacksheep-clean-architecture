from argon2 import PasswordHasher
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
from src.application.use_cases.order.commands.create_order.command import CreateOrderCommand
from src.application.use_cases.order.commands.create_order.handler import CreateOrderHandler
from src.application.use_cases.order.queries.get_all_orders.handler import GetAllOrdersHandler
from src.application.use_cases.order.queries.get_all_orders.query import GetAllOrdersQuery
from src.application.use_cases.order.queries.get_order_by_id.handler import GetOrderByIdHandler
from src.application.use_cases.order.queries.get_order_by_id.query import GetOrderByIdQuery
from src.domain.domain_services.implementation.order_service import OrderServiceImpl
from src.infrastructure.implementation.database.repositories.user.repository import UserRepositoryImpl
from src.infrastructure.implementation.database.repositories.order.repository import OrderRepositoryImpl
from src.infrastructure.implementation.database.unit_of_work import SQLAlchemyUnitOfWork
from src.infrastructure.implementation.delivery.delivery_service import DeliveryServiceImpl
from src.infrastructure.interfaces.database.repositories.customer.repository import UserRepository
from src.utils.cqrs_lib import MediatorImpl, MediatorInterface


def user_repository_factory(services: GetServiceContext) -> UserRepository:
    session = services.provider.get(sessionmaker)()
    return UserRepositoryImpl(session)


def authentication_service_factory(services: GetServiceContext) -> AuthenticationService:
    settings = services.provider.get(LazySettings)
    customer_repository = services.provider.get(UserRepository)
    return JWTAuthenticationService(
        token_decoder=JWTTokenDecoder(
            secret_key=settings.web.auth.secret_key,
            encoding_algorithm=settings.web.auth.algorithm,
        ),
        customer_repository=customer_repository,
    )


def token_issuer_factory(services: GetServiceContext) -> TokenIssuer:
    settings = services.provider.get(LazySettings)
    user_repository = services.provider.get(UserRepository)
    return JWTTokenIssuer(
        user_repository=user_repository,
        secret_key=settings.web.auth.secret_key,
        encoding_algorithm=settings.web.auth.algorithm,
        password_hasher=PasswordHasher(parallelism=8)
    )


def mediator_factory(services: GetServiceContext) -> MediatorInterface:
    session = services.provider.get(sessionmaker)()
    order_repository = OrderRepositoryImpl(session)
    uow = SQLAlchemyUnitOfWork(session)
    order_domain_service = OrderServiceImpl(DeliveryServiceImpl())
    return MediatorImpl(
        query_handlers={
            GetOrderByIdQuery: [
                GetOrderByIdHandler(order_repository, order_domain_service, uow)
            ],
            GetAllOrdersQuery: [
                GetAllOrdersHandler(order_repository, order_domain_service, uow)
            ]
        },
        command_handlers={
            CreateOrderCommand: CreateOrderHandler(order_repository, uow)
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
