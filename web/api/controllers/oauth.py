from typing import Optional

from blacksheep import Response
from blacksheep.server.bindings import FromJSON
from blacksheep.server.openapi.v3 import OpenAPIHandler
from blacksheep.server.routing import RoutesRegistry
from dynaconf import LazySettings

from application.application_services.dto.form_data import FormData
from application.application_services.interfaces.security.jwt.security_service import (
    SecurityService,
)
from application.cqrs_lib import MediatorInterface
from web.api.controllers import RegistrableApiController
from web.dto.oauth_input import OauthFormInput


class OauthController(RegistrableApiController):
    def __init__(
            self,
            security_service: SecurityService,
            router: RoutesRegistry,
            settings: LazySettings,
            mediator: MediatorInterface,
            docs: OpenAPIHandler,
    ):
        RegistrableApiController.__init__(self, router, settings, mediator, docs)
        self._security_service = security_service

    def register(self) -> None:
        self.add_route("POST", "/authenticate", self.get_token, require_auth=False)

    async def get_token(self, form_gasket: FromJSON[OauthFormInput]) -> Response:
        form = form_gasket.value
        token = await self._security_service.issue_token(
            FormData(username=form.username, password=form.password)
        )
        return self.pretty_json(token)

    @classmethod
    def class_name(cls) -> str:
        return "oauth"

    @classmethod
    def version(cls) -> Optional[str]:
        return "v1"
