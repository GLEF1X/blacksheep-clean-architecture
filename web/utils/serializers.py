from __future__ import annotations

import abc
from typing import Final, Generic, TypeVar, Type, cast

import dataclass_factory

PlainData = TypeVar("PlainData")
Serialized = TypeVar("Serialized")

KEY_VALUE_SEPARATOR: Final[str] = "::/::"
UTF8_ENCODING: Final[str] = "utf-8"
DEFAULT_ITEM_DELIMITER: Final[str] = "|"


class SerializationError(Exception):
    pass


class Serializer(abc.ABC, Generic[PlainData, Serialized]):
    @abc.abstractmethod
    def serialize(self, data: PlainData) -> Serialized:
        pass

    def deserialize(self, data: Serialized, skip_empty: bool = False) -> PlainData:
        if skip_empty and data is None:
            return self._get_empty_result()
        return self._deserialize(data)

    @abc.abstractmethod
    def _deserialize(self, data: Serialized) -> PlainData:
        pass

    @abc.abstractmethod
    def _get_empty_result(self) -> PlainData:
        pass


Model = TypeVar("Model")


class DataclassSerializer(Serializer[Model, str]):

    def __init__(self, class_: Type[Model]):
        self._factory = dataclass_factory.Factory()
        self._class = class_

    def serialize(self, data: PlainData) -> Serialized:
        return cast(Serialized, self._factory.dump(data, self._class))

    def _deserialize(self, data: Serialized) -> PlainData:
        return self._factory.load(data, self._class)

    def _get_empty_result(self) -> PlainData:
        return {}  # type: ignore
