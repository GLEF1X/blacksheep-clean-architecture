from contextvars import Token
from typing import Optional, Sequence, Callable, Awaitable

from blacksheep import Response, Request

from src.web.util.blacksheep_context.errors import ConfigurationError, MiddleWareValidationError
from src.web.util.blacksheep_context.plugins import Plugin


class ContextMiddleware:
    """
    Middleware that creates empty context for request it's used on. If not
    used, you won't be able to use context object.
    """

    def __init__(
            self,
            plugins: Optional[Sequence[Plugin]] = None,
            default_error_response: Response = Response(status=400),
    ) -> None:
        for plugin in plugins or ():
            if not isinstance(plugin, Plugin):
                raise ConfigurationError(
                    f"Plugin {plugin} is not a valid instance"
                )
        self.plugins = plugins or ()
        self.error_response = default_error_response

    async def set_context(self, request: Request) -> dict:
        """
        You might want to override this method.

        The dict it returns will be saved in the scope of a context. You can
        always do that later.
        """
        return {
            plugin.key: await plugin.process_request(request)
            for plugin in self.plugins
        }

    async def dispatch(
            self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        try:
            context = await self.set_context(request)
            token: Token = _request_scope_context_storage.set(context)
        except MiddleWareValidationError as e:
            if e.error_response:
                error_response = e.error_response
            else:
                error_response = self.error_response
            return error_response

        try:
            response = await call_next(request)
            for plugin in self.plugins:
                await plugin.enrich_response(response)

        finally:
            _request_scope_context_storage.reset(token)

        return response
