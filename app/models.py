from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import date

class IngredientInfo(BaseModel):
    id: int
    name: str
    function: str
    ph: Optional[str] = None
    comedogenic_rating: int
    fungal_acne_safe: bool
    irritancy_rating: int
    description: str
    category_scores: Dict[str, float] = {}

class ProductInfo(BaseModel):
    product_id: int
    brand_name: str
    product_name: str
    target_area: str
    ingredient_ids: List[int]
    inci_ingredients: List[str] = []

class RoutineItem(BaseModel):
    item_type: str  # "product" or "custom"
    product_id: Optional[int] = None
    ingredient_names: Optional[List[str]] = None
    label: Optional[str] = None

class Routine(BaseModel):
    name: str
    items: List[RoutineItem]
    time_of_day: str = "morning"

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

class ScoreResult(BaseModel):
    category_scores: Dict[str, float]
    total_score: float

class TreatmentAnalysis(BaseModel):
    treatment_name: str
    flagged_products: Dict[str, List[Dict[str, Any]]]

class TreatmentLog(BaseModel):
    treatment_id: int
    date: date
    notes: Optional[str] = None
