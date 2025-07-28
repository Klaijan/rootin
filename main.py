# Entrypoint for CLI or test run

from app.db import get_ingredient_name, interaction_type_order
from app.logic import after_treatment, compare_ingredient_lists
from app.scoring import routine_score

if __name__ == "__main__":

    # Now it's brand + product_name 
    # need to fix
    # products = [
    #     ("Kiehl's", "Micro-Dose Anti-Aging Retinol Serum with Ceramides and Peptide"),
    #     ("The Ordinary", "Niacinamide 10% + Zinc 1%"),
    #     ("La Roche-Posay", "Retinol"), # doesn't exist in the database
    #     ("Decorté", "Liposome Advanced Repair Serum"),
    #     ("Clinique", "All About Eyes™ Eye Cream with Vitamin C"),
    # ]

    products = [
        1, 
        2, 
        3,
        34, 
        67, 
        ["Ceramides", "Retinol", "Niacinamide"]
    ]

    treatments = [
        1, # microneedling
    ]

    interactions = compare_ingredient_lists(products)
    grouped_interactions = {}
    if not interactions:
        print("No interactions found.")
    else:
        for interaction in interactions:
            if interaction["interaction_type"] in grouped_interactions:
                grouped_interactions[interaction["interaction_type"]].append(interaction)
            else:
                grouped_interactions[interaction["interaction_type"]] = [interaction]

    ordered_types = sorted(
        grouped_interactions.items(),
        key=lambda kv: interaction_type_order.get(kv[0].lower(), 999)  # 999 = fallback
    )
    if grouped_interactions:
        print("⚠️ Interactions found:\n")
        for interaction_type, group in ordered_types:
            print(f"{interaction_type.title()} ({len(group)}):")
            for v in group:
                name_a = get_ingredient_name(v["ingredient_a"])
                name_b = get_ingredient_name(v["ingredient_b"])
                print(
                    f"- {name_a} (from {v['product_a']}) × {name_b} (from {v['product_b']})"
                )
                print(f"    Effect: {v['effect']}")
                print(f"    Details: {v['details']}\n")
            print()

    print("🧪 Routine Category Scores:")
    scores = routine_score(products)
    for cat, val in scores.items():
        print(f"{cat}: {val:.2f}")

    # Treatments
    for treatment in treatments:
        result = after_treatment(treatment, products)

        if "error" in result:
            print(f"❌ Error for treatment ID {treatment}: {result['error']}")
        else:
            treatment_name = result.get("treatment_name", f"Treatment {treatment}")
            print(f"\n🧴 Post-Treatment Check for: {treatment_name}\n")
            for product_source, flagged in result["flagged"].items():
                if not flagged:
                    continue
                print(f"⚠️ Product: {product_source}")
                for entry in flagged:
                    action = entry["action"].upper()
                    print(f"  - {entry['ingredient']} → {action}")
                    print(f"    Reason: {entry['reason']}\n")