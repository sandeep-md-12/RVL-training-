from sqlalchemy.ext.asyncio import AsyncSession
from repositories.product_repository import ProductRepository
from models.product import Product
from schemas.product import ProductCreate, ProductUpdate
from utils.exceptions import ProductNotFoundError, InsufficientStockError
from fastapi import HTTPException
from typing import Optional, List

def _effective_price(product: Product) -> float:
    if product.is_discounted and product.discount_percentage > 0:
        return round(product.price * (1 - product.discount_percentage / 100), 2)
    return product.price

def _to_response(product: Product) -> dict:
    return {
        "product_id": product.product_id,
        "name": product.name,
        "price": product.price,
        "stock_quantity": product.stock_quantity,
        "category": product.category,
        "description": product.description or "",
        "is_discounted": product.is_discounted,
        "discount_percentage": product.discount_percentage,
        "effective_price": _effective_price(product),
    }

class ProductService:
    def __init__(self, db: AsyncSession):
        self.repo = ProductRepository(db)

    async def create_product(self, data: ProductCreate) -> dict:
        product = Product(**data.model_dump())
        created = await self.repo.create(product)
        return _to_response(created)

    async def get_product(self, product_id: str) -> dict:
        product = await self.repo.get_by_id(product_id)
        if not product:
            raise ProductNotFoundError(f"Product '{product_id}' not found")
        return _to_response(product)

    async def get_all_products(self) -> List[dict]:
        products = await self.repo.get_all()
        return [_to_response(p) for p in products]

    async def update_product(self, product_id: str, data: ProductUpdate) -> dict:
        product = await self.repo.get_by_id(product_id)
        if not product:
            raise ProductNotFoundError(f"Product '{product_id}' not found")
        for field, value in data.model_dump(exclude_none=True).items():
            if field == "price" and value < 0:
                raise HTTPException(status_code=422, detail="Price cannot be negative")
            setattr(product, field, value)
        if not product.is_discounted:
            product.discount_percentage = 0.0
        updated = await self.repo.update(product)
        return _to_response(updated)

    async def delete_product(self, product_id: str):
        product = await self.repo.get_by_id(product_id)
        if not product:
            raise ProductNotFoundError(f"Product '{product_id}' not found")
        await self.repo.delete(product)

    async def restock(self, product_id: str, quantity: int) -> dict:
        product = await self.repo.get_by_id(product_id)
        if not product:
            raise ProductNotFoundError(f"Product '{product_id}' not found")
        product.stock_quantity += quantity
        updated = await self.repo.update(product)
        return _to_response(updated)

    async def search_products(
        self,
        category: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        name_keyword: Optional[str] = None
    ) -> List[dict]:
        products = await self.repo.search(category, min_price, max_price, name_keyword)
        return [_to_response(p) for p in products]

    async def get_low_stock(self, threshold: int = 10) -> List[dict]:
        products = await self.repo.get_low_stock(threshold)
        return [_to_response(p) for p in products]

    async def reduce_stock(self, product_id: str, quantity: int):
        product = await self.repo.get_by_id(product_id)
        if not product:
            raise ProductNotFoundError(f"Product '{product_id}' not found")
        if product.stock_quantity < quantity:
            raise InsufficientStockError(f"Insufficient stock for '{product.name}'")
        product.stock_quantity -= quantity
        await self.repo.update(product)

    async def increase_stock(self, product_id: str, quantity: int):
        product = await self.repo.get_by_id(product_id)
        if not product:
            raise ProductNotFoundError(f"Product '{product_id}' not found")
        product.stock_quantity += quantity
        await self.repo.update(product)
