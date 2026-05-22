import uuid
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from repositories.order_repository import OrderRepository
from repositories.cart_repository import CartRepository
from repositories.customer_repository import CustomerRepository
from repositories.product_repository import ProductRepository
from models.order import Order, OrderItem
from services.coupon_service import CouponService
from services.product_service import _effective_price
from utils.exceptions import (
    InsufficientStockError, InvalidCouponError,
    OrderAlreadyConfirmedError, ProductNotFoundError
)
from fastapi import HTTPException

TIER_DISCOUNTS = {"Gold": 0.08, "Silver": 0.05, "Regular": 0.0}

class OrderService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.order_repo = OrderRepository(db)
        self.cart_repo = CartRepository(db)
        self.customer_repo = CustomerRepository(db)
        self.product_repo = ProductRepository(db)
        self.coupon_service = CouponService(db)

    async def create_order(self, customer_id: str, owner_user_id: str = None) -> dict:
        customer = await self.customer_repo.get_by_id(customer_id)
        print ("got customer ", {customer})
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")

        cart = await self.cart_repo.get_by_customer(customer_id)
        print ("got cart ", {cart})
        if not cart or not cart.items:
            raise HTTPException(status_code=400, detail="Cart is empty")

        total = 0.0
        order_items = []
        for ci in cart.items:
            p = ci.product
            ep = _effective_price(p)
            subtotal = round(ep * ci.quantity, 2)
            total += subtotal
            order_items.append(OrderItem(
                id=str(uuid.uuid4()),
                product_id=p.product_id,
                product_name=p.name,
                unit_price=ep,
                quantity=ci.quantity,
                subtotal=subtotal,
            ))

        tier_discount = TIER_DISCOUNTS.get(customer.membership_tier, 0.0)
        total = round(total * (1 - tier_discount), 2)

        order = Order(
            order_id=str(uuid.uuid4()),
            customer_id=customer_id,
            owner_user_id=owner_user_id,
            total_amount=total,
            order_date=datetime.utcnow(),
            status="pending",
            payment_status="pending",
            shipping_address=customer.shipping_address,
            applied_coupon_code=None,
        )
        print ("created order ", {order})
        order.items = order_items
        await self.order_repo.create(order)
        print ("saved order ", {order})
        saved_order = await self.order_repo.get_by_id(order.order_id)
        print ("formatted order ", {saved_order})
        return await self._format_order(saved_order)

    async def apply_coupon(self, order_id: str, coupon_code: str) -> dict:
        order = await self.order_repo.get_by_id(order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        if order.status != "pending":
            raise HTTPException(status_code=400, detail="Can only apply coupon to pending orders")

        coupon = await self.coupon_service.validate_coupon(coupon_code, order.total_amount)

        if coupon.discount_type == "percentage":
            discount = round(order.total_amount * coupon.value / 100, 2)
        else:
            discount = min(coupon.value, order.total_amount)

        order.total_amount = round(order.total_amount - discount, 2)
        order.applied_coupon_code = coupon_code
        await self.coupon_service.use_coupon(coupon_code)
        await self.order_repo.update(order)
        return await self._format_order(order)

    async def confirm_order(self, order_id: str) -> dict:
        order = await self.order_repo.get_by_id(order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        if order.status != "pending":
            raise HTTPException(status_code=400, detail="Order is not in pending state")

        deducted = []
        try:
            for item in order.items:
                product = await self.product_repo.get_by_id(item.product_id)
                if not product:
                    raise ProductNotFoundError(f"Product '{item.product_id}' not found")
                if product.stock_quantity < item.quantity:
                    raise InsufficientStockError(f"Insufficient stock for '{product.name}'")
                product.stock_quantity -= item.quantity
                await self.product_repo.update(product)
                deducted.append((item.product_id, item.quantity))
        except (InsufficientStockError, ProductNotFoundError) as e:
            for pid, qty in deducted:
                p = await self.product_repo.get_by_id(pid)
                if p:
                    p.stock_quantity += qty
                    await self.product_repo.update(p)
            order.status = "pending"
            order.payment_status = "failed"
            await self.order_repo.update(order)
            raise InsufficientStockError(str(e))

        order.status = "confirmed"
        order.payment_status = "paid"
        await self.order_repo.update(order)

        customer = await self.customer_repo.get_by_id(order.customer_id)
        points = int(order.total_amount // 10)
        if customer.membership_tier == "Gold":
            points = int(points * 1.5)
        customer.loyalty_points += points
        await self.customer_repo.update(customer)

        await self.cart_repo.clear_cart(await self.cart_repo.get_by_customer(order.customer_id))
        return await self._format_order(order)

    async def cancel_order(self, order_id: str) -> dict:
        order = await self.order_repo.get_by_id(order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        if order.status == "confirmed":
            raise OrderAlreadyConfirmedError("Cannot cancel a confirmed order")
        if order.status == "cancelled":
            raise HTTPException(status_code=400, detail="Order already cancelled")

        order.status = "cancelled"
        await self.order_repo.update(order)
        return await self._format_order(order)

    async def get_order(self, order_id: str) -> dict:
        order = await self.order_repo.get_by_id(order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        return await self._format_order(order)

    async def get_customer_orders(self, customer_id: str):
        orders = await self.order_repo.get_by_customer(customer_id)
        return [await self._format_order(o) for o in orders]

    async def get_orders_by_user(self, owner_user_id: str):
        """Return all orders whose owner_user_id matches the given user_id."""
        orders = await self.order_repo.get_by_owner_user(owner_user_id)
        return [await self._format_order(o) for o in orders]

    async def get_all_orders(self):
        """Return every order in the system (admin use)."""
        orders = await self.order_repo.get_all()
        return [await self._format_order(o) for o in orders]

    async def get_order_summary(self, order_id: str) -> str:
        order = await self.order_repo.get_by_id(order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        customer = await self.customer_repo.get_by_id(order.customer_id)

        lines = [
            "=" * 50,
            f"ORDER RECEIPT - {order.order_id}",
            "=" * 50,
            f"Date       : {order.order_date.strftime('%Y-%m-%d %H:%M:%S')}",
            f"Customer   : {customer.name} ({customer.membership_tier})",
            f"Ship To    : {order.shipping_address}",
            "-" * 50,
            f"{'Product':<25} {'Qty':>5} {'Unit':>8} {'Sub':>10}",
            "-" * 50,
        ]
        for item in order.items:
            lines.append(f"{item.product_name:<25} {item.quantity:>5} {item.unit_price:>8.2f} {item.subtotal:>10.2f}")

        lines += [
            "-" * 50,
            f"{'Coupon':<35} {order.applied_coupon_code or 'None':>14}",
            f"{'TOTAL':<35} {order.total_amount:>14.2f}",
            f"{'Status':<35} {order.status.upper():>14}",
            f"{'Payment':<35} {order.payment_status.upper():>14}",
            f"{'Loyalty Points':<35} {customer.loyalty_points:>14}",
            "=" * 50,
        ]
        return "\n".join(lines)

    async def _format_order(self, order: Order) -> dict:
        print ("formatting order ", {order.order_id})
        return {
            "order_id": order.order_id,
            "customer_id": order.customer_id,
            "owner_user_id": order.owner_user_id,
            "total_amount": order.total_amount,
            "order_date": order.order_date,
            "status": order.status,
            "payment_status": order.payment_status,
            "shipping_address": order.shipping_address,
            "applied_coupon_code": order.applied_coupon_code,
            "items": [
                {
                    "product_id": i.product_id,
                    "product_name": i.product_name,
                    "unit_price": i.unit_price,
                    "quantity": i.quantity,
                    "subtotal": i.subtotal,
                }
                for i in order.items
            ],
        }
