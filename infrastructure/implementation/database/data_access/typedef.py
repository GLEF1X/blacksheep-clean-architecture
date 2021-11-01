import typing

from sqlalchemy.ext.asyncio import AsyncSessionTransaction
from sqlalchemy.sql import ClauseElement
from sqlalchemy.sql.elements import BinaryExpression

SQLAlchemyModel = typing.TypeVar("SQLAlchemyModel", bound="SQLAlchemyModelProto")

# bool in Union statement only for sqlalchemy mypy plugin
ExpressionType = typing.Union[BinaryExpression, ClauseElement, bool]

TransactionContext = typing.AsyncContextManager[AsyncSessionTransaction]


class SQLAlchemyModelProto(typing.Protocol):
    __abstract__: bool = False
