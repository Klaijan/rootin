### 
# This file needs to be fixed to use DB engine and session
###

from typing import Dict, List, Optional
import pandas as pd

# Load data once globally
PRODUCT_INGREDIENTS_PATH = "data/product_ingredients.csv"
PRODUCT_PATH = "data/products.csv"
INTERACTIONS_PATH = "data/interactions.csv"
INGREDIENTS_PATH = "data/ingredients.csv"

product_ingredients = pd.read_csv(PRODUCT_INGREDIENTS_PATH)
products = pd.read_csv(PRODUCT_PATH)
interactions = pd.read_csv(INTERACTIONS_PATH)
ingredients = pd.read_csv(INGREDIENTS_PATH)

type_order = pd.read_csv("data/interaction_types.csv") 
interaction_type_order = {
    name.lower(): idx for idx, name in enumerate(type_order["name"].tolist())
}

ingredient_lookup = dict(zip(ingredients["id"], ingredients["inci_name"]))

interaction_lookup = {
    tuple(sorted((row["a_id"], row["b_id"]))): (
        row["interaction_type"], row["effect"], row["details"]
    )
    for _, row in interactions.iterrows()
}

name_to_id = {
    name.lower(): _id for _id, name in zip(ingredients["id"], ingredients["inci_name"])
}

def get_product_ingredients(product_id: int) -> List[str]:
    return product_ingredients[product_ingredients["product_id"] == product_id]["inci_ingredients"].tolist()


def get_product_ingredients_id(product_id: int) -> List[str]:
    return product_ingredients[product_ingredients["product_id"] == product_id]["ingredient_id"].tolist()


def get_interaction(ing_a: int, ing_b: int) -> Optional[Dict]:
    key = tuple(sorted([ing_a, ing_b]))
    result = interaction_lookup.get(key)
    if result:
        interaction_type, effect, details = result
        return {
            "ingredient_a": key[0], 
            "ingredient_b": key[1], 
            "interaction_type": interaction_type,
            "effect":  effect,
            "details": details
        }
    return None


def get_ingredient_name(ingredient_id: int) -> str:
    return ingredient_lookup.get(ingredient_id, ingredient_id)


def resolve_ingredient_name(name: str) -> Optional[int]:
    # TODO - fuzzy match ingredient
    return name_to_id.get(name.lower())
