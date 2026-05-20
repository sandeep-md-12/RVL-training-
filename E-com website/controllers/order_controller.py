from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from services.order_service import OrderService
from utils.exceptions import InsufficientStockError, OrderAlreadyConfirmedError, InvalidCouponError

class OrderController:
    def __init__(self, db: AsyncSession):
        self.service = OrderService(db)

    async def create_order(self, customer_id: str):
        return await self.service.create_order(customer_id)

    async def apply_coupon(self, order_id: str, coupon_code: str):
        try:
            return await self.service.apply_coupon(order_id, coupon_code)
        except InvalidCouponError as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def confirm_order(self, order_id: str):
        try:
            return await self.service.confirm_order(order_id)
        except InsufficientStockError as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def cancel_order(self, order_id: str):
        try:
            return await self.service.cancel_order(order_id)
        except OrderAlreadyConfirmedError as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def get_order(self, order_id: str):
        return await self.service.get_order(order_id)

    async def get_customer_orders(self, customer_id: str):
        return await self.service.get_customer_orders(customer_id)

    async def get_order_summary(self, order_id: str):
        return await self.service.get_order_summary(order_id)
