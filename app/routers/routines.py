from fastapi import APIRouter, HTTPException
import logging
from typing import List

from app.models.routine import (
    CreateRoutineRequest,
    InteractionResult,
    RoutineItem,
    RoutineResponse,
    ScoreResult,
    UpdateRoutineRequest, 
)
from app.core.db import data_manager
from app.services.skincare_analyzer import analyzer
from app.models.treatment import TreatmentAnalysis
from app.services.routine_service import RoutineService
from app.services.storage_service import routine_storage


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/routines", tags=["routines"])
routine_service = RoutineService()


@router.post("", response_model=RoutineResponse)
async def create_routine(request: CreateRoutineRequest):
    """Create a new skincare routine with ordered steps"""
    try:
        # Log the incoming request for debugging
        logger.info(f"Creating routine with name: {request.name}")
        logger.info(f"Product IDs: {request.product_ids}")
        logger.info(f"Time of day: {request.time_of_day}")
        
        # Validate product IDs exist
        invalid_ids = routine_service.validate_product_ids(request.product_ids)
        if invalid_ids:
            logger.error(f"Invalid product IDs found: {invalid_ids}")
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid product IDs: {invalid_ids}"
            )
        
        # Order the products into steps
        time_of_day = request.time_of_day or "both"  # Default to "both" if not specified
        ordered_steps = routine_service.order_routine_products(
            request.product_ids, 
            time_of_day
        )
        
        # Create routine data with ordered steps
        routine_data = {
            "name": request.name,
            "description": request.description or "",  # Handle None description
            "product_ids": request.product_ids,
            "time_of_day": time_of_day,
            "items": [step.dict() for step in ordered_steps],
            "user_id": request.user_id
        }
        
        # Store the routine
        routine_id = routine_storage.create_routine(routine_data)
        logger.info(f"Routine created with ID: {routine_id}")
        
        # Get and return the stored routine
        stored_routine = routine_storage.get_routine(routine_id)
        return RoutineResponse(**stored_routine)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating routine: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("")
async def list_routines():
    """List all routines"""
    try:
        routines = routine_storage.list_routines()
        return {
            "routines": routines,
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing routines: {str(e)}")


@router.get("/{routine_id}", response_model=RoutineResponse)
async def get_routine(routine_id: str):
    """Get a routine by ID"""
    stored_routine = routine_storage.get_routine(routine_id)
    if not stored_routine:
        raise HTTPException(status_code=404, detail="Routine not found")

    return RoutineResponse(**stored_routine)


@router.put("/{routine_id}", response_model=RoutineResponse)
async def update_routine(routine_id: str, request: UpdateRoutineRequest):
    """Update a routine and re-order if products changed"""
    try:
        # Check if routine exists
        existing_routine = routine_storage.get_routine(routine_id)
        if not existing_routine:
            raise HTTPException(status_code=404, detail="Routine not found")
        
        # Prepare update data
        update_data = {}
        
        # If product_ids changed, re-order the steps
        if request.product_ids is not None:
            invalid_ids = routine_service.validate_product_ids(request.product_ids)
            if invalid_ids:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid product IDs: {invalid_ids}"
                )
            
            # Re-order with new products
            time_of_day = request.time_of_day or existing_routine.get('time_of_day', 'both')
            ordered_steps = routine_service.order_routine_products(
                request.product_ids,
                time_of_day
            )
            
            update_data['product_ids'] = request.product_ids
            update_data['items'] = [step.dict() for step in ordered_steps]
        
        # Update other fields if provided
        if request.name is not None:
            update_data['name'] = request.name
        if request.description is not None:
            update_data['description'] = request.description
        if request.time_of_day is not None:
            update_data['time_of_day'] = request.time_of_day
            
            # If only time_of_day changed but not products, might need to re-order
            # (depending on if your ordering logic uses time_of_day)
            if 'product_ids' not in update_data:
                ordered_steps = routine_service.order_routine_products(
                    existing_routine['product_ids'],
                    request.time_of_day
                )
                update_data['items'] = [step.dict() for step in ordered_steps]
        
        # Update the routine
        success = routine_storage.update_routine(routine_id, update_data)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update routine")
        
        # Return updated routine
        updated_routine = routine_storage.get_routine(routine_id)
        return RoutineResponse(**updated_routine)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating routine {routine_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{routine_id}")
async def delete_routine(routine_id: str):
    """Delete a routine"""
    try:
        success = routine_storage.delete_routine(routine_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Routine not found")
        
        return {"message": "Routine deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting routine: {str(e)}")


@router.post("/preview")
async def preview_routine_order(request: CreateRoutineRequest):
    """Preview routine order without storing it"""
    try:
        # Validate product IDs
        existing_product_ids = set(data_manager.products["product_id"].tolist())
        invalid_ids = [pid for pid in request.product_ids if pid not in existing_product_ids]
        
        if invalid_ids:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid product IDs: {invalid_ids}"
            )
        
        # Order the products
        ordered_routine = routine_service.order_routine_products(
            request.product_ids, 
            request.time_of_day
        )
        
        return ordered_routine
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error previewing routine: {str(e)}")

@router.get("/{routine_id}/analyze/interactions", response_model=List[InteractionResult])
async def analyze_interactions(routine_id: str):
    """Analyze ingredient interactions in a routine"""
    try:
        stored_routine = routine_storage.get_routine(routine_id)
        if not stored_routine:
            raise HTTPException(status_code=404, detail="Routine not found")
        
        # Convert stored items to RoutineItem objects for analyzer
        routine_steps = [RoutineItem(**item) for item in stored_routine.get('items', [])]
        
        return analyzer.analyze_interactions(routine_steps)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing interactions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{routine_id}/analyze/score", response_model=ScoreResult)
async def analyze_score(routine_id: str):
    """Calculate routine category scores"""
    try:
        stored_routine = routine_storage.get_routine(routine_id)
        if not stored_routine:
            raise HTTPException(status_code=404, detail="Routine not found")
        
        # Convert stored items to RoutineItem objects for analyzer
        routine_steps = [RoutineItem(**item) for item in stored_routine.get('items', [])]
        
        return analyzer.calculate_routine_score(routine_steps)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating scores: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{routine_id}/analyze/post-treatment/{treatment_id}", response_model=TreatmentAnalysis)
async def analyze_post_treatment(routine_id: str, treatment_id: int):
    """Analyze routine safety after treatment"""
    try:
        stored_routine = routine_storage.get_routine(routine_id)
        if not stored_routine:
            raise HTTPException(status_code=404, detail="Routine not found")
        
        # Convert stored items to RoutineItem objects for analyzer
        routine_steps = [RoutineItem(**item) for item in stored_routine.get('items', [])]
        
        return analyzer.analyze_post_treatment(treatment_id, routine_steps)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing post-treatment: {e}")
        raise HTTPException(status_code=500, detail=str(e))