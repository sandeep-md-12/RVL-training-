from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from models.cart import Cart, CartItem
from typing import Optional

class CartRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_customer(self, customer_id: str) -> Optional[Cart]:
        result = await self.db.execute(
            select(Cart)
            .where(Cart.customer_id == customer_id)
            .options(selectinload(Cart.items).selectinload(CartItem.product))
        )
        return result.scalar_one_or_none()

    async def create(self, cart: Cart) -> Cart:
        self.db.add(cart)
        await self.db.commit()
        await self.db.refresh(cart)
        return cart

    async def get_cart_item(self, cart_id: str, product_id: str) -> Optional[CartItem]:
        result = await self.db.execute(
            select(CartItem).where(
                CartItem.cart_id == cart_id,
                CartItem.product_id == product_id
            )
        )
        return result.scalar_one_or_none()

    async def add_item(self, item: CartItem) -> CartItem:
        self.db.add(item)
        await self.db.commit()
        await self.db.refresh(item)
        return item

    async def update(self) -> None:
        await self.db.commit()

    async def delete_item(self, item: CartItem) -> None:
        await self.db.delete(item)
        await self.db.commit()

    async def clear_cart(self, cart: Cart) -> None:
        for item in cart.items:
            await self.db.delete(item)
        await self.db.commit()
