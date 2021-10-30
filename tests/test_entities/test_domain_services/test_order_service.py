from __future__ import annotations

import pytest

from entities.domain_services.implementation.order_service import OrderServiceImpl
from entities.models.order import Order
from entities.models.product import Product
from infrastructure.implementation.delivery.delivery_service import DeliveryServiceImpl


@pytest.fixture()
def delivery_service() -> DeliveryServiceImpl:
    return DeliveryServiceImpl()


@pytest.fixture()
def order_service(delivery_service: DeliveryServiceImpl) -> OrderServiceImpl:
    return OrderServiceImpl(delivery_service)


@pytest.fixture()
def order() -> Order:
    return Order(
        id=1,
        products=[
            Product(id=1, weight=5, price=50),
            Product(id=2, weight=10, price=70)
        ]
    )


def test_get_total(order: Order, order_service: OrderServiceImpl) -> None:
    price = order_service.get_total(order)
    expected_price = 0
    assert price == expected_price
