from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from services.product_service import ProductService
from schemas.product import ProductCreate, ProductUpdate, RestockRequest
from utils.exceptions import ProductNotFoundError, InsufficientStockError
from typing import Optional

class ProductController:
    def __init__(self, db: AsyncSession):
        self.service = ProductService(db)

    async def create(self, data: ProductCreate):
        return await self.service.create_product(data)
    
    async def get_one(self, product_id: str):
        try:
            return await self.service.get_product(product_id)
        except ProductNotFoundError as e:
                raise e

    async def get_all(self):
        return await self.service.get_all_products()

    async def update(self, product_id: str, data: ProductUpdate):
        try:
            return await self.service.update_product(product_id, data)
        except ProductNotFoundError as e:
                raise e
        except ValueError as e:
            raise HTTPException(status_code=422, detail=str(e))

    async def delete(self, product_id: str):
        try:
            await self.service.delete_product(product_id)
            return {"message": f"Product '{product_id}' deleted"}
        except ProductNotFoundError as e:
                raise e

    async def restock(self, product_id: str, data: RestockRequest):
        try:
            return await self.service.restock(product_id, data.quantity)
        except ProductNotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))

    async def search(
        self,
        category: Optional[str],
        min_price: Optional[float],
        max_price: Optional[float],
        name_keyword: Optional[str],
    ):
        return await self.service.search_products(category, min_price, max_price, name_keyword)

    async def low_stock(self, threshold: int):
        return await self.service.get_low_stock(threshold)
