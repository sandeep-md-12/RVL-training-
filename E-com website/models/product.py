from sqlalchemy import Column, String, Float, Integer, Boolean
from utils.database import Base
from utils.exceptions import InsufficientStockError

class Product(Base):
    __tablename__ = "products"

    product_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    _price = Column("price", Float, nullable=False)
    _stock_quantity = Column("stock_quantity", Integer, nullable=False, default=0)
    category = Column(String, nullable=False)
    description = Column(String, default="")
    is_discounted = Column(Boolean, default=False)
    discount_percentage = Column(Float, default=0.0)

    @property
    def price(self) -> float:
        return self._price

    @price.setter
    def price(self, value: float):
        if value < 0:
            raise ValueError("Price cannot be negative")
        self._price = value

    @property
    def stock_quantity(self) -> int:
        return self._stock_quantity

    @stock_quantity.setter
    def stock_quantity(self, value: int):
        if value < 0:
            raise InsufficientStockError("Stock quantity cannot fall below 0")
        self._stock_quantity = value

    def reduce_stock(self, quantity: int):
        if self._stock_quantity < quantity:
            raise InsufficientStockError(f"Insufficient stock for '{self.name}'")
        self.stock_quantity = self._stock_quantity - quantity

    def increase_stock(self, quantity: int):
        self.stock_quantity = self._stock_quantity + quantity

    def is_available(self, quantity: int = 1) -> bool:
        return self._stock_quantity >= quantity

    def __eq__(self, other):
        if not isinstance(other, Product):
            return False
        return self.product_id == other.product_id

    def __hash__(self):
        return hash(self.product_id)

    def __str__(self):
        return f"Product({self.product_id} | {self.name} | {self.price} | stock={self.stock_quantity})"

    def __repr__(self):
        return f"<Product product_id={self.product_id} name={self.name} price={self.price}>"
