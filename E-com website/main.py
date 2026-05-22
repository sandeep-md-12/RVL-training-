from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from utils.database import init_db
from routes.product_routes import router as product_router
from routes.customer_routes import router as customer_router
from routes.coupon_routes import router as coupon_router
from routes.cart_routes import router as cart_router
from routes.order_routes import router as order_router
from routes.auth_routes import router as auth_router
from utils.exceptions import (
    InsufficientStockError, InvalidCouponError,
    OrderAlreadyConfirmedError, ProductNotFoundError
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(title="E-Commerce API", version="1.0.0", lifespan=lifespan)

# Global exception handlers
@app.exception_handler(ProductNotFoundError)
async def product_not_found_handler(request: Request, exc: ProductNotFoundError):
    return JSONResponse(status_code=404, content={"detail": str(exc)})

@app.exception_handler(InsufficientStockError)
async def insufficient_stock_handler(request: Request, exc: InsufficientStockError):
    return JSONResponse(status_code=400, content={"detail": str(exc)})

@app.exception_handler(InvalidCouponError)
async def invalid_coupon_handler(request: Request, exc: InvalidCouponError):
    return JSONResponse(status_code=400, content={"detail": str(exc)})

@app.exception_handler(OrderAlreadyConfirmedError)
async def order_confirmed_handler(request: Request, exc: OrderAlreadyConfirmedError):
    return JSONResponse(status_code=400, content={"detail": str(exc)})

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"detail": "An unexpected error occurred"})

# Register routers
app.include_router(product_router)
app.include_router(customer_router)
app.include_router(coupon_router)
app.include_router(cart_router)
app.include_router(order_router)
app.include_router(auth_router)

@app.get("/", tags=["Health"])
async def root():
    return {"status": "ok", "message": "E-Commerce API is running"}

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="127.0.0.1", port=8000)

