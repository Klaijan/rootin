from fastapi import APIRouter, HTTPException
from typing import List

from app.models import (
    IngredientInfo, ProductInfo, Routine, InteractionResult, 
    ScoreResult, TreatmentAnalysis
)
from app.db import data_manager
from app.logic import analyzer

router = APIRouter()

# Ingredients endpoints
@router.get("/ingredients", response_model=List[IngredientInfo])
async def get_all_ingredients():
    """Get all ingredients"""
    return data_manager.get_all_ingredients()

@router.get("/ingredients/{ingredient_id}", response_model=IngredientInfo)
async def get_ingredient(ingredient_id: int):
    """Get specific ingredient by ID"""
    ingredient = data_manager.get_ingredient_by_id(ingredient_id)
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    return ingredient

# Products endpoints
@router.get("/products", response_model=List[ProductInfo])
async def get_all_products():
    """Get all products"""
    return data_manager.get_all_products()

@router.get("/products/{product_id}", response_model=ProductInfo)
async def get_product(product_id: int):
    """Get specific product by ID"""
    product = data_manager.get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

# Analysis endpoints
@router.post("/analyze/interactions", response_model=List[InteractionResult])
async def analyze_routine_interactions(routine: Routine):
    """Analyze ingredient interactions in a routine"""
    try:
        return analyzer.analyze_interactions(routine.items)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.post("/analyze/score", response_model=ScoreResult)
async def calculate_routine_score(routine: Routine):
    """Calculate routine category scores"""
    try:
        return analyzer.calculate_routine_score(routine.items)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scoring failed: {str(e)}")

@router.post("/analyze/post-treatment", response_model=TreatmentAnalysis)
async def analyze_post_treatment(treatment_id: int, routine: Routine):
    """Analyze routine safety after treatment"""
    try:
        return analyzer.analyze_post_treatment(treatment_id, routine.items)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Treatment analysis failed: {str(e)}")

# Treatments endpoints
@router.get("/treatments")
async def get_treatments():
    """Get all available treatments"""
    if data_manager.treatments.empty:
        return []
    return data_manager.treatments.to_dict(orient="records")

@router.get("/treatments/{treatment_id}")
async def get_treatment(treatment_id: int):
    """Get specific treatment information"""
    treatment = data_manager.get_treatment_info(treatment_id)
    if not treatment:
        raise HTTPException(status_code=404, detail="Treatment not found")
    return treatment
