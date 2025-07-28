# Business logic (e.g., add_interaction, check_product_clash)

from collections import defaultdict
from itertools import combinations
from typing import List, Union
from app.db import (
    get_ingredient_name,
    get_product_ingredients_id, 
    get_interaction,
    get_treatment,
    get_treatment_rule,
    resolve_ingredient_name
)


def resolve_ingredients(item, index=None) -> List[tuple[str, str]]:
    if isinstance(item, int):  # product_id
        ingredients = get_product_ingredients_id(item)
        return [(ing, item) for ing in ingredients]  # label = product ID
    elif isinstance(item, list):  # raw ingredient list
        label = f"User_Product_{index + 1}" if index is not None else "custom"
        resolved_ids = []
        for ing in item:
            try:
                ing_id = int(ing)  # try ID directly
            except ValueError:
                ing_id = resolve_ingredient_name(ing)  # try name
            if ing_id is not None:
                resolved_ids.append((ing_id, label))
        return resolved_ids
    else:
        return []

# TODO   
"""
def map_product_name_id(input: str) -> str:
    pass
"""


def map_inci_ingredient_id(input: List[str]) -> List[int]:
    pass


def compare_ingredient_lists(
    items: List[Union[int, List[str]]],
    self_compare: bool = True
) -> List[dict]:
    # Now takes in product_id or list of string ingredients

    all_interactions = []
    resolved = [resolve_ingredients(item, idx) for idx, item in enumerate(items)]

    # Flatten the list: [(ingredient_id, source)]
    flat = []
    for ingredient_list in resolved:
        flat.extend(ingredient_list)

    for (ing_a, product_a), (ing_b, product_b) in combinations(flat, 2):
        if ing_a == ing_b or (not self_compare and product_a == product_b):
            continue
        interaction = get_interaction(ing_a, ing_b)
        if interaction:
            interaction["product_a"] = product_a
            interaction["product_b"] = product_b
            all_interactions.append(interaction)

    return all_interactions


def after_treatment(
    treatment_ids: List[int],
    product_list: List[Union[int, List[str]]]
):
    if isinstance(treatment_ids, int):
        treatment_ids = [treatment_ids]

    all_rules = []
    treatment_names = []

    # Load all rules for all treatment IDs
    for treatment_id in treatment_ids:
        rules = get_treatment_rule(treatment_id)
        all_rules.extend(rules)

        treatment = get_treatment(treatment_id)
        if treatment:
            treatment_names.append(treatment["treatment_name"])

    if not all_rules:
        return {"error": "No treatment rules found."}

    # Ingredient rule lookup
    rule_lookup = {
        int(rule["ingredient_id"]): rule for rule in all_rules
    }

    flagged = defaultdict(list)
    product_avoid_days = {}

    for idx, product in enumerate(product_list):
        label = product if isinstance(product, int) else f"User_Product_{idx + 1}"
        ingredient_ids = []

        if isinstance(product, int):
            ingredient_ids = get_product_ingredients_id(product)
        elif isinstance(product, list):
            for ing in product:
                try:
                    ing_id = int(ing)
                except ValueError:
                    ing_id = resolve_ingredient_name(ing)
                if ing_id is not None:
                    ingredient_ids.append(ing_id)

        ingredient_ids = list(set(map(int, ingredient_ids)))
        max_duration = 0

        for ing_id in ingredient_ids:
            if ing_id in rule_lookup:
                rule = rule_lookup[ing_id]
                flagged[label].append({
                    "ingredient": get_ingredient_name(ing_id),
                    "action": rule["advice"],  # 'avoid' or 'be careful'
                    "duration_days": rule["duration_days"],
                    "reason": rule["reason"]
                })
                if rule["advice"].lower() == "avoid":
                    max_duration = max(max_duration, int(rule["duration_days"]))

        if max_duration > 0:
            product_avoid_days[label] = max_duration

    return {
        "treatment_name": ", ".join(treatment_names),
        "flagged": dict(flagged),
        "product_avoid_days": product_avoid_days
    }