from __future__ import annotations

import typing

from sqlalchemy import delete, exists, func, lambda_stmt, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import Executable

from src.infrastructure.implementation.database.orm.util.bulk_save import make_proxy_bulk_save_func
from src.infrastructure.implementation.database.orm.util.typedef import SQLAlchemyModel, ExpressionType
from src.infrastructure.interfaces.database.repositories.crud_repository import AbstractCRUDRepository

ASTERISK: typing.Final[str] = "*"


class SQLAlchemyCRUDRepository(AbstractCRUDRepository[SQLAlchemyModel]):
    def __init__(
            self,
            session_or_pool: typing.Union[sessionmaker, AsyncSession],
            model: typing.Optional[typing.Type[SQLAlchemyModel]] = None,
    ) -> None:
        AbstractCRUDRepository.__init__(self, model)
        if isinstance(session_or_pool, sessionmaker):
            self._session: AsyncSession = typing.cast(AsyncSession, session_or_pool())
        else:
            self._session = session_or_pool

    async def add(self, **values: typing.Any) -> int:
        insert_stmt = insert(self.model).values(**values)
        result = await self._session.execute(insert_stmt)
        return typing.cast(int, result.scalar())

    async def add_many(self, *models: SQLAlchemyModel) -> None:
        bulk_save_func = make_proxy_bulk_save_func(instances=models)
        await self._session.run_sync(bulk_save_func)

    async def get_all(self, *clauses: ExpressionType) -> typing.List[SQLAlchemyModel]:
        query_model = self.model
        stmt = lambda_stmt(lambda: select(query_model))
        stmt += lambda s: s.where(*clauses)
        result = (
            (await self._session.execute(typing.cast(Executable, stmt))).scalars().all()
        )
        return result

    async def get_one(
            self, *clauses: ExpressionType
    ) -> typing.Optional[SQLAlchemyModel]:
        query_model = self.model
        stmt = lambda_stmt(lambda: select(query_model))
        stmt += lambda s: s.where(*clauses)
        result = (
            (await self._session.execute(typing.cast(Executable, stmt)))
                .scalars()
                .first()
        )
        return typing.cast(typing.Optional[SQLAlchemyModel], result)

    async def update(self, *clauses: ExpressionType, **values: typing.Any) -> None:
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
