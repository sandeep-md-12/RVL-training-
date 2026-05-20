from fastapi import HTTPException


class InsufficientStockError(Exception):
    pass

class InvalidCouponError(Exception):
    pass

class OrderAlreadyConfirmedError(Exception):
    pass

class ProductNotFoundError(Exception):
    pass