from __future__ import annotations

import abc
from typing import AsyncContextManager


class AbstractUnitOfWork(abc.ABC):
    @property
    @abc.abstractmethod
    def pipeline(self) -> AsyncContextManager:  # type: ignore
        pass
