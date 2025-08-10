from fastapi import APIRouter, HTTPException
from app.core.db import data_manager


router = APIRouter(prefix="/treatments", tags=["treatments"])

# Treatments endpoints
@router.get("")
async def get_treatments():
    """Get all available treatments"""
    if data_manager.treatments.empty:
        return []
    return data_manager.treatments.to_dict(orient="records")

@router.get("/{treatment_id}")
async def get_treatment(treatment_id: int):
    """Get specific treatment information"""
    treatment = data_manager.get_treatment_info(treatment_id)
    if not treatment:
        raise HTTPException(status_code=404, detail="Treatment not found")
    return treatment
