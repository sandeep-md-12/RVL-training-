from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.customer import Customer
from typing import Optional, List

class CustomerRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, customer: Customer) -> Customer:
        self.db.add(customer)
        await self.db.commit()
        await self.db.refresh(customer)
        return customer

    async def get_by_id(self, customer_id: str) -> Optional[Customer]:
        result = await self.db.execute(select(Customer).where(Customer.customer_id == customer_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[Customer]:
        result = await self.db.execute(select(Customer).where(Customer.email == email))
        return result.scalar_one_or_none()

    async def get_all(self) -> List[Customer]:
        result = await self.db.execute(select(Customer))
        return result.scalars().all()

    async def update(self, customer: Customer) -> Customer:
        await self.db.commit()
        await self.db.refresh(customer)
        return customer
