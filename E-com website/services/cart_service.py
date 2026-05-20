import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from repositories.cart_repository import CartRepository
from repositories.product_repository import ProductRepository
from models.cart import Cart, CartItem
from utils.exceptions import ProductNotFoundError, InsufficientStockError
from fastapi import HTTPException
from services.product_service import _effective_price

class CartService:
    def __init__(self, db: AsyncSession):
        self.repo = CartRepository(db)
        self.product_repo = ProductRepository(db)
    
    async def _get_or_create_cart(self, customer_id: str) -> Cart:
        cart = await self.repo.get_by_customer(customer_id)
        if not cart:
            cart = Cart(cart_id=str(uuid.uuid4()), customer_id=customer_id)
            await self.repo.create(cart)
            cart = await self.repo.get_by_customer(customer_id)
        return cart
        
    async def get_cart(self, customer_id: str) -> dict:
        cart = await self._get_or_create_cart(customer_id)
        return self._format_cart(cart)

    async def add_item(self, customer_id: str, product_id: str, quantity: int = 1) -> dict:
        product = await self.product_repo.get_by_id(product_id)
        if not product:
            raise ProductNotFoundError(f"Product '{product_id}' not found")

        cart = await self._get_or_create_cart(customer_id)
        existing_item = await self.repo.get_cart_item(cart.cart_id, product_id)
        new_qty = (existing_item.quantity if existing_item else 0) + quantity

        if product.stock_quantity < new_qty:
            raise InsufficientStockError(f"Only {product.stock_quantity} units available for '{product.name}'")

        if existing_item:
            existing_item.quantity = new_qty
            await self.repo.update()
        else:
            item = CartItem(
                id=str(uuid.uuid4()),
                cart_id=cart.cart_id,
                product_id=product_id,
                quantity=quantity
            )
            await self.repo.add_item(item)

        return await self.get_cart(customer_id)

    async def remove_item(self, customer_id: str, product_id: str, quantity: int = None) -> dict:
        cart = await self._get_or_create_cart(customer_id)
        item = await self.repo.get_cart_item(cart.cart_id, product_id)
        if not item:
            raise HTTPException(status_code=404, detail="Item not in cart")

        if quantity is None or quantity >= item.quantity:
            await self.repo.delete_item(item)
        else:
            item.quantity -= quantity
            await self.repo.update()

        return await self.get_cart(customer_id)

    async def update_quantity(self, customer_id: str, product_id: str, new_quantity: int) -> dict:
        product = await self.product_repo.get_by_id(product_id)
        if not product:
            raise ProductNotFoundError(f"Product '{product_id}' not found")
        if product.stock_quantity < new_quantity:
            raise InsufficientStockError(f"Only {product.stock_quantity} units available")

        cart = await self._get_or_create_cart(customer_id)
        item = await self.repo.get_cart_item(cart.cart_id, product_id)
        if not item:
            raise HTTPException(status_code=404, detail="Item not in cart")

        if new_quantity <= 0:
            await self.repo.delete_item(item)
        else:
            item.quantity = new_quantity
            await self.repo.update()

        return await self.get_cart(customer_id)

    async def clear_cart(self, customer_id: str) -> dict:
        cart = await self._get_or_create_cart(customer_id)
        await self.repo.clear_cart(cart)
        return await self.get_cart(customer_id)

    def _format_cart(self, cart: Cart) -> dict:
        items = []
        total = 0.0
        item_count = 0
        for ci in cart.items:
            p = ci.product
            ep = _effective_price(p)
            subtotal = round(ep * ci.quantity, 2)
            total += subtotal
            item_count += ci.quantity
            items.append({
                "product": {
                    "product_id": p.product_id,
                    "name": p.name,
                    "price": p.price,
                    "stock_quantity": p.stock_quantity,
                    "category": p.category,
                    "description": p.description or "",
                    "is_discounted": p.is_discounted,
                    "discount_percentage": p.discount_percentage,
                    "effective_price": ep,
                },
                "quantity": ci.quantity,
                "subtotal": subtotal,
            })
        return {
            "cart_id": cart.cart_id,
            "customer_id": cart.customer_id,
            "items": items,
            "total": round(total, 2),
            "item_count": item_count,
        }
