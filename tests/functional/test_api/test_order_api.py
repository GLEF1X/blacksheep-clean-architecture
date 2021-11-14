from datetime import datetime
from http import HTTPStatus

import pytest
from blacksheep import Content
from blacksheep.testing import TestClient

from src.application.use_cases.order.dto.order_dto import (
    CreateOrderDto,
    CreateProductDto,
)

pytestmark = pytest.mark.asyncio


async def test_get_order_by_id(insecure_test_client: TestClient, base_api_path: str):
    response = await insecure_test_client.get(base_api_path + "/orders/1")
    assert response.status == HTTPStatus.OK


async def test_create_new_order(insecure_test_client: TestClient, base_api_path: str):
    content = Content(
        content_type=b"application/json",
        data=bytes(
            CreateOrderDto(
                products=[CreateProductDto(id=1, quantity=2)], order_date=datetime.now()
            ).json(),
            "utf-8",
        ),
    )
    response = await insecure_test_client.put(
        base_api_path + "/orders/create", content=content
    )
    assert response.status == HTTPStatus.CREATED
