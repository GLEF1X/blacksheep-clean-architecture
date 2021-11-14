from __future__ import annotations

from typing import Protocol

from src.entities.models.order import Order


class OrderDomainServiceInterface(Protocol):
    def get_total(self, order: Order) -> float:
        ...
