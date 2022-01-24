from contextvars import ContextVar
from typing import Any, Dict

_request_scope_context_storage: ContextVar[Dict[Any, Any]] = ContextVar(
    "starlette_context"
)

from src.web.util.blacksheep_context.ctx import context  # noqa: E402
from src.web.util.blacksheep_context.header_keys import HeaderKeys  # noqa: E402
