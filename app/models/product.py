from typing import List, Optional
from pydantic import BaseModel

class ProductInfo(BaseModel):
    product_id: int
    brand_name: str
    product_name: str
    target_area: str
    ingredient_ids: List[int]
    inci_ingredients: List[str]
    product_type: str
    product_texture: Optional[str]
    target_area: str
