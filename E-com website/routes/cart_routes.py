from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from utils.database import get_db
from controllers.cart_controller import CartController
from schemas.cart import CartItemAdd, CartItemRemove, CartItemUpdate, CartResponse
from dependencies import get_current_user

router = APIRouter(prefix="/cart", tags=["Cart"])


# All cart operations require a logged-in user
@router.get("/{customer_id}", response_model=CartResponse,
            dependencies=[Depends(get_current_user)])
async def get_cart(customer_id: str, db: AsyncSession = Depends(get_db)):
    return await CartController(db).get_cart(customer_id)


@router.post("/{customer_id}/add", response_model=CartResponse,
             dependencies=[Depends(get_current_user)])
async def add_item(customer_id: str, data: CartItemAdd, db: AsyncSession = Depends(get_db)):
    return await CartController(db).add_item(customer_id, data.product_id, data.quantity)


@router.post("/{customer_id}/remove", response_model=CartResponse,
             dependencies=[Depends(get_current_user)])
async def remove_item(customer_id: str, data: CartItemRemove, db: AsyncSession = Depends(get_db)):
    return await CartController(db).remove_item(customer_id, data.product_id, data.quantity)


@router.put("/{customer_id}/update", response_model=CartResponse,
            dependencies=[Depends(get_current_user)])
async def update_quantity(customer_id: str, data: CartItemUpdate, db: AsyncSession = Depends(get_db)):
    return await CartController(db).update_quantity(customer_id, data.product_id, data.new_quantity)


@router.delete("/{customer_id}/clear", response_model=CartResponse,
               dependencies=[Depends(get_current_user)])
async def clear_cart(customer_id: str, db: AsyncSession = Depends(get_db)):
    return await CartController(db).clear_cart(customer_id)
