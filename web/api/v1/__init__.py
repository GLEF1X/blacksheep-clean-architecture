from __future__ import annotations

from typing import Optional

from fastapi import APIRouter

from web.api.v1 import order

v1_router = APIRouter(prefix="api/v1")


def install_v1_api(main_router: Optional[APIRouter] = None) -> None:
    if main_router is not None:
        main_router.include_router(v1_router)
    v1_router.include_router(order.router)
