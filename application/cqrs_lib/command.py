from __future__ import annotations

from typing import Generic, TypeVar

T = TypeVar("T")


class Command(Generic[T]):
    ...
