import pandas as pd
from typing import List, Dict
from app.core.db import data_manager

from app.models.routine import RoutineItem


class RoutineService:
    """Service layer for routine-related business logic"""
    
    def __init__(self):
        self.product_type_orders, self.step_display_names = self._load_product_type_data()
        self.product_texture_orders = self._load_product_texture_orders()

    def _load_product_type_data(self):
        """Load both product type orders and display names from the same CSV"""
        try:
            df = pd.read_csv("data/product_type_order.csv")
            
            # Create mapping from name to order
            product_type_orders = {}
            for _, row in df.iterrows():
                product_type_orders[row['name']] = int(row['order'])
            
            # Create mapping from order to display_name (using unique values)
            step_display_names = {}
            seen_orders = set()
            for _, row in df.iterrows():
                order = int(row['order'])
                if order not in seen_orders:
                    step_display_names[order] = row['display_name']
                    seen_orders.add(order)
            
            # Add default for unknown products
            step_display_names[999] = "Additional Care"
            print(f"Loaded {len(product_type_orders)} product types and {len(step_display_names)} step names")
            
            return product_type_orders, step_display_names
        
        except Exception as e:
            print(f"Error loading product type data: {e}")
            # Fallback based on your CSV structure
            product_type_orders = {
                "cleanser": 1,
                "exfoliator": 2,
                "toner": 3,
                "essence": 4,
                "serum": 5,
                "ampule": 5,
                "spot_treatment": 5,
                "concentrate": 5,
                "sheet_mask": 6,
                "eye_cream": 7,
                "eye_serum": 7,
                "moisturizer": 8,
                "gel_cream": 8,
                "sleeping_mask": 8,
                "face_oil": 9,
                "sun_protection": 10
            }
            
            step_display_names = {
                1: "Cleanser",
                2: "Exfoliator",
                3: "Toner and Essence",
                4: "Toner and Essence",
                5: "Treatment",
                6: "Sheet Mask",
                7: "Eye Care",
                8: "Moisturizer",
                9: "Face Oil",
                10: "Sun Protection",
                999: "Additional Care"
            }
            return product_type_orders, step_display_names
    
    def _load_product_texture_orders(self) -> Dict[str, int]:
        """Load product texture orders from CSV file"""
        try:
            texture_order_df = pd.read_csv("data/product_texture_order.csv")
            
            texture_to_order = {}
            for _, row in texture_order_df.iterrows():
                texture_to_order[row['name']] = row['order']
            
            return texture_to_order
        except Exception as e:
            print(f"Error loading product texture orders (file may not exist yet): {e}")
            # Fallback to default mapping
            return {
                'water': 1,
                'mist': 1,
                'essence': 2,
                'gel': 3,
                'lotion': 4,
                'serum': 4,
                'cream': 5,
                'balm': 6,
                'oil': 7,
                'thick_cream': 6,
                'paste': 7
            }
    
    def get_step_order(self, product_type: str) -> int:
        """Get step order from product type using your real data"""
        if not product_type or str(product_type).lower() == 'nan':
            return 999  # Unknown products go to end
        
        product_type_clean = str(product_type).lower().strip()
        return self.product_type_orders.get(product_type_clean, 999)
    
    def get_texture_order(self, product_texture: str) -> int:
        """Get texture order for sub-sorting within steps"""
        if not product_texture or str(product_texture).lower() == 'nan':
            return 5  # Default middle
        
        texture_clean = str(product_texture).lower().strip()
        return self.product_texture_orders.get(texture_clean, 5)
    
    def get_step_name(self, step_order: int) -> str:
        """Get display name for step based on your data"""
        return self.step_display_names.get(step_order, "Additional Care")
    

    def order_routine_products(self, product_ids: List[int], time_of_day: str = 'both') -> List[RoutineItem]:
        """Order routine products by skincare steps with sequential numbering"""
        if not product_ids:
            return []
        
        ordered_products = []
        
        # Create RoutineItems with original step orders
        for product_id in product_ids:
            product = data_manager.get_product_by_id(product_id)
            
            if not product:
                print(f"Warning: Product ID {product_id} not found")
                continue
            
            # Calculate routine-specific metadata
            step_order = self.get_step_order(product.product_type)
            texture_order = self.get_texture_order(product.product_texture)
            step_name = self.get_step_name(step_order)
            
            # Create RoutineItem
            routine_item = RoutineItem(
                **product.dict(),
                step_order=step_order,  # Original order (1, 2, 3, 5, 10, etc.)
                texture_order=texture_order,
                step_name=step_name
            )
            ordered_products.append(routine_item)
        
        # Sort by original step order, then texture order, then product_id
        ordered_products.sort(key=lambda p: (p.step_order, p.texture_order, p.product_id))
        
        # Assign sequential routine_step_order
        current_step = 1
        last_step_order = None
        
        for product in ordered_products:
            # If we've moved to a new step type, increment the counter
            if last_step_order is not None and product.step_order != last_step_order:
                current_step += 1
            
            product.routine_step_order = current_step  # Sequential: 1, 2, 3, 4
            last_step_order = product.step_order
        
        return ordered_products

        
    def validate_product_ids(self, product_ids: List[int]) -> List[int]:
        """Validate that product IDs exist in the database"""
        existing_product_ids = set(data_manager.products['product_id'].tolist())
        invalid_ids = [pid for pid in product_ids if pid not in existing_product_ids]
        return invalid_ids
