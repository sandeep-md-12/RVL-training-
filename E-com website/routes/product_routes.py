from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from utils.database import get_db
from controllers.product_controller import ProductController
from schemas.product import ProductCreate, ProductUpdate, ProductResponse, RestockRequest
from typing import List, Optional

router = APIRouter(prefix="/products", tags=["Products"])

@router.post("/", response_model=ProductResponse, status_code=201)
async def create_product(data: ProductCreate, db: AsyncSession = Depends(get_db)):
    return await ProductController(db).create(data)

@router.get("/search", response_model=List[ProductResponse])
async def search_products(
    category: Optional[str] = Query(None),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    name_keyword: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    return await ProductController(db).search(category, min_price, max_price, name_keyword)

@router.get("/low-stock", response_model=List[ProductResponse])
async def low_stock(threshold: int = Query(10), db: AsyncSession = Depends(get_db)):
    return await ProductController(db).low_stock(threshold)

@router.get("/", response_model=List[ProductResponse])
async def get_all_products(db: AsyncSession = Depends(get_db)):
    return await ProductController(db).get_all()

@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: str, db: AsyncSession = Depends(get_db)):
    return await ProductController(db).get_one(product_id)

@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(product_id: str, data: ProductUpdate, db: AsyncSession = Depends(get_db)):
    return await ProductController(db).update(product_id, data)

@router.delete("/{product_id}")
async def delete_product(product_id: str, db: AsyncSession = Depends(get_db)):
    return await ProductController(db).delete(product_id)

@router.post("/{product_id}/restock", response_model=ProductResponse)
async def restock_product(product_id: str, data: RestockRequest, db: AsyncSession = Depends(get_db)):
    return await ProductController(db).restock(product_id, data)
