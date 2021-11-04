from __future__ import annotations

from typing import TypeVar, Generic

T = TypeVar("T")


class Query(Generic[T]):
    ...
