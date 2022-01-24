from contextvars import Token
from typing import Optional, Sequence, Callable, Awaitable, Dict, Any

from blacksheep import Response, Request

from src.web.util.blacksheep_context import _request_scope_context_storage
from src.web.util.blacksheep_context.errors import ConfigurationError, MiddleWareValidationError
from src.web.util.blacksheep_context.plugins import Plugin


class RawContextMiddleware:
    def __init__(
            self,
            plugins: Optional[Sequence[Plugin]] = None,
            default_error_response: Response = Response(status=400),
    ) -> None:
        for plugin in plugins or ():
            if not isinstance(plugin, Plugin):
                raise ConfigurationError(f"Plugin {plugin} is not a valid instance")

        self.plugins = plugins or ()
        self.error_response = default_error_response

    async def get_context(self, request: Request) -> Dict[Any, Any]:
        """
        You might want to override this method.

        The dict it returns will be saved in the scope of a context. You can
        always do that later.
        """
        return {
            plugin.key: await plugin.process_request(request)
            for plugin in self.plugins
        }

    async def __call__(
            self, request: Request, handler: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        try:
            ctx = await self.get_context(request)
        except MiddleWareValidationError as e:
            if e.error_response is not None:
                error_response = e.error_response
            else:
                error_response = self.error_response
            return error_response

        token: Token = _request_scope_context_storage.set(ctx)

        try:
            response = await handler(request)
            for plugin in self.plugins:
                await plugin.enrich_response(response)
            return response
        finally:
            _request_scope_context_storage.reset(token)
