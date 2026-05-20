from sqlalchemy import Column, String, Float, Integer, DateTime
from utils.database import Base

class Coupon(Base):
    __tablename__ = "coupons"

    code = Column(String, primary_key=True, index=True)
    discount_type = Column(String, nullable=False)  # percentage or fixed
    value = Column(Float, nullable=False)
    min_order_amount = Column(Float, default=0.0)
    expiry_date = Column(DateTime, nullable=False)
    usage_limit = Column(Integer, nullable=False)
    usage_count = Column(Integer, default=0)
