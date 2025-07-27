import os
import requests

BASE_URL = os.getenv("BASEROW_API_URL")
TABLE_ID = os.getenv("TABLE_ID_INTERACTIONS")
TOKEN = os.getenv("BASEROW_API_TOKEN")

HEADERS = {
    "Authorization": f"Token {TOKEN}"
}

# def list_interactions():
#     url = f"{BASE_URL}/database/rows/table/{TABLE_ID}/?user_field_names=true"
#     res = requests.get(url, headers=HEADERS)
#     res.raise_for_status()
#     return res.json()["results"]

def add_interaction(name_a, name_b, interaction_type, details=""):
    url = f"{BASE_URL}/database/rows/table/{TABLE_ID}/?user_field_names=true"
    payload = {
        "Ingredient A": name_a,
        "Ingredient B": name_b,
        "Type": interaction_type,
        "Details": details
    }
    res = requests.post(url, headers=HEADERS, json=payload)
    res.raise_for_status()
    return res.json()


def get_interactions(product_a, product_b):
    pass