from __future__ import annotations

import typing

from sqlalchemy import delete, exists, func, lambda_stmt, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, sessionmaker  # noqa
from sqlalchemy.sql import Executable

from infrastructure.interfaces.database.data_access.repository import AbstractRepository
from .typedef import (
    SQLAlchemyModel,
    ExpressionType
)

ASTERISK = "*"


class SQLAlchemyRepository(AbstractRepository[SQLAlchemyModel]):
    # You need to define this variable in child classes
    model: typing.ClassVar[typing.Type[SQLAlchemyModel]]

    def __init__(self, session_or_pool: typing.Union[sessionmaker, AsyncSession]) -> None:
        if isinstance(session_or_pool, sessionmaker):
            self._session: AsyncSession = typing.cast(AsyncSession, session_or_pool())
        else:
            self._session = session_or_pool

    async def add(self, **values: typing.Any) -> None:
        insert_stmt = insert(self.model).values(**values).on_conflict_do_nothing()
        await self._session.execute(insert_stmt)

    async def get_all(self, *clauses: ExpressionType) -> typing.List[SQLAlchemyModel]:
        query_model = self.model
        stmt = lambda_stmt(lambda: select(query_model))
        stmt += lambda s: s.where(*clauses)
        result = (await self._session.execute(typing.cast(Executable, stmt))).scalars().all()
        return result

    async def get_one(self, *clauses: ExpressionType) -> typing.Optional[SQLAlchemyModel]:
        query_model = self.model
        stmt = lambda_stmt(lambda: select(query_model))
        stmt += lambda s: s.where(*clauses)
        result = (await self._session.execute(typing.cast(Executable, stmt))).scalars().first()
        return typing.cast(typing.Optional[SQLAlchemyModel], result)

    async def update(self, *clauses: ExpressionType, **values: typing.Any) -> None:
        """
        Update values in database, filter by `telegram_id`

        :param clauses: where conditionals
        :param values: key/value for update
        :return:
        """
        stmt = update(self.model).where(*clauses).values(**values).returning(None)
        await self._session.execute(stmt)
        return None

    async def exists(self, *clauses: ExpressionType) -> bool:
        stmt = exists(select(self.model).where(*clauses)).select()
        result = (await self._session.execute(stmt)).scalar()
        return typing.cast(bool, result)

    async def delete(self, *clauses: ExpressionType) -> typing.List[SQLAlchemyModel]:
        stmt = delete(self.model).where(*clauses).returning(ASTERISK)
        result = (await self._session.execute(stmt)).scalars().all()
        return typing.cast(typing.List[SQLAlchemyModel], result)

    async def count(self, *clauses: ExpressionType) -> int:
        stmt = lambda_stmt(lambda: select(func.count(ASTERISK)))
        if clauses:
            stmt += lambda s: s.where(*clauses)
        result = (await self._session.execute(typing.cast(Executable, stmt))).scalar()

        return typing.cast(int, result)


def make_proxy_bulk_save_func(
        instances: typing.Sequence[typing.Any],
        return_defaults: bool = False,
        update_changed_only: bool = True,
        preserve_order: bool = True,
) -> typing.Callable[[Session], None]:
    def _proxy(session: Session) -> None:
        return session.bulk_save_objects(
            instances,
            return_defaults=return_defaults,
            update_changed_only=update_changed_only,
            preserve_order=preserve_order,
        )  # type: ignore

    return _proxy
