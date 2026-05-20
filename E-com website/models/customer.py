from sqlalchemy import Column, String, Integer
from utils.database import Base

class Customer(Base):
    __tablename__ = "customers"

    customer_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    shipping_address = Column(String, nullable=False)
    loyalty_points = Column(Integer, default=0)
    membership_tier = Column(String, default="Regular")  # Regular, Silver, Gold
