from __future__ import annotations

from typing import Protocol


class OrderServiceInterface(Protocol):

    def get_total(self, order: Order) -> float: ...
