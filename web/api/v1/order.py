from __future__ import annotations

from fastapi import APIRouter, Path, Body

router = APIRouter(prefix="/orders")


@router.get("/get/{order_id}")
async def get_orders(order_id: str = Path(..., alias="orderId")):
    pass


@router.get("/create")
async def add_order(order_dto: OrderDto = Body(...)):
    pass
