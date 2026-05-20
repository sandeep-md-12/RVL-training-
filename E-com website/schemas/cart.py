from pydantic import BaseModel
from typing import List
from schemas.product import ProductResponse

class CartItemAdd(BaseModel):
    product_id: str
    quantity: int = 1

class CartItemRemove(BaseModel):
    product_id: str
    quantity: int = None

class CartItemUpdate(BaseModel):
    product_id: str
    new_quantity: int

class CartItemResponse(BaseModel):
    product: ProductResponse
    quantity: int
    subtotal: float

    model_config = {"from_attributes": True}

class CartResponse(BaseModel):
    cart_id: str
    customer_id: str
    items: List[CartItemResponse]
    total: float
    item_count: int
