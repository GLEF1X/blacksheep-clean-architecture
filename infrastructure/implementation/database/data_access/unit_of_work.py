from __future__ import annotations

import abc
import contextlib
from typing import Any, Dict, Generic, Type, TypeVar, cast, AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, AsyncSessionTransaction

from infrastructure.implementation.database.data_access.repository import SQLAlchemyRepository, \
    AbstractRepository
from infrastructure.implementation.database.data_access.typedef import TransactionContext

_Repository = TypeVar("_Repository", bound=AbstractRepository[Any])
_T = TypeVar("_T", bound=SQLAlchemyRepository[Any])


class AbstractUnitOfWork(abc.ABC, Generic[_Repository]):

    def __init__(self):
        self._repositories: Dict[str, _Repository] = {}

    @abc.abstractmethod
    def transaction(self) -> Any:  # type: ignore
        pass

    @abc.abstractmethod
    def get_repository(self, repository_type: Type[_Repository]) -> _Repository:
        pass


class SQLAlchemyUnitOfWork(AbstractUnitOfWork[SQLAlchemyRepository[Any]]):

    def __init__(self, session: AsyncSession) -> None:
        super(SQLAlchemyUnitOfWork, self).__init__()
        self._session = session

    @contextlib.asynccontextmanager
    async def _transaction(self) -> AsyncGenerator:
        if not self._session.in_transaction() and self._session.is_active:
            async with self._session.begin() as transaction:  # type: AsyncSessionTransaction
                yield transaction
        else:
            yield  # type: ignore

    @property
    def transaction(self) -> TransactionContext:  # this property only for mypy and IDE's coverage
        return self._transaction()

    def get_repository(self, repository_type: Type[_T]) -> _T:
        key = repository_type.__qualname__
        repository = self._repositories.get(key)
        if repository is None:
            repository = repository_type(self._session)
            self._repositories.update({key: repository})
        return cast(_T, repository)
