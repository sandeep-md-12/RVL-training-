from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from utils.database import get_db
from controllers.customer_controller import CustomerController
from schemas.customer import CustomerCreate, CustomerUpdate, CustomerResponse
from typing import List

router = APIRouter(prefix="/customers", tags=["Customers"])

@router.post("/", response_model=CustomerResponse, status_code=201)
async def create_customer(data: CustomerCreate, db: AsyncSession = Depends(get_db)):
    return await CustomerController(db).create(data)

@router.get("/", response_model=List[CustomerResponse])
async def get_all_customers(db: AsyncSession = Depends(get_db)):
    return await CustomerController(db).get_all()

@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(customer_id: str, db: AsyncSession = Depends(get_db)):
    return await CustomerController(db).get_one(customer_id)

@router.put("/{customer_id}", response_model=CustomerResponse)
async def update_customer(customer_id: str, data: CustomerUpdate, db: AsyncSession = Depends(get_db)):
    return await CustomerController(db).update(customer_id, data)
