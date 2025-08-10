from typing import List, Dict, Any, Tuple
from collections import defaultdict
import ast
from app.models.routine import RoutineItem, InteractionResult, ScoreResult
from app.models.treatment import TreatmentAnalysis
from app.core.db import data_manager

class SkincareAnalyzer:
    """Main business logic for skincare analysis"""
    
    def __init__(self):
        self.dm = data_manager

    def resolve_routine_ingredients(self, items: List[RoutineItem]) -> List[Tuple[int, str]]:
        """Resolve routine items from steps to (ingredient_id, source_label) pairs"""
        resolved = []
        
        for item in items:
            if item.product_id:
                ingredient_ids = self.dm.get_product_ingredient_ids(item.product_id)
                # Use product attributes directly
                label = f"{item.brand_name} - {item.product_name}"
                resolved.extend([(ing_id, label) for ing_id in ingredient_ids])
        
        return resolved
    
    """
    def resolve_routine_ingredients(self, items: List[RoutineItem]) -> List[Tuple[int, str]]:
        # Resolve routine items from steps to (ingredient_id, source_label) pairs 
        resolved = []
        
            # TODO - add this back when allows custom product
            # if item.item_type == "product" and item.product_id:
            #     ingredient_ids = self.dm.get_product_ingredient_ids(item.product_id)
            #     product_info = self.dm.get_product_by_id(item.product_id)
            #     if product_info:
            #         label = f"{product_info.brand_name} - {product_info.product_name}"
            #         resolved.extend([(ing_id, label) for ing_id in ingredient_ids])
            
            # elif item.item_type == "custom" and item.ingredient_names:
            #     label = item.label or f"Custom_{idx + 1}"
            #     for ing_name in item.ingredient_names:
            #         try:
            #             ing_id = int(ing_name)  # Try as ID first
            #         except ValueError:
            #             ing_id = self.dm.resolve_ingredient_name(ing_name)
                    
            #         if ing_id:
            #             resolved.append((ing_id, label))
        
        return resolved
        """

    def analyze_interactions(self, items: List[RoutineItem]) -> List[InteractionResult]:
        """Analyze ingredient interactions in a routine"""
        resolved = self.resolve_routine_ingredients(items)
        interactions = []
        
        for i, (ing_a, source_a) in enumerate(resolved):
            for ing_b, source_b in resolved[i+1:]:
                if ing_a != ing_b:  # Don't compare ingredient with itself
                    interaction_data = self.dm.get_interaction(ing_a, ing_b)
                    
                    if interaction_data:
                        interactions.append(InteractionResult(
                            ingredient_a=ing_a,
                            ingredient_b=ing_b,
                            ingredient_a_name=self.dm.ingredient_lookup.get(ing_a, "Unknown"),
                            ingredient_b_name=self.dm.ingredient_lookup.get(ing_b, "Unknown"),
                            product_a=source_a,
                            product_b=source_b,
                            **interaction_data
                        ))

        return interactions
        
        
    def calculate_routine_score(self, items: List[RoutineItem]) -> ScoreResult:
        """Calculate routine category scores"""
        resolved = self.resolve_routine_ingredients(items)
        all_ingredient_ids = list(set([ing_id for ing_id, _ in resolved]))
        
        category_scores = defaultdict(float)
        
        # Calculate scores from ingredients
        for ing_id in all_ingredient_ids:
            ingredient = self.dm.get_ingredient_by_id(ing_id)
            if ingredient and ingredient.category_scores:
                for category, score in ingredient.category_scores.items():
                    category_scores[category] += score
        
        # Apply clash penalties
        clash_penalties = self._calculate_clash_penalties(all_ingredient_ids)
        for category, penalty in clash_penalties.items():
            category_scores[category] += penalty
        
        return ScoreResult(
            category_scores=dict(category_scores),
            total_score=sum(category_scores.values())
        )
    
    def _calculate_clash_penalties(self, ingredient_ids: List[int]) -> Dict[str, float]:
        """Calculate penalties for ingredient clashes"""
        penalties = defaultdict(float)
        
        # Build category map for ingredients
        category_map = {}
        for ing_id in ingredient_ids:
            ingredient = self.dm.get_ingredient_by_id(ing_id)
            if ingredient and ingredient.category_scores:
                category_map[ing_id] = set(ingredient.category_scores.keys())
        
        # Check for clashes
        for i, ing_a in enumerate(ingredient_ids):
            for ing_b in ingredient_ids[i+1:]:
                interaction = self.dm.get_interaction(ing_a, ing_b)
                
                if interaction and interaction["interaction_type"].lower() == "clash":
                    shared_categories = category_map.get(ing_a, set()) & category_map.get(ing_b, set())
                    for category in shared_categories:
                        penalties[category] -= 1.0
        
        return dict(penalties)
    
    def analyze_post_treatment(self, treatment_id: int, items: List[RoutineItem]) -> TreatmentAnalysis:
        """Analyze routine safety after treatment"""
        treatment_rules = self.dm.get_treatment_rules(treatment_id)
        
        if not treatment_rules:
            raise ValueError("No rules found for this treatment")
        
        resolved = self.resolve_routine_ingredients(items)
        flagged = defaultdict(list)
        
        # Create rule lookup
        rule_lookup = {}
        for rule in treatment_rules:
            rule_lookup[rule["ingredient_id"]] = {
                "advice": rule["advice"],
                "duration_days": rule["duration_days"],
                "reason": rule["reason"]
            }
        
        # Check each ingredient
        for ing_id, source in resolved:
            if ing_id in rule_lookup:
                rule = rule_lookup[ing_id]
                flagged[source].append({
                    "ingredient": self.dm.ingredient_lookup.get(ing_id, "Unknown"),
                    "ingredient_id": ing_id,
                    "action": rule["advice"],
                    "duration_days": rule["duration_days"],
                    "reason": rule["reason"]
                })
        
        treatment_info = self.dm.get_treatment_info(treatment_id)
        if treatment_info:
            treatment_name = treatment_info["treatment_name"]  # e.g., "chemical_peel"
            treatment_display_name = treatment_info.get("display_name", treatment_name.replace("_", " ").title())

        return TreatmentAnalysis(
            treatment_name=treatment_name,
            display_name=treatment_display_name,
            flagged_products=dict(flagged)
        )

# Global analyzer instance
analyzer = SkincareAnalyzer()