from __future__ import annotations

from datetime import datetime

import pytest

from src.entities.domain_services.implementation.order_service import OrderServiceImpl
from src.entities.models.order import Order
from src.entities.models.product import Product
from src.entities.models.user import User
from src.infrastructure.implementation.delivery.delivery_service import (
    DeliveryServiceImpl,
)


@pytest.fixture()
def delivery_service() -> DeliveryServiceImpl:
    return DeliveryServiceImpl()


@pytest.fixture()
def order_service(delivery_service: DeliveryServiceImpl) -> OrderServiceImpl:
    return OrderServiceImpl(delivery_service)


@pytest.fixture()
def order() -> Order:
    order = Order(
        products=[
            Product(id=1, weight=5, price=50, created_at=datetime.now()),
            Product(id=2, weight=10, price=70, created_at=datetime.now()),
        ],
        created_at=datetime.now(),
        order_date=datetime.now(),
        customer=User(
            first_name="Glib",
            last_name="Garanin",
            username="GLEF1X",
            hashed_password="sdfs",
        ),
    )
    order.id = 1
    return order


def test_get_total(order: Order, order_service: OrderServiceImpl) -> None:
    price = order_service.get_total(order)
    assert price == 120
