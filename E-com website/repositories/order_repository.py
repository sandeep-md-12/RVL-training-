from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from models.order import Order, OrderItem
from typing import Optional, List

class OrderRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, order: Order) -> Order:
        self.db.add(order)
        await self.db.commit()
        return order
    
    async def get_by_id(self, order_id: str) -> Optional[Order]:
        result = await self.db.execute(
            select(Order)
            .where(Order.order_id == order_id)
            .options(selectinload(Order.items), selectinload(Order.customer), selectinload(Order.coupon))
        )
        return result.scalar_one_or_none()
    
    async def get_by_customer(self, customer_id: str) -> List[Order]:
        result = await self.db.execute(
            select(Order)
            .where(Order.customer_id == customer_id)
            .options(selectinload(Order.items))
        )
        return result.scalars().all()

    async def update(self, order: Order) -> Order:
        await self.db.commit()
        await self.db.refresh(order)
        return order

    async def get_by_owner_user(self, owner_user_id: str) -> List[Order]:
        """Return all orders created by a specific user (JWT owner_user_id)."""
        result = await self.db.execute(
            select(Order)
            .where(Order.owner_user_id == owner_user_id)
            .options(selectinload(Order.items))
        )
        return result.scalars().all()

    async def get_all(self) -> List[Order]:
        """Return every order in the system."""
        result = await self.db.execute(
            select(Order).options(selectinload(Order.items))
        )
        return result.scalars().all()
