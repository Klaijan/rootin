from typing import List
from fastapi import APIRouter, HTTPException

from app.core.db import data_manager
from app.models.product import ProductInfo

router = APIRouter(prefix="/products", tags=["products"])

@router.get("", response_model=List[ProductInfo])
async def get_all_products():
    """Get all products"""
    return data_manager.get_all_products()

@router.get("/{product_id}", response_model=ProductInfo)
async def get_product(product_id: int):
    """Get specific product by ID"""
    product = data_manager.get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product