from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from services.cart_service import CartService
from utils.exceptions import ProductNotFoundError, InsufficientStockError

class CartController:
    def __init__(self, db: AsyncSession):
        self.service = CartService(db)

    async def get_cart(self, customer_id: str):
        return await self.service.get_cart(customer_id)

    async def add_item(self, customer_id: str, product_id: str, quantity: int):
        try:
            return await self.service.add_item(customer_id, product_id, quantity)
        except ProductNotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except InsufficientStockError as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def remove_item(self, customer_id: str, product_id: str, quantity: int = None):
        return await self.service.remove_item(customer_id, product_id, quantity)

    async def update_quantity(self, customer_id: str, product_id: str, new_quantity: int):
        try:
            return await self.service.update_quantity(customer_id, product_id, new_quantity)
        except ProductNotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except InsufficientStockError as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def clear_cart(self, customer_id: str):
        return await self.service.clear_cart(customer_id)
