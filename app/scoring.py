from collections import defaultdict
import ast
from typing import Union
from app.db import (
    get_product_ingredients_id,
    resolve_ingredient_name,
    get_interaction,
    ingredients,
)

def get_ingredient_scores(ingredient_ids: list[int]) -> dict:
    scores = defaultdict(float)

    ingredients["category_score"] = ingredients["category_score"].apply(
        lambda x: ast.literal_eval(x) if isinstance(x, str) else {}
    )
    category_map = dict(zip(ingredients["id"], ingredients["category_score"]))

    for ing_id in ingredient_ids:
        cat_score = category_map.get(ing_id, {})
        for category, value in cat_score.items():
            scores[category] += value
    return dict(scores)


def apply_clash_penalty(all_ingredients: list[int]) -> dict:
    penalty = defaultdict(float)
    ingredients["category_score"] = ingredients["category_score"].apply(
        lambda x: ast.literal_eval(x) if isinstance(x, str) else {}
    )
    category_map = dict(zip(ingredients["id"], ingredients["category_score"]))

    for i, ing1 in enumerate(all_ingredients):
        cat1 = set(category_map.get(ing1, {}).keys())
        for ing2 in all_ingredients[i+1:]:
            interaction = get_interaction(ing1, ing2)
            if interaction and interaction["interaction_type"].lower() == "clash":
                cat2 = set(category_map.get(ing2, {}).keys())
                shared_cats = cat1 & cat2
                for cat in shared_cats:
                    penalty[cat] -= 1
                # If no shared_cats, do nothing
    return penalty


def routine_score(routine_items: list[Union[int, list[str]]]) -> dict:
    all_ingredients = []

    for idx, item in enumerate(routine_items):
        if isinstance(item, int):  # product ID
            all_ingredients += get_product_ingredients_id(item)
        elif isinstance(item, list):  # ingredient names
            for ing in item:
                try:
                    ing_id = int(ing)
                except ValueError:
                    ing_id = resolve_ingredient_name(ing)
                if ing_id is not None:
                    all_ingredients.append(ing_id)

    # Deduplicate
    all_ingredients = list(set(map(int, all_ingredients)))

    # Category scores
    score = get_ingredient_scores(all_ingredients)

    # Clash penalty
    clash_penalties = apply_clash_penalty(all_ingredients)

    # Combine with category scores
    for cat, val in clash_penalties.items():
        score[cat] += val
        
    return score
