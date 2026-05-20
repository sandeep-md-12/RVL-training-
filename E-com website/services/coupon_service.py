from sqlalchemy.ext.asyncio import AsyncSession
from repositories.coupon_repository import CouponRepository
from models.coupon import Coupon
from schemas.coupon import CouponCreate
from utils.exceptions import InvalidCouponError
from datetime import datetime, timezone
from fastapi import HTTPException

class CouponService:
    def __init__(self, db: AsyncSession):
        self.repo = CouponRepository(db)

    async def create_coupon(self, data: CouponCreate) -> Coupon:
        existing = await self.repo.get_by_code(data.code)
        if existing:
            raise HTTPException(status_code=400, detail="Coupon code already exists")
        coupon = Coupon(**data.model_dump())
        return await self.repo.create(coupon)

    async def get_coupon(self, code: str) -> Coupon:
        coupon = await self.repo.get_by_code(code)
        if not coupon:
            raise HTTPException(status_code=404, detail="Coupon not found")
        return coupon

    async def update_coupon(self, code: str, data) -> Coupon:
        coupon = await self.repo.get_by_code(code)
        if not coupon:
            raise HTTPException(status_code=404, detail="Coupon not found")
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(coupon, field, value)
        return await self.repo.update(coupon)

    async def validate_coupon(self, code: str, order_amount: float) -> Coupon:
        coupon = await self.repo.get_by_code(code)
        if not coupon:
            raise InvalidCouponError("Coupon not found")
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        print("coupon.usage_count >= coupon.usage_limit, ", {coupon.usage_count}, {coupon.usage_limit})
        if coupon.usage_count >= coupon.usage_limit:
            raise InvalidCouponError("Coupon usage limit reached")
        if coupon.expiry_date < now:
            raise InvalidCouponError("Coupon has expired")
        if order_amount < coupon.min_order_amount:
            raise InvalidCouponError(f"Order amount must be at least {coupon.min_order_amount}")
        return coupon

    async def use_coupon(self, code: str) -> Coupon:
        coupon = await self.repo.get_by_code(code)
        if not coupon:
            raise InvalidCouponError("Coupon not found")
        coupon.usage_count += 1
        return await self.repo.update(coupon)
