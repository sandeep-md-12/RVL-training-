from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.product import Product
from typing import Optional, List

class ProductRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, product: Product) -> Product:
        self.db.add(product)
        await self.db.commit()
        await self.db.refresh(product)
        return product

    async def get_by_id(self, product_id: str) -> Optional[Product]:
        result = await self.db.execute(select(Product).where(Product.product_id == product_id))
        return result.scalar_one_or_none()

    async def get_all(self) -> List[Product]:
        result = await self.db.execute(select(Product))
        return result.scalars().all()

    async def update(self, product: Product) -> Product:
        await self.db.commit()
        await self.db.refresh(product)
        return product

    async def delete(self, product: Product):
        await self.db.delete(product)
        await self.db.commit()

    async def search(
        self,
        category: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        name_keyword: Optional[str] = None
    ) -> List[Product]:
        query = select(Product)
        if category:
            query = query.where(Product.category == category)
        if min_price is not None:
            query = query.where(Product.price >= min_price)
        if max_price is not None:
            query = query.where(Product.price <= max_price)
        if name_keyword:
            query = query.where(Product.name.ilike(f"%{name_keyword}%"))
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_low_stock(self, threshold: int = 10) -> List[Product]:
        result = await self.db.execute(select(Product).where(Product.stock_quantity < threshold))
        return result.scalars().all()
