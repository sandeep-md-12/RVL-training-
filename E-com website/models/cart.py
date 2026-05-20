from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from utils.database import Base

class Cart(Base):
    __tablename__ = "carts"

    cart_id = Column(String, primary_key=True, index=True)
    customer_id = Column(String, ForeignKey("customers.customer_id"), nullable=False, unique=True)

    items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")
    customer = relationship("Customer")

class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(String, primary_key=True, index=True)
    cart_id = Column(String, ForeignKey("carts.cart_id"), nullable=False)
    product_id = Column(String, ForeignKey("products.product_id"), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)

    cart = relationship("Cart", back_populates="items")
    product = relationship("Product")
