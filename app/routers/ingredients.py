from typing import List
from fastapi import HTTPException, APIRouter
from app.core.db import data_manager
from app.models.ingredient import IngredientInfo

router = APIRouter(prefix="/ingredients", tags=["ingredients"])

@router.get("", response_model=List[IngredientInfo])
async def get_all_ingredients():
    """Get all ingredients"""
    return data_manager.get_all_ingredients()

@router.get("/{ingredient_id}", response_model=IngredientInfo)
async def get_ingredient(ingredient_id: int):
    """Get specific ingredient by ID"""
    ingredient = data_manager.get_ingredient_by_id(ingredient_id)
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    return ingredient