from __future__ import annotations

from datetime import datetime
from typing import List

from pydantic import BaseModel, PositiveInt, Field, PositiveFloat

from entities.models.product import Product

GREATER_THAN_1 = 1


class ObtainedProductDto(BaseModel, Product):
    pass


class CreateProductDto(BaseModel):
    id: PositiveInt
    quantity: int = Field(..., ge=GREATER_THAN_1)


class ObtainedOrderDto(BaseModel):
    id: PositiveInt
    products: List[ObtainedProductDto]
    total: PositiveFloat
    order_date: datetime
    created_at: datetime


class CreateOrderDto(BaseModel):
    products: List[CreateProductDto]
    order_date: datetime
