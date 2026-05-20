from sqlalchemy.ext.asyncio import AsyncSession
from repositories.customer_repository import CustomerRepository
from models.customer import Customer
from schemas.customer import CustomerCreate, CustomerUpdate
from fastapi import HTTPException

class CustomerService:
    def __init__(self, db: AsyncSession):
        self.repo = CustomerRepository(db)

    async def create_customer(self, data: CustomerCreate) -> Customer:
        existing = await self.repo.get_by_email(data.email)
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")
        existing_id = await self.repo.get_by_id(data.customer_id)
        if existing_id:
            raise HTTPException(status_code=400, detail="Customer ID already exists")
        customer = Customer(**data.model_dump())
        return await self.repo.create(customer)

    async def get_customer(self, customer_id: str) -> Customer:
        customer = await self.repo.get_by_id(customer_id)
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        return customer

    async def get_all_customers(self):
        return await self.repo.get_all()

    async def update_customer(self, customer_id: str, data: CustomerUpdate) -> Customer:
        customer = await self.repo.get_by_id(customer_id)
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(customer, field, value)
        return await self.repo.update(customer)

    def _calc_loyalty_points(self, amount_spent: float, tier: str) -> int:
        points = int(amount_spent // 10)
        if tier == "Gold":
            points = int(points * 1.5)
        return points

    async def add_loyalty_points(self, customer_id: str, amount_spent: float) -> Customer:
        customer = await self.repo.get_by_id(customer_id)
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        customer.loyalty_points += self._calc_loyalty_points(amount_spent, customer.membership_tier)
        return await self.repo.update(customer)
