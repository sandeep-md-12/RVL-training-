from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional

class CouponCreate(BaseModel):
    code: str
    discount_type: str  # percentage or fixed
    value: float
    min_order_amount: float = 0.0
    expiry_date: datetime
    usage_limit: int

    @field_validator("discount_type")
    @classmethod
    def type_must_be_valid(cls, v):
        if v not in {"percentage", "fixed"}:
            raise ValueError("discount_type must be 'percentage' or 'fixed'")
        return v

    @field_validator("value")
    @classmethod
    def value_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Coupon value must be positive")
        return v

class CouponResponse(BaseModel):
    code: str
    discount_type: str
    value: float
    min_order_amount: float
    expiry_date: datetime
    usage_limit: int
    usage_count: int

    model_config = {"from_attributes": True}

class CouponUpdate(BaseModel):
    discount_type: Optional[str] = None
    value: Optional[float] = None
    min_order_amount: Optional[float] = None
    expiry_date: Optional[datetime] = None
    usage_limit: Optional[int] = None

    @field_validator("discount_type")
    @classmethod
    def type_must_be_valid(cls, v):
        if v is not None and v not in {"percentage", "fixed"}:
            raise ValueError("discount_type must be 'percentage' or 'fixed'")
        return v

    @field_validator("value")
    @classmethod
    def value_must_be_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError("Coupon value must be positive")
        return v

class ApplyCouponRequest(BaseModel):
    coupon_code: str
