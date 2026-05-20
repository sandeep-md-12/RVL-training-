from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from utils.database import get_db
from controllers.order_controller import OrderController
from schemas.order import OrderResponse, OrderSummaryResponse
from schemas.coupon import ApplyCouponRequest
from typing import List

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.post("/{customer_id}", response_model=OrderResponse, status_code=201)
async def create_order(customer_id: str, db: AsyncSession = Depends(get_db)):
    return await OrderController(db).create_order(customer_id)

@router.get("/customer/{customer_id}", response_model=List[OrderResponse])
async def get_customer_orders(customer_id: str, db: AsyncSession = Depends(get_db)):
    return await OrderController(db).get_customer_orders(customer_id)

@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(order_id: str, db: AsyncSession = Depends(get_db)):
    return await OrderController(db).get_order(order_id)

@router.post("/{order_id}/apply-coupon", response_model=OrderResponse)
async def apply_coupon(order_id: str, data: ApplyCouponRequest, db: AsyncSession = Depends(get_db)):
    return await OrderController(db).apply_coupon(order_id, data.coupon_code)

@router.post("/{order_id}/confirm", response_model=OrderResponse)
async def confirm_order(order_id: str, db: AsyncSession = Depends(get_db)):
    return await OrderController(db).confirm_order(order_id)

@router.post("/{order_id}/cancel", response_model=OrderResponse)
async def cancel_order(order_id: str, db: AsyncSession = Depends(get_db)):
    return await OrderController(db).cancel_order(order_id)

@router.get("/{order_id}/summary", response_model=OrderSummaryResponse)
async def get_order_summary(order_id: str, db: AsyncSession = Depends(get_db)):
    summary = await OrderController(db).get_order_summary(order_id)
    return {"summary": summary}
