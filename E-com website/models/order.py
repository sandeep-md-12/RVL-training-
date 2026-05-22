from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from utils.database import Base

class Order(Base):
    __tablename__ = "orders"

    order_id = Column(String, primary_key=True, index=True)
    customer_id = Column(String, ForeignKey("customers.customer_id"), nullable=False)
    # user_id from the JWT at the time of order creation — used for ownership checks
    owner_user_id = Column(String, nullable=True)
    total_amount = Column(Float, nullable=False)
    order_date = Column(DateTime, nullable=False)
    status = Column(String, default="pending")           # pending, confirmed, cancelled
    payment_status = Column(String, default="pending")  # pending, paid, failed
    shipping_address = Column(String, nullable=False)
    applied_coupon_code = Column(String, ForeignKey("coupons.code"), nullable=True)

    customer = relationship("Customer")
    coupon = relationship("Coupon")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(String, primary_key=True, index=True)
    order_id = Column(String, ForeignKey("orders.order_id"), nullable=False)
    product_id = Column(String, nullable=False)
    product_name = Column(String, nullable=False)
    unit_price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    subtotal = Column(Float, nullable=False)

    order = relationship("Order", back_populates="items")
