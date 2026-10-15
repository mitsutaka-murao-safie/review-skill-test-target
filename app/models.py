from typing import List, Optional

from pydantic import BaseModel, Field


class OrderItemIn(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)


class OrderIn(BaseModel):
    items: List[OrderItemIn] = Field(min_length=1)
    coupon_code: Optional[str] = None


class OrderItemOut(BaseModel):
    product_id: int
    quantity: int
    unit_price: int


class OrderOut(BaseModel):
    id: int
    status: str
    subtotal: int
    discount: int
    total: int
    coupon_code: Optional[str]
    created_at: str
    items: List[OrderItemOut]


class ProductOut(BaseModel):
    id: int
    name: str
    price: int
    stock: int
