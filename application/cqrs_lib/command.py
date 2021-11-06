from __future__ import annotations

from typing import Generic, TypeVar

from pydantic.generics import GenericModel

T = TypeVar("T")


class Command(GenericModel, Generic[T]):
    ...
