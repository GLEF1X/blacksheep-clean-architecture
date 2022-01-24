from __future__ import annotations

from typing import Protocol

from src.domain.entities.order import Order


class OrderDomainServiceInterface(Protocol):
    def get_total(self, order: Order) -> float:
        ...
