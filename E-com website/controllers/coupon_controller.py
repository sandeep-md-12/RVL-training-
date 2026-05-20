from sqlalchemy.ext.asyncio import AsyncSession
from services.coupon_service import CouponService
from schemas.coupon import CouponCreate, CouponUpdate

class CouponController:
    def __init__(self, db: AsyncSession):
        self.service = CouponService(db)

    async def create(self, data: CouponCreate):
        return await self.service.create_coupon(data)

    async def get_one(self, code: str):
        return await self.service.get_coupon(code)

    async def update(self, code: str, data: CouponUpdate):
        return await self.service.update_coupon(code, data)
