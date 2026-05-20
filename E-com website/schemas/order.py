from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class OrderItemResponse(BaseModel):
    product_id: str
    product_name: str
    unit_price: float
    quantity: int
    subtotal: float

    model_config = {"from_attributes": True}

class OrderResponse(BaseModel):
    order_id: str
    customer_id: str
    total_amount: float
    order_date: datetime
    status: str
    payment_status: str
    shipping_address: str
    applied_coupon_code: Optional[str]
    items: List[OrderItemResponse]

    model_config = {"from_attributes": True}

class OrderSummaryResponse(BaseModel):
    summary: str
