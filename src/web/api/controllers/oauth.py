import http
from typing import Optional

from blacksheep import Response
from blacksheep.server.bindings import FromJSON
from blacksheep.server.openapi.common import EndpointDocs, ResponseInfo, ContentInfo
from blacksheep.server.openapi.v3 import OpenAPIHandler
from blacksheep.server.routing import RoutesRegistry
from dynaconf import LazySettings

from src.application.application_services.dto.form_data import FormData
from src.application.application_services.dto.issued_token import IssuedTokenDto
from src.application.application_services.dto.user_dto import UserDto
from src.application.application_services.implementation.security.jwt.exceptions import SecurityExceptionCatalog
from src.application.application_services.interfaces.security.jwt.token_issuer import (
    TokenIssuer,
)
from src.utils.cqrs_lib import MediatorInterface
from src.utils.exceptions import ProcessError
from src.web.api.controllers import RegistrableApiController
from src.web.dto.oauth_input import OauthFormInput

EXAMPLE_API_TOKEN = (
    "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9."
    "eyJzdWIiOiJHTEVGMVgiLCJleHAiOjE2MzY0MDE4MDcsInNjb3BlcyI6WyJoZWxsbyIsIndvcmxkIiwiZXgiXX0."
    "J8KhG52tRVkxW7oyXILJuR0M0oxz6dskKVBjuELBqz4"
)


class OauthController(RegistrableApiController):
    def __init__(
            self,
            token_issuer: TokenIssuer,
            router: RoutesRegistry,
            settings: LazySettings,
            mediator: MediatorInterface,
            docs: OpenAPIHandler,
    ):
        RegistrableApiController.__init__(self, router, settings, mediator, docs)
        self._token_issuer = token_issuer

    async def get_token(self, form_gasket: FromJSON[OauthFormInput]) -> Response:
        form = form_gasket.value
        try:
            token = await self._token_issuer.issue_token(
                FormData(username=form.username, password=form.password, scopes=form.scopes)
            )
        except ProcessError:
            return Response(status=http.HTTPStatus.UNAUTHORIZED)
        return self.pretty_json(token)

    @classmethod
    def class_name(cls) -> str:
        return "oauth"

    @classmethod
    def version(cls) -> Optional[str]:
        return "v1"

    def register(self) -> None:
        self.add_route(
            method="POST",
            path="/sign-in",
            controller_method=self.get_token,
            doc=EndpointDocs(
                responses={
                    200: ResponseInfo(
                        "Token was successfully created.",
                        content=[
                            ContentInfo(
                                IssuedTokenDto,
                                examples=[
                                    IssuedTokenDto(
                                        api_token=EXAMPLE_API_TOKEN,
                                        issuer=UserDto(
                                            id=1,
                                            first_name="Glib",
                                            last_name="Garanin",
                                            username="GLEF1X",
                                            email="glebgar567@gmail.com",
                                        ),
                                    )
                                ],
                            )
                        ],
                    )
                }
            ),
        )
