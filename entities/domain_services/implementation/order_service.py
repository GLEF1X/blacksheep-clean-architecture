from __future__ import annotations

from entities.models.order import Order
from infrastructure.interfaces.delivery.delivery_service import DeliveryServiceInterface


class OrderServiceImpl:
    def __init__(self, delivery_service: DeliveryServiceInterface):
        self._delivery_service = delivery_service

    def get_total(self, order: Order) -> float:
        total_price = sum(product.price for product in order.products)
        delivery_cost = 0.00
        if total_price < 1000:
            total_weight = sum(product.weight for product in order.products)
            delivery_cost = self._delivery_service.calculate_delivery_cost(total_weight)
        return total_price + delivery_cost
