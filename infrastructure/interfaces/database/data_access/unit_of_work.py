from __future__ import annotations

import abc
from typing import Any, AsyncContextManager, Dict, Generic, Type, TypeVar

from infrastructure.interfaces.database.data_access.repository import AbstractRepository

_Repository = TypeVar("_Repository", bound=AbstractRepository[Any])


class AbstractUnitOfWork(abc.ABC, Generic[_Repository]):
    def __init__(self):
        self._repositories: Dict[str, _Repository] = {}

    @property
    @abc.abstractmethod
    def pipeline(self) -> AsyncContextManager:  # type: ignore
        pass

    @abc.abstractmethod
    def get_repository(self, repository_type: Type[_Repository]) -> _Repository:
        pass
