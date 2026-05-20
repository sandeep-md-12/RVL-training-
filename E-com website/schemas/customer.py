from pydantic import BaseModel, field_validator
from typing import Optional

VALID_TIERS = {"Regular", "Silver", "Gold"}

class CustomerCreate(BaseModel):
    customer_id: str
    name: str
    email: str
    shipping_address: str
    membership_tier: str = "Regular"

    @field_validator("membership_tier")
    @classmethod
    def tier_must_be_valid(cls, v):
        if v not in VALID_TIERS:
            raise ValueError(f"membership_tier must be one of {VALID_TIERS}")
        return v

class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    shipping_address: Optional[str] = None
    membership_tier: Optional[str] = None

class CustomerResponse(BaseModel):
    customer_id: str
    name: str
    email: str
    shipping_address: str
    loyalty_points: int
    membership_tier: str

    model_config = {"from_attributes": True}
