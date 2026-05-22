from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from utils.database import get_db
from controllers.order_controller import OrderController
from schemas.order import OrderResponse, OrderSummaryResponse
from schemas.coupon import ApplyCouponRequest
from dependencies import get_current_user, require_admin
from models.user import User
from typing import List

router = APIRouter(prefix="/orders", tags=["Orders"])


# ── Customer: create an order (attaches user_id from JWT) ───────────────────

@router.post("/", response_model=OrderResponse, status_code=201)
async def create_order(
    customer_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create an order for *customer_id*.

    The ``user_id`` from the JWT is stored on the order so ownership can be
    verified later.  A customer may only create orders for themselves.
    """
    if current_user.role == "customer" and current_user.user_id != customer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only create orders for your own account",
        )
    return await OrderController(db).create_order(customer_id, current_user.user_id)


# ── Customer: view their own orders ─────────────────────────────────────────

@router.get("/mine", response_model=List[OrderResponse])
async def get_my_orders(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Return all orders that belong to the currently authenticated user."""
    return await OrderController(db).get_orders_by_user(current_user.user_id)


# ── Admin: view all orders ───────────────────────────────────────────────────

@router.get("/", response_model=List[OrderResponse],
            dependencies=[Depends(require_admin)])
async def get_all_orders(db: AsyncSession = Depends(get_db)):
    """Admin only — returns every order in the system."""
    return await OrderController(db).get_all_orders()


# ── Admin or owner: view a specific order ───────────────────────────────────

@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    order = await OrderController(db).get_order(order_id)
    # Customers may only view their own orders
    if current_user.role == "customer" and order.get("owner_user_id") != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this order",
        )
    return order


# ── Logged-in user: apply coupon ─────────────────────────────────────────────

@router.post("/{order_id}/apply-coupon", response_model=OrderResponse)
async def apply_coupon(
    order_id: str,
    data: ApplyCouponRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    order = await OrderController(db).get_order(order_id)
    if current_user.role == "customer" and order.get("owner_user_id") != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to modify this order",
        )
    return await OrderController(db).apply_coupon(order_id, data.coupon_code)


# ── Logged-in user: confirm order ────────────────────────────────────────────

@router.post("/{order_id}/confirm", response_model=OrderResponse)
async def confirm_order(
    order_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    order = await OrderController(db).get_order(order_id)
    if current_user.role == "customer" and order.get("owner_user_id") != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to confirm this order",
        )
    return await OrderController(db).confirm_order(order_id)


# ── Logged-in user: cancel order ─────────────────────────────────────────────

@router.post("/{order_id}/cancel", response_model=OrderResponse)
async def cancel_order(
    order_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    order = await OrderController(db).get_order(order_id)
    if current_user.role == "customer" and order.get("owner_user_id") != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to cancel this order",
        )
    return await OrderController(db).cancel_order(order_id)


# ── Logged-in user: order summary ────────────────────────────────────────────

@router.get("/{order_id}/summary", response_model=OrderSummaryResponse)
async def get_order_summary(
    order_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    order = await OrderController(db).get_order(order_id)
    if current_user.role == "customer" and order.get("owner_user_id") != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this order",
        )
    summary = await OrderController(db).get_order_summary(order_id)
    return {"summary": summary}


# ── Admin: get orders by customer_id ─────────────────────────────────────────

@router.get("/customer/{customer_id}", response_model=List[OrderResponse],
            dependencies=[Depends(require_admin)])
async def get_customer_orders(customer_id: str, db: AsyncSession = Depends(get_db)):
    """Admin only — returns all orders for a given customer."""
    return await OrderController(db).get_customer_orders(customer_id)
