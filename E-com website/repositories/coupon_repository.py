from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.coupon import Coupon
from typing import Optional

class CouponRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, coupon: Coupon) -> Coupon:
        self.db.add(coupon)
        await self.db.commit()
        await self.db.refresh(coupon)
        return coupon

    async def get_by_code(self, code: str) -> Optional[Coupon]:
        result = await self.db.execute(select(Coupon).where(Coupon.code == code))
        return result.scalar_one_or_none()

    async def update(self, coupon: Coupon) -> Coupon:
        await self.db.commit()
        await self.db.refresh(coupon)
        return coupon
