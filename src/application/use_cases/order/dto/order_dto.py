from __future__ import annotations

from datetime import datetime
from typing import List

from pydantic import BaseModel, Field, PositiveFloat, PositiveInt


class ObtainedProductDto(BaseModel):
    price: float
    weight: int
    id: int


class UserDto(BaseModel):
    id: int
    username: str


class CreateProductDto(BaseModel):
    id: PositiveInt
    quantity: int = Field(..., ge=1)


class ObtainedOrderDto(BaseModel):
    id: PositiveInt
    products: List[ObtainedProductDto]
    total: PositiveFloat
    order_date: datetime
    created_at: datetime
    customer: UserDto


class CreateOrderDto(BaseModel):
    products: List[CreateProductDto]
    order_date: datetime
    customer_id: int
