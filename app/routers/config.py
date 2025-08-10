# app/routers/config.py - Configuration endpoints

from fastapi import APIRouter, HTTPException
import pandas as pd
import logging
from typing import Dict

router = APIRouter(prefix="/config", tags=["configuration"])
logger = logging.getLogger(__name__)

@router.get("/step-names", response_model=Dict[int, str])
async def get_step_names():
    """Get step display names mapping"""
    try:
        df = pd.read_csv("data/product_type_order.csv")
        
        # Create a dictionary of unique order -> display_name
        step_names = {}
        seen_orders = set()
        
        for _, row in df.iterrows():
            order = int(row['order'])
            if order not in seen_orders:
                step_names[order] = row['display_name']
                seen_orders.add(order)
        
        # Add default for unknown
        step_names[999] = "Additional Care"
        
        return step_names
        
    except FileNotFoundError:
        logger.error("product_type_order.csv not found")
        raise HTTPException(status_code=404, detail="Configuration file not found")
    except Exception as e:
        logger.error(f"Error loading step names: {e}")
        raise HTTPException(status_code=500, detail="Failed to load configuration")

@router.get("/product-types")
async def get_product_types():
    """Get all product type mappings"""
    try:
        df = pd.read_csv("data/product_type_order.csv")
        
        product_types = []
        for _, row in df.iterrows():
            product_types.append({
                "id": int(row['id']),
                "order": int(row['order']),
                "name": row['name'],
                "type": row['type'],
                "display_name": row['display_name']
            })
        
        return product_types
        
    except FileNotFoundError:
        logger.error("product_type_order.csv not found")
        raise HTTPException(status_code=404, detail="Configuration file not found")
    except Exception as e:
        logger.error(f"Error loading product types: {e}")
        raise HTTPException(status_code=500, detail="Failed to load configuration")

@router.get("/texture-orders")
async def get_texture_orders():
    """Get product texture ordering configuration"""
    try:
        df = pd.read_csv("data/product_texture_order.csv")
        
        texture_orders = {}
        for _, row in df.iterrows():
            texture_orders[row['name']] = int(row['order'])
        
        return texture_orders
        
    except FileNotFoundError:
        # Return defaults if file doesn't exist
        return {
            'water': 1,
            'mist': 1,
            'essence': 2,
            'gel': 3,
            'lotion': 4,
            'serum': 4,
            'cream': 5,
            'balm': 6,
            'oil': 7
        }
    except Exception as e:
        logger.error(f"Error loading texture orders: {e}")
        raise HTTPException(status_code=500, detail="Failed to load configuration")

@router.get("/categories")
async def get_scoring_categories():
    """Get scoring category labels"""
    try:
        df = pd.read_csv("data/scoring_labels.csv")
        
        categories = []
        for _, row in df.iterrows():
            categories.append({
                "id": int(row['id']),
                "name": row['Name']
            })
        
        return categories
        
    except FileNotFoundError:
        logger.error("scoring_labels.csv not found")
        raise HTTPException(status_code=404, detail="Scoring labels file not found")
    except Exception as e:
        logger.error(f"Error loading categories: {e}")
        raise HTTPException(status_code=500, detail="Failed to load categories")