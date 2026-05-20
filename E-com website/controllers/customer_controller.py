from sqlalchemy.ext.asyncio import AsyncSession
from services.customer_service import CustomerService
from schemas.customer import CustomerCreate, CustomerUpdate

class CustomerController:
    def __init__(self, db: AsyncSession):
        self.service = CustomerService(db)

    async def create(self, data: CustomerCreate):
        return await self.service.create_customer(data)

    async def get_one(self, customer_id: str):
        return await self.service.get_customer(customer_id)

    async def get_all(self):
        return await self.service.get_all_customers()

    async def update(self, customer_id: str, data: CustomerUpdate):
        return await self.service.update_customer(customer_id, data)
