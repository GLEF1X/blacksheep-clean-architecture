from typing import Any, TypeVar, Callable, cast

import kink

FuncT = TypeVar("FuncT", bound=Callable[..., Any])


def boostrap_dependency_injection() -> None:
    pass


def inject(func: FuncT, *args: Any, **kwargs: Any) -> FuncT:
    """Alias for dependency injection library `inject` function"""
    return cast(FuncT, kink.inject(func, *args, **kwargs))
