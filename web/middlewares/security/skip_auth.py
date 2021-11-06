from types import MethodType
from typing import TypeVar, Callable, Any, Union
from web.constants import SKIP_AUTH_KEY

C = TypeVar("C", bound=Callable[..., Any])
M = TypeVar("M", bound=MethodType)

C_M = Union[C, M]


def allow_no_auth(handler: C_M) -> C_M:
    if isinstance(handler, MethodType):
        need_to_be_wrapped = handler.__func__
    else:
        need_to_be_wrapped = handler
    setattr(need_to_be_wrapped, SKIP_AUTH_KEY, True)
    return handler
