from __future__ import annotations

import contextlib
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, AsyncSessionTransaction

from src.infrastructure.implementation.database.orm.util.typedef import TransactionContext
from src.infrastructure.interfaces.database.unit_of_work import (
    AbstractUnitOfWork
)


class SQLAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @contextlib.asynccontextmanager
    async def _transaction(self) -> AsyncGenerator:
        if not self._session.in_transaction() and self._session.is_active:
            async with self._session.begin() as transaction:  # type: AsyncSessionTransaction
                yield transaction
        else:
            yield  # type: ignore

    @property
    def pipeline(
            self,
    ) -> TransactionContext:  # this property only for mypy and IDE's coverage
        return self._transaction()
