from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import date

class TreatmentAnalysis(BaseModel):
    treatment_name: str
    display_name: str
    flagged_products: Dict[str, List[Dict[str, Any]]]

class TreatmentLog(BaseModel):
    treatment_id: int
    date: date
    notes: Optional[str] = None
