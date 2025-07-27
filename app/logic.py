# Business logic (e.g., add_interaction, check_product_clash)

from itertools import combinations
from typing import List, Union
from app.db import (
    get_product_ingredients_id, 
    get_interaction, 
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