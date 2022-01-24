import copy
from collections import UserDict
from contextvars import copy_context
from typing import Any

from src.web.util.blacksheep_context import _request_scope_context_storage
from src.web.util.blacksheep_context.errors import ConfigurationError, ContextDoesNotExistError


class _Context(UserDict):
    """
    A mapping with dict-like interface.
    It is using request context as a data store. Can be used only if context
    has been created in the middleware.
    """

    def __init__(self, error=ConfigurationError("Can't instantiate with attributes"), *args: Any,  # noqa
                 **kwargs: Any):
        # not calling super on purpose
        if args or kwargs:
            raise error

    @property
    def data(self) -> dict:  # type: ignore
        """
        Dump this to json.
        Object itself it not serializable.
        """
        try:
            return _request_scope_context_storage.get()
        except LookupError:
            raise ContextDoesNotExistError

    def exists(self) -> bool:
        return _request_scope_context_storage in copy_context()

    def copy(self) -> dict:  # type: ignore
        """Read only context data."""

        return copy.copy(self.data)

    def __del__(self) -> None:
        del _request_scope_context_storage


context = _Context()
