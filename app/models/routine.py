from typing import Dict, Optional, List
from pydantic import BaseModel, Field, computed_field

from app.models.product import ProductInfo

class RoutineItem(ProductInfo):
    """Extended product info with routine-specific metadata"""
    step_order: int
    texture_order: int
    step_name: str
    routine_step_order: Optional[int] = 999
    amount: Optional[str] = None  # e.g., "2 pumps", "pea-sized"
    notes: Optional[str] = None
    wait_time_after: Optional[int] = None  # minutes to wait after applying


class Routine(BaseModel):
    name: str
    items: List[RoutineItem]
    time_of_day: Optional[str] = None


class CreateRoutineRequest(BaseModel):
    """Request model for creating a new routine"""
    name: str = Field(..., min_length=1, max_length=100, description="Name of the routine")
    description: Optional[str] = Field(None, max_length=500, description="Optional description")
    product_ids: List[int] = Field(..., min_items=1, description="List of product IDs")
    time_of_day: Optional[str] = Field(None, description="When to use this routine")
    user_id: Optional[str] = Field(None, description="User ID (for future user management)")


class UpdateRoutineRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    product_ids: Optional[List[int]] = Field(None, min_items=1)
    time_of_day: Optional[str] = Field(None)


class RoutineResponse(BaseModel):
    """Complete routine response with ordered steps"""
    routine_id: str
    name: str
    description: Optional[str]
    product_ids: List[int]
    time_of_day: Optional[str]
    items: List[RoutineItem]
    created_at: str
    updated_at: str
    user_id: Optional[str] = None
    
    class Config:
        from_attributes = True

    @computed_field
    @property
    def total_products(self) -> int:
        return len(self.items)


class PreviewRoutineRequest(BaseModel):
    """Request model for previewing routine order without saving"""
    product_ids: List[int] = Field(..., min_items=1)
    time_of_day: str = Field(None)


class PreviewRoutineResponse(BaseModel):
    """Response model for routine preview"""
    items: List[RoutineItem]
    total_products: int


class ScoreResult(BaseModel):
    category_scores: Dict[str, float]
    total_score: float


class InteractionResult(BaseModel):
    ingredient_a: int
    ingredient_b: int
    ingredient_a_name: str
    ingredient_b_name: str
    product_a: str
    product_b: str
    interaction_type: str
    effect: str
    details: str
