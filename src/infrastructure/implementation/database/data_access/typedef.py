import typing

from sqlalchemy.ext.asyncio import AsyncSessionTransaction
from sqlalchemy.sql import ClauseElement
from sqlalchemy.sql.elements import BinaryExpression

SQLAlchemyModel = typing.TypeVar("SQLAlchemyModel")

# bool in Union statement only for sqlalchemy mypy plugin
ExpressionType = typing.Union[BinaryExpression, ClauseElement, bool]

TransactionContext = typing.AsyncContextManager[AsyncSessionTransaction]
