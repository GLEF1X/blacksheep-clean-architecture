from __future__ import annotations

from typing import Generic, Optional, TypeVar

T = TypeVar("T")


class Failure:
    def __init__(self, message: str, *exceptions: Exception) -> None:
        self._failure_details = {
            ex.__class__.__qualname__: ex.__str__() for ex in exceptions
        }
        self.message = message

    @classmethod
    def from_exception(cls, ex: Exception, message: Optional[str] = None) -> Failure:
        if message is None:
            message = str(ex)
        return cls(message, ex)


class Result(Generic[T]):
    def __init__(self, value: T, failure: Optional[Failure] = None) -> None:
        self._value = value
        self._failure = failure

    @property
    def value(self) -> T:
        return self._value

    @classmethod
    def fail(cls, failure: Failure) -> Result[None]:
        return cls(None, failure)  # type: ignore

    @classmethod
    def success(cls, value: T) -> Result[T]:
        return cls(value)

    @property
    def failed(self) -> bool:
        return self._failure is not None

    @property
    def error_message(self) -> str:
        if self._failure is None:
            raise AttributeError()
        return self._failure.message
