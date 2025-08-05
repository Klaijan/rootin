import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import ast
from app.models import IngredientInfo, ProductInfo

class DataManager:
    """Handles all data loading and basic queries from CSV files"""
    
    def __init__(self, data_path: str = "data"):
        self.data_path = Path(data_path)
        self.load_data()
    
    def load_data(self):
        """Load all CSV data with error handling"""
        try:
            # Load CSV files
            self.ingredients = pd.read_csv(self.data_path / "ingredients.csv")
            self.products = pd.read_csv(self.data_path / "products.csv") 
            self.product_ingredients = pd.read_csv(self.data_path / "product_ingredients.csv")
            self.interactions = pd.read_csv(self.data_path / "interactions.csv")
            self.treatments = pd.read_csv(self.data_path / "treatments.csv")
            self.treatment_rules = pd.read_csv(self.data_path / "treatment_rules.csv")
            self.scoring_labels = pd.read_csv(self.data_path / "scoring_labels.csv")
            self.common_names = pd.read_csv(self.data_path / "common_names.csv")
            
            # Create lookup dictionaries for performance
            self._build_lookups()
            
        except Exception as e:
            print(f"Error loading data: {e}")
            self._create_empty_dataframes()
    
    def _create_empty_dataframes(self):
        """Create empty dataframes as fallback"""
        self.ingredients = pd.DataFrame()
        self.products = pd.DataFrame()
        self.product_ingredients = pd.DataFrame()
        self.interactions = pd.DataFrame()
        self.treatments = pd.DataFrame()
        self.treatment_rules = pd.DataFrame()
        self.scoring_labels = pd.DataFrame()
        self.common_names = pd.DataFrame()
        self._build_lookups()
    
    def _build_lookups(self):
        """Build lookup dictionaries for fast access"""
        # Ingredient lookups
        if not self.ingredients.empty:
            self.ingredient_lookup = dict(zip(self.ingredients["id"], self.ingredients["inci_name"]))
            self.name_to_id = {name.lower(): _id for _id, name in zip(self.ingredients["id"], self.ingredients["inci_name"])}
        else:
            self.ingredient_lookup = {}
            self.name_to_id = {}
        
        # Interaction lookups
        if not self.interactions.empty:
            self.interaction_lookup = {}
            for _, row in self.interactions.iterrows():
                key = tuple(sorted([row["a_id"], row["b_id"]]))
                self.interaction_lookup[key] = {
                    "interaction_type": row["interaction_type"],
                    "effect": row["effect"],
                    "details": row["details"]
                }
        else:
            self.interaction_lookup = {}
        
        # Common names lookup
        if not self.common_names.empty:
            self.common_names_lookup = {}
            for _, row in self.common_names.iterrows():
                self.common_names_lookup[row["name"].lower()] = row["inci_id"]
        else:
            self.common_names_lookup = {}
    
    def get_ingredient_by_id(self, ingredient_id: int) -> Optional[IngredientInfo]:
        """Get ingredient by ID"""
        if self.ingredients.empty:
            return None
        
        ingredient = self.ingredients[self.ingredients["id"] == ingredient_id]
        if ingredient.empty:
            return None
        
        row = ingredient.iloc[0]
        
        # Parse category scores
        category_scores = {}
        try:
            if pd.notna(row.get("category_score")) and isinstance(row["category_score"], str):
                category_scores = ast.literal_eval(row["category_score"])
        except:
            pass
        
        return IngredientInfo(
            id=row["id"],
            name=row["inci_name"],
            function=row.get("function", ""),
            ph=row.get("ph"),
            comedogenic_rating=row.get("comedogenic_rating", 0),
            fungal_acne_safe=row.get("fungal_acne_safe", True),
            irritancy_rating=row.get("irritancy_rating", 0),
            description=row.get("description", ""),
            category_scores=category_scores
        )
    
    def get_product_by_id(self, product_id: int) -> Optional[ProductInfo]:
        """Get product by ID"""
        if self.products.empty:
            return None
        
        product = self.products[self.products["product_id"] == product_id]
        if product.empty:
            return None
        
        row = product.iloc[0]
        
        # Get ingredient IDs for this product
        ingredient_ids = self.get_product_ingredient_ids(product_id)
        
        # Parse INCI ingredients list
        inci_ingredients = []
        try:
            if pd.notna(row.get("inci_ingredients")) and isinstance(row["inci_ingredients"], str):
                inci_ingredients = ast.literal_eval(row["inci_ingredients"])
        except:
            pass
        
        return ProductInfo(
            product_id=row["product_id"],
            brand_name=row["brand_name"],
            product_name=row["product_name"],
            target_area=row.get("target_area", "face"),
            ingredient_ids=ingredient_ids,
            inci_ingredients=inci_ingredients
        )
    
    def get_product_ingredient_ids(self, product_id: int) -> List[int]:
        """Get ingredient IDs for a product (only positive IDs)"""
        if self.product_ingredients.empty:
            return []
        
        product_ings = self.product_ingredients[
            self.product_ingredients["product_id"] == product_id
        ]
        # Filter out negative IDs (these seem to be placeholders in your data)
        return [int(ing) for ing in product_ings["ingredient_id"].tolist() if ing > 0]
    
    def get_all_products(self) -> List[ProductInfo]:
        """Get all products"""
        if self.products.empty:
            return []
        
        products = []
        for _, row in self.products.iterrows():
            product = self.get_product_by_id(row["product_id"])
            if product:
                products.append(product)
        return products
    
    def get_all_ingredients(self) -> List[IngredientInfo]:
        """Get all ingredients"""
        if self.ingredients.empty:
            return []
        
        ingredients = []
        for _, row in self.ingredients.iterrows():
            ingredient = self.get_ingredient_by_id(row["id"])
            if ingredient:
                ingredients.append(ingredient)
        return ingredients
    
    def resolve_ingredient_name(self, name: str) -> Optional[int]:
        """Resolve ingredient name to ID with exact and common name matching"""
        # Try exact match first
        exact_match = self.name_to_id.get(name.lower())
        if exact_match:
            return exact_match
        
        # Try common names
        common_match = self.common_names_lookup.get(name.lower())
        if common_match:
            return common_match
        
        return None
    
    def get_interaction(self, ing_a: int, ing_b: int) -> Optional[Dict]:
        """Get interaction between two ingredients"""
        key = tuple(sorted([ing_a, ing_b]))
        return self.interaction_lookup.get(key)
    
    def get_treatment_rules(self, treatment_id: int) -> List[Dict]:
        """Get treatment rules for a specific treatment"""
        if self.treatment_rules.empty:
            return []
        
        rules = self.treatment_rules[self.treatment_rules["treatment_id"] == treatment_id]
        return rules.to_dict(orient="records")
    
    def get_treatment_info(self, treatment_id: int) -> Optional[Dict]:
        """Get treatment information"""
        if self.treatments.empty:
            return None
        
        treatment = self.treatments[self.treatments["treatment_id"] == treatment_id]
        if treatment.empty:
            return None
        
        return treatment.iloc[0].to_dict()

# Global data manager instance
data_manager = DataManager()
