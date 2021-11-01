import pytest
from blacksheep.testing import TestClient
from dynaconf import LazySettings

pytestmark = pytest.mark.asyncio


class TestOrderApi:
    async def test_get_order_by_id(
        self, test_client: TestClient, settings: LazySettings
    ) -> None:
        response = await test_client.get(settings.web.api_path + "/orders/get/1")
        assert response.status == 200
