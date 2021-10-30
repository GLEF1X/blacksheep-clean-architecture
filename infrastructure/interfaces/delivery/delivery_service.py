from __future__ import annotations

from typing import Protocol


class DeliveryServiceInterface(Protocol):

    def calculate_delivery_cost(self, weight: float) -> float: ...
