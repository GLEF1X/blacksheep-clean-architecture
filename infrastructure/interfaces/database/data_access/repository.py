from __future__ import annotations

import abc
import typing

EntryType = typing.TypeVar("EntryType")

_T = typing.TypeVar("_T")


class AbstractRepository(abc.ABC, typing.Generic[EntryType]):
    """
    Base class of hierarchy of repositories

    """

    model: typing.ClassVar[typing.Type[EntryType]]

    @abc.abstractmethod
    async def add(self, **values: typing.Any) -> int:
        pass

    @abc.abstractmethod
    async def add_many(self, *models: EntryType) -> None:
        pass

    @abc.abstractmethod
    async def get_all(self, *clauses: typing.Any) -> typing.List[EntryType]:
        pass

    @abc.abstractmethod
    async def get_one(self, *clauses: typing.Any) -> typing.Optional[EntryType]:
        pass

    @abc.abstractmethod
    async def update(self, *clauses: typing.Any, **values: typing.Any) -> None:
        pass

    @abc.abstractmethod
    async def delete(self, *clauses: typing.Any) -> typing.List[EntryType]:
        pass

    async def exists(self, *clauses: typing.Any) -> typing.Any:  # type: ignore
        cls_name = self.__class__.__qualname__
        raise TypeError(
            "Repository %s does not provide way to determine is object exists or not"
            % cls_name
        )

    async def count(self, *clauses: typing.Any) -> typing.Any:  # type: ignore
        cls_name = self.__class__.__qualname__
        raise TypeError(
            "Repository %s does not provide way to determine count of objects"
            % cls_name
        )

    def with_changed_query_model(
        self, /, model: typing.Type[_T]
    ) -> AbstractRepository[_T]:
        self.model = model
        return self
