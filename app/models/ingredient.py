
from typing import Dict, Optional
from pydantic import BaseModel


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
