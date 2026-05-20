from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from utils.database import get_db
from controllers.coupon_controller import CouponController
from schemas.coupon import CouponCreate, CouponUpdate, CouponResponse

router = APIRouter(prefix="/coupons", tags=["Coupons"])

@router.post("/", response_model=CouponResponse, status_code=201)
async def create_coupon(data: CouponCreate, db: AsyncSession = Depends(get_db)):
    return await CouponController(db).create(data)

@router.get("/{code}", response_model=CouponResponse)
async def get_coupon(code: str, db: AsyncSession = Depends(get_db)):
    return await CouponController(db).get_one(code)

@router.put("/{code}", response_model=CouponResponse)
async def update_coupon(code: str, data: CouponUpdate, db: AsyncSession = Depends(get_db)):
    return await CouponController(db).update(code, data)
