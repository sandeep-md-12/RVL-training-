from pydantic import BaseModel, field_validator, model_validator
from typing import Optional

class ProductCreate(BaseModel):
    product_id: str
    name: str
    price: float
    stock_quantity: int
    category: str
    description: Optional[str] = ""
    is_discounted: bool = False
    discount_percentage: float = 0.0

    @field_validator("price")
    @classmethod
    def price_must_be_positive(cls, v):
        if v < 0:
            raise ValueError("Price cannot be negative")
        return v

    @field_validator("stock_quantity")
    @classmethod
    def stock_must_be_non_negative(cls, v):
        if v < 0:
            raise ValueError("Stock quantity cannot be negative")
        return v

    @model_validator(mode="after")
    def validate_discount(self):
        if not self.is_discounted and self.discount_percentage != 0.0:
            raise ValueError("discount_percentage can only be set when is_discounted is True")
        if self.is_discounted:
            if not (0 < self.discount_percentage <= 100):
                raise ValueError("discount_percentage must be between 1 and 100 when is_discounted is True")
        return self

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    stock_quantity: Optional[int] = None
    category: Optional[str] = None
    description: Optional[str] = None
    is_discounted: Optional[bool] = None
    discount_percentage: Optional[float] = None

    @model_validator(mode="after")
    def validate_discount(self):
        if self.is_discounted is False and self.discount_percentage is not None:
            raise ValueError("discount_percentage can only be set when is_discounted is True")
        if self.is_discounted is True and self.discount_percentage is not None:
            if not (0 < self.discount_percentage <= 100):
                raise ValueError("discount_percentage must be between 1 and 100")
        return self

class ProductResponse(BaseModel):
    product_id: str
    name: str
    price: float
    stock_quantity: int
    category: str
    description: str
    is_discounted: bool
    discount_percentage: float
    effective_price: float

    model_config = {"from_attributes": True}

class RestockRequest(BaseModel):
    quantity: int

class SearchQuery(BaseModel):
    category: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    name_keyword: Optional[str] = None
