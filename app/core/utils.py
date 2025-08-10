from typing import Tuple

def get_ordered_pair(id1: int, id2: int) -> Tuple[int, int]:
    """Get ordered pair for consistent interaction lookup"""
    return (id1, id2) if id1 < id2 else (id2, id1)

def truncate_text(text: str, max_length: int = 50) -> str:
    """Truncate text with ellipsis"""
    return text if len(text) <= max_length else text[:max_length-3] + "..."

def format_ingredient_list(ingredients: list, max_display: int = 4) -> str:
    """Format ingredient list for display"""
    if len(ingredients) <= max_display:
        return ", ".join(ingredients)
    else:
        return ", ".join(ingredients[:max_display]) + f"... (+{len(ingredients) - max_display} more)"
