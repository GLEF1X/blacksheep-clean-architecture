from __future__ import annotations

from typing import Generic, TypeVar, Optional, Sequence, Type

T = TypeVar("T")


class Failure:
    def __init__(self, exceptions: Sequence[Exception], message: str) -> None:
        self._failure_details = {
            ex.__class__.__qualname__: ex.__str__() for ex in exceptions
        }
        self._message = message


class Result(Generic[T]):
    def __init__(self, value: T, failure: Optional[Failure] = None) -> None:
        self._value = value
        self._failure = failure

    @property
    def value(self) -> T:
        return self._value

    @classmethod
    def fail(cls: Type[Result[None]], failure: Failure) -> Result[None]:
        return cls(None, failure)

    @classmethod
    def success(cls, value: T) -> Result[T]:
        return cls(value, None)
