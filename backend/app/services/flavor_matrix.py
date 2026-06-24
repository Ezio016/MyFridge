"""
Flavor Matrix System (Database Version)

Each ingredient is represented as a vector in flavor space:
[sweet, salty, sour, bitter, umami, spicy, fatty, aromatic]

When you combine ingredients, you can predict the overall flavor profile
of the dish by summing the flavor vectors.

Flavor Profile = Σ (ingredient_i × flavor_vector_i)

This version supports both:
1. In-memory INGREDIENT_FLAVORS dict (fallback)
2. Database ingredient_flavors table (preferred)
"""

from typing import Optional, Dict, List
from sqlalchemy.orm import Session

# ============================================================
# FLAVOR DIMENSIONS (8 basic taste/flavor categories)
# ============================================================
FLAVOR_DIMENSIONS = [
    "sweet",      # Sugars, fruits, honey
    "salty",      # Salt, soy sauce, fish sauce
    "sour",       # Citrus, vinegar, fermented
    "bitter",     # Coffee, dark greens, some herbs
    "umami",      # Savory depth - meat, mushrooms, aged cheese
    "spicy",      # Heat - chili, pepper, ginger
    "fatty",      # Richness - oils, butter, cream
    "aromatic",   # Fragrant - herbs, spices, garlic
]

N_FLAVORS = len(FLAVOR_DIMENSIONS)

# ============================================================
# INGREDIENT FLAVOR PROFILES
# Values from 0.0 (none) to 1.0 (very strong)
# Format: [sweet, salty, sour, bitter, umami, spicy, fatty, aromatic]
# ============================================================
INGREDIENT_FLAVORS = {
    # === PROTEINS ===
    "chicken":      [0.0, 0.1, 0.0, 0.0, 0.6, 0.0, 0.3, 0.1],
    "beef":         [0.0, 0.1, 0.0, 0.0, 0.8, 0.0, 0.5, 0.2],
    "pork":         [0.1, 0.2, 0.0, 0.0, 0.7, 0.0, 0.6, 0.1],
    "lamb":         [0.0, 0.1, 0.0, 0.0, 0.7, 0.0, 0.5, 0.4],
    "fish":         [0.0, 0.2, 0.0, 0.0, 0.7, 0.0, 0.3, 0.3],
    "shrimp":       [0.1, 0.3, 0.0, 0.0, 0.8, 0.0, 0.2, 0.2],
    "eggs":         [0.0, 0.1, 0.0, 0.0, 0.5, 0.0, 0.4, 0.1],
    "tofu":         [0.0, 0.0, 0.0, 0.0, 0.3, 0.0, 0.1, 0.0],
    "bacon":        [0.1, 0.7, 0.0, 0.0, 0.8, 0.0, 0.8, 0.5],
    
    # === DAIRY ===
    "milk":         [0.2, 0.1, 0.0, 0.0, 0.2, 0.0, 0.3, 0.0],
    "butter":       [0.1, 0.2, 0.0, 0.0, 0.3, 0.0, 0.9, 0.2],
    "cheese":       [0.0, 0.5, 0.1, 0.0, 0.7, 0.0, 0.6, 0.3],
    "parmesan":     [0.0, 0.6, 0.0, 0.1, 0.9, 0.0, 0.4, 0.4],
    "cream":        [0.2, 0.1, 0.0, 0.0, 0.2, 0.0, 0.8, 0.1],
    "yogurt":       [0.1, 0.1, 0.4, 0.0, 0.2, 0.0, 0.3, 0.1],
    
    # === VEGETABLES ===
    "onion":        [0.3, 0.0, 0.0, 0.0, 0.2, 0.1, 0.0, 0.6],
    "garlic":       [0.0, 0.0, 0.0, 0.1, 0.3, 0.2, 0.0, 0.9],
    "tomato":       [0.3, 0.0, 0.4, 0.0, 0.5, 0.0, 0.0, 0.3],
    "potato":       [0.1, 0.0, 0.0, 0.0, 0.1, 0.0, 0.0, 0.0],
    "carrot":       [0.4, 0.0, 0.0, 0.0, 0.1, 0.0, 0.0, 0.2],
    "celery":       [0.0, 0.2, 0.0, 0.2, 0.1, 0.0, 0.0, 0.4],
    "pepper":       [0.3, 0.0, 0.0, 0.1, 0.1, 0.1, 0.0, 0.3],
    "mushroom":     [0.0, 0.0, 0.0, 0.0, 0.8, 0.0, 0.0, 0.5],
    "spinach":      [0.0, 0.0, 0.0, 0.3, 0.2, 0.0, 0.0, 0.2],
    "broccoli":     [0.0, 0.0, 0.0, 0.3, 0.2, 0.0, 0.0, 0.3],
    "cabbage":      [0.1, 0.0, 0.0, 0.2, 0.1, 0.1, 0.0, 0.2],
    "eggplant":     [0.0, 0.0, 0.0, 0.2, 0.2, 0.0, 0.0, 0.1],
    "zucchini":     [0.1, 0.0, 0.0, 0.0, 0.1, 0.0, 0.0, 0.1],
    "avocado":      [0.0, 0.0, 0.0, 0.0, 0.2, 0.0, 0.7, 0.1],
    
    # === AROMATICS & HERBS ===
    "ginger":       [0.0, 0.0, 0.0, 0.0, 0.1, 0.5, 0.0, 0.9],
    "basil":        [0.1, 0.0, 0.0, 0.0, 0.1, 0.1, 0.0, 0.8],
    "cilantro":     [0.0, 0.0, 0.1, 0.0, 0.1, 0.0, 0.0, 0.9],
    "parsley":      [0.0, 0.0, 0.0, 0.1, 0.1, 0.0, 0.0, 0.6],
    "thyme":        [0.0, 0.0, 0.0, 0.1, 0.1, 0.0, 0.0, 0.8],
    "rosemary":     [0.0, 0.0, 0.0, 0.2, 0.1, 0.0, 0.0, 0.9],
    "oregano":      [0.0, 0.0, 0.0, 0.2, 0.1, 0.1, 0.0, 0.8],
    "mint":         [0.1, 0.0, 0.0, 0.0, 0.0, 0.2, 0.0, 0.9],
    "dill":         [0.0, 0.0, 0.0, 0.1, 0.1, 0.0, 0.0, 0.7],
    "bay leaf":     [0.0, 0.0, 0.0, 0.2, 0.1, 0.0, 0.0, 0.6],
    
    # === GRAINS & CARBS ===
    "rice":         [0.1, 0.0, 0.0, 0.0, 0.1, 0.0, 0.0, 0.1],
    "pasta":        [0.1, 0.0, 0.0, 0.0, 0.1, 0.0, 0.0, 0.1],
    "bread":        [0.2, 0.1, 0.0, 0.0, 0.2, 0.0, 0.1, 0.3],
    "noodles":      [0.1, 0.0, 0.0, 0.0, 0.1, 0.0, 0.0, 0.0],
    "flour":        [0.1, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    
    # === SEASONINGS & SAUCES ===
    "salt":         [0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    "sugar":        [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    "honey":        [0.9, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.3],
    "soy sauce":    [0.1, 0.8, 0.0, 0.0, 0.9, 0.0, 0.0, 0.3],
    "fish sauce":   [0.0, 0.7, 0.0, 0.0, 0.9, 0.0, 0.0, 0.5],
    "vinegar":      [0.0, 0.0, 0.9, 0.0, 0.0, 0.0, 0.0, 0.2],
    "lemon":        [0.1, 0.0, 0.9, 0.1, 0.0, 0.0, 0.0, 0.5],
    "lime":         [0.0, 0.0, 0.9, 0.1, 0.0, 0.0, 0.0, 0.6],
    "mustard":      [0.0, 0.2, 0.2, 0.1, 0.1, 0.4, 0.0, 0.5],
    "ketchup":      [0.5, 0.3, 0.3, 0.0, 0.3, 0.0, 0.0, 0.2],
    "mayo":         [0.1, 0.2, 0.2, 0.0, 0.2, 0.0, 0.8, 0.1],
    "miso":         [0.1, 0.6, 0.0, 0.0, 0.9, 0.0, 0.1, 0.4],
    
    # === SPICES ===
    "black pepper": [0.0, 0.0, 0.0, 0.1, 0.0, 0.6, 0.0, 0.7],
    "cumin":        [0.0, 0.0, 0.0, 0.1, 0.2, 0.2, 0.0, 0.8],
    "paprika":      [0.2, 0.0, 0.0, 0.1, 0.1, 0.3, 0.0, 0.7],
    "cayenne":      [0.0, 0.0, 0.0, 0.0, 0.0, 0.9, 0.0, 0.4],
    "chili":        [0.0, 0.0, 0.0, 0.0, 0.1, 0.9, 0.0, 0.5],
    "cinnamon":     [0.4, 0.0, 0.0, 0.1, 0.0, 0.2, 0.0, 0.9],
    "nutmeg":       [0.2, 0.0, 0.0, 0.1, 0.0, 0.1, 0.0, 0.8],
    "turmeric":     [0.0, 0.0, 0.0, 0.3, 0.1, 0.1, 0.0, 0.6],
    "curry":        [0.0, 0.1, 0.0, 0.1, 0.3, 0.5, 0.0, 0.9],
    "coriander":    [0.1, 0.0, 0.1, 0.0, 0.1, 0.0, 0.0, 0.8],
    
    # === OILS & FATS ===
    "olive oil":    [0.0, 0.0, 0.0, 0.1, 0.1, 0.0, 0.8, 0.4],
    "sesame oil":   [0.0, 0.0, 0.0, 0.0, 0.3, 0.0, 0.7, 0.8],
    "coconut oil":  [0.2, 0.0, 0.0, 0.0, 0.0, 0.0, 0.8, 0.4],
    "vegetable oil":[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.7, 0.0],
    
    # === FRUITS ===
    "apple":        [0.7, 0.0, 0.3, 0.0, 0.0, 0.0, 0.0, 0.3],
    "banana":       [0.8, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.4],
    "orange":       [0.6, 0.0, 0.5, 0.1, 0.0, 0.0, 0.0, 0.6],
    "mango":        [0.8, 0.0, 0.2, 0.0, 0.0, 0.0, 0.0, 0.7],
    "pineapple":    [0.7, 0.0, 0.5, 0.0, 0.0, 0.0, 0.0, 0.5],
    "berries":      [0.5, 0.0, 0.4, 0.0, 0.0, 0.0, 0.0, 0.4],
    
    # === NUTS ===
    "almonds":      [0.1, 0.0, 0.0, 0.1, 0.2, 0.0, 0.5, 0.3],
    "peanuts":      [0.1, 0.1, 0.0, 0.0, 0.3, 0.0, 0.5, 0.4],
    "walnuts":      [0.0, 0.0, 0.0, 0.2, 0.2, 0.0, 0.6, 0.3],
    "cashews":      [0.2, 0.0, 0.0, 0.0, 0.2, 0.0, 0.5, 0.2],
    
    # === LEGUMES ===
    "chickpeas":    [0.0, 0.0, 0.0, 0.0, 0.3, 0.0, 0.1, 0.2],
    "lentils":      [0.0, 0.0, 0.0, 0.0, 0.4, 0.0, 0.1, 0.2],
    "black beans":  [0.0, 0.0, 0.0, 0.0, 0.4, 0.0, 0.1, 0.2],
    
    # === OTHER ===
    "coconut milk": [0.3, 0.0, 0.0, 0.0, 0.1, 0.0, 0.7, 0.5],
    "stock":        [0.0, 0.4, 0.0, 0.0, 0.7, 0.0, 0.2, 0.4],
    "wine":         [0.1, 0.0, 0.4, 0.2, 0.2, 0.0, 0.0, 0.5],
    "beer":         [0.1, 0.0, 0.1, 0.4, 0.2, 0.0, 0.0, 0.4],
    "chocolate":    [0.4, 0.0, 0.0, 0.5, 0.1, 0.0, 0.4, 0.6],
    "coffee":       [0.0, 0.0, 0.0, 0.7, 0.1, 0.0, 0.0, 0.8],
    "vanilla":      [0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.9],
}


def get_flavor_vector(ingredient: str) -> list[float]:
    """Get the flavor vector for an ingredient."""
    ing_lower = ingredient.lower()
    
    # Direct match
    if ing_lower in INGREDIENT_FLAVORS:
        return INGREDIENT_FLAVORS[ing_lower]
    
    # Partial match
    for key, vector in INGREDIENT_FLAVORS.items():
        if key in ing_lower or ing_lower in key:
            return vector
    
    # Default neutral flavor
    return [0.0] * N_FLAVORS


def identify_ingredient(ingredient_str: str) -> Optional[str]:
    """Identify which standard ingredient matches the string."""
    ing_lower = ingredient_str.lower()
    
    for key in INGREDIENT_FLAVORS.keys():
        if key in ing_lower:
            return key
    
    return None


def calculate_recipe_flavor(ingredients: list[str]) -> dict:
    """
    Calculate the overall flavor profile of a recipe.
    
    Returns a dictionary with:
    - raw_vector: The summed flavor values
    - normalized_vector: Values scaled to 0-1 range
    - dominant_flavors: Top 3 flavor characteristics
    - flavor_description: Human-readable description
    """
    # Sum all ingredient flavor vectors
    total_vector = [0.0] * N_FLAVORS
    ingredient_contributions = []
    
    for ing in ingredients:
        flavor = get_flavor_vector(ing)
        identified = identify_ingredient(ing)
        
        if identified:
            ingredient_contributions.append({
                "ingredient": identified,
                "vector": flavor
            })
        
        for i in range(N_FLAVORS):
            total_vector[i] += flavor[i]
    
    # Normalize to 0-1 range
    max_val = max(total_vector) if max(total_vector) > 0 else 1
    normalized = [round(v / max_val, 2) for v in total_vector]
    
    # Find dominant flavors
    flavor_scores = list(zip(FLAVOR_DIMENSIONS, normalized))
    flavor_scores.sort(key=lambda x: x[1], reverse=True)
    dominant = [f for f, s in flavor_scores[:3] if s > 0.3]
    
    # Generate description
    descriptions = []
    for flavor, score in flavor_scores:
        if score >= 0.7:
            descriptions.append(f"very {flavor}")
        elif score >= 0.4:
            descriptions.append(flavor)
    
    description = ", ".join(descriptions[:4]) if descriptions else "balanced, mild"
    
    return {
        "raw_vector": [round(v, 2) for v in total_vector],
        "normalized_vector": normalized,
        "dimensions": FLAVOR_DIMENSIONS,
        "dominant_flavors": dominant,
        "flavor_description": description,
        "ingredient_contributions": ingredient_contributions[:10],  # Top 10
    }


def predict_combination_flavor(ingredients_a: list[str], ingredients_b: list[str]) -> dict:
    """
    Predict what flavor profile you get when combining two sets of ingredients.
    Useful for fusion recipe predictions.
    """
    combined = ingredients_a + ingredients_b
    return calculate_recipe_flavor(combined)


def suggest_balancing_ingredient(current_flavors: dict, target_flavor: str) -> list[str]:
    """
    Suggest ingredients to add to balance or enhance a specific flavor.
    """
    suggestions = []
    
    for ing, vector in INGREDIENT_FLAVORS.items():
        flavor_idx = FLAVOR_DIMENSIONS.index(target_flavor)
        if vector[flavor_idx] >= 0.5:
            suggestions.append({
                "ingredient": ing,
                "contribution": vector[flavor_idx]
            })
    
    # Sort by contribution
    suggestions.sort(key=lambda x: x["contribution"], reverse=True)
    
    return suggestions[:10]


def flavor_compatibility(ing_a: str, ing_b: str) -> float:
    """
    Calculate flavor compatibility between two ingredients.
    Uses cosine similarity of flavor vectors.
    """
    vec_a = get_flavor_vector(ing_a)
    vec_b = get_flavor_vector(ing_b)
    
    # Cosine similarity
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = sum(a * a for a in vec_a) ** 0.5
    norm_b = sum(b * b for b in vec_b) ** 0.5
    
    if norm_a > 0 and norm_b > 0:
        return round(dot / (norm_a * norm_b), 3)
    return 0.0


# ============================================================
# DATABASE FUNCTIONS
# ============================================================

def get_recipe_flavor_from_db(db: Session, recipe_id: str) -> Optional[Dict]:
    """Get pre-computed flavor profile from database."""
    from ..models import Recipe, RecipeFlavorProfile
    
    recipe = db.query(Recipe).filter(
        (Recipe.external_id == recipe_id) | 
        (Recipe.id == int(recipe_id) if recipe_id.isdigit() else -1)
    ).first()
    
    if recipe and recipe.flavor_profile:
        return recipe.flavor_profile.to_dict()
    return None


def get_ingredient_flavor_from_db(db: Session, ingredient_name: str) -> Optional[List[float]]:
    """Get ingredient flavor vector from database."""
    from ..models import Ingredient, IngredientFlavor
    
    ingredient = db.query(Ingredient).filter(
        Ingredient.name == ingredient_name.lower()
    ).first()
    
    if ingredient and ingredient.flavor:
        return ingredient.flavor.to_vector()
    
    # Fall back to in-memory dict
    return get_flavor_vector(ingredient_name)


def calculate_recipe_flavor_db(db: Session, recipe_id: str) -> Optional[Dict]:
    """
    Get or calculate flavor profile for a recipe.
    Uses pre-computed profile from database if available.
    """
    # Try database first
    db_profile = get_recipe_flavor_from_db(db, recipe_id)
    if db_profile:
        return {
            "raw_vector": None,  # Not stored
            "normalized_vector": list(db_profile['dimensions'].values()),
            "dimensions": FLAVOR_DIMENSIONS,
            "dominant_flavors": db_profile['dominant_flavors'],
            "flavor_description": db_profile['description'],
            "ingredient_contributions": [],
        }
    
    # Fall back to calculation
    from ..models import Recipe
    recipe = db.query(Recipe).filter(
        (Recipe.external_id == recipe_id) | 
        (Recipe.id == int(recipe_id) if recipe_id.isdigit() else -1)
    ).first()
    
    if recipe:
        ingredients = [ri.original_text or ri.ingredient_name for ri in recipe.ingredients]
        return calculate_recipe_flavor(ingredients)
    
    return None


def get_recipes_by_flavor_db(
    db: Session,
    target_profile: Dict[str, float],
    limit: int = 10
) -> List[Dict]:
    """Find recipes that match a target flavor profile."""
    from ..models import Recipe, RecipeFlavorProfile
    
    recipes = db.query(Recipe).join(RecipeFlavorProfile).all()
    
    distances = []
    for recipe in recipes:
        if not recipe.flavor_profile:
            continue
        
        profile = recipe.flavor_profile
        dist = (
            (profile.sweet - target_profile.get('sweet', 0)) ** 2 +
            (profile.salty - target_profile.get('salty', 0)) ** 2 +
            (profile.sour - target_profile.get('sour', 0)) ** 2 +
            (profile.bitter - target_profile.get('bitter', 0)) ** 2 +
            (profile.umami - target_profile.get('umami', 0)) ** 2 +
            (profile.spicy - target_profile.get('spicy', 0)) ** 2 +
            (profile.fatty - target_profile.get('fatty', 0)) ** 2 +
            (profile.aromatic - target_profile.get('aromatic', 0)) ** 2
        ) ** 0.5
        
        distances.append((recipe, dist))
    
    distances.sort(key=lambda x: x[1])
    
    return [
        {
            "recipe": r.to_dict(),
            "flavor_distance": round(d, 3),
            "flavor_profile": r.flavor_profile.to_dict() if r.flavor_profile else None
        }
        for r, d in distances[:limit]
    ]


def update_user_flavor_profile(
    db: Session,
    user_id: int,
    recipe_id: str,
    interaction_type: str,
    weight: float = None
) -> Dict[str, float]:
    """
    Update user's flavor profile based on recipe interaction.
    
    interaction_type: view, like, cook, shop
    """
    from ..models import UserFlavorProfile, Recipe
    
    # Get or create user profile
    profile = db.query(UserFlavorProfile).filter(
        UserFlavorProfile.user_id == user_id
    ).first()
    
    if not profile:
        profile = UserFlavorProfile(user_id=user_id)
        db.add(profile)
    
    # Get recipe flavor profile
    recipe = db.query(Recipe).filter(
        (Recipe.external_id == recipe_id) | 
        (Recipe.id == int(recipe_id) if recipe_id.isdigit() else -1)
    ).first()
    
    if not recipe or not recipe.flavor_profile:
        db.commit()
        return profile.to_vector() if hasattr(profile, 'to_vector') else {}
    
    recipe_flavor = recipe.flavor_profile
    
    # Determine weight based on interaction type
    if weight is None:
        weights = {
            'view': 0.1,
            'like': 0.3,
            'cook': 0.5,
            'shop': 0.2,
        }
        weight = weights.get(interaction_type, 0.1)
    
    # Update profile using exponential moving average
    decay = 0.95  # How much to retain existing profile
    
    profile.sweet = decay * profile.sweet + weight * recipe_flavor.sweet
    profile.salty = decay * profile.salty + weight * recipe_flavor.salty
    profile.sour = decay * profile.sour + weight * recipe_flavor.sour
    profile.bitter = decay * profile.bitter + weight * recipe_flavor.bitter
    profile.umami = decay * profile.umami + weight * recipe_flavor.umami
    profile.spicy = decay * profile.spicy + weight * recipe_flavor.spicy
    profile.fatty = decay * profile.fatty + weight * recipe_flavor.fatty
    profile.aromatic = decay * profile.aromatic + weight * recipe_flavor.aromatic
    profile.interaction_count += 1
    
    db.commit()
    
    return {
        "sweet": round(profile.sweet, 3),
        "salty": round(profile.salty, 3),
        "sour": round(profile.sour, 3),
        "bitter": round(profile.bitter, 3),
        "umami": round(profile.umami, 3),
        "spicy": round(profile.spicy, 3),
        "fatty": round(profile.fatty, 3),
        "aromatic": round(profile.aromatic, 3),
    }


# Quick test
if __name__ == "__main__":
    test_ingredients = [
        "chicken breast",
        "garlic",
        "soy sauce",
        "ginger",
        "sesame oil",
        "rice"
    ]
    
    print("=== Flavor Analysis: Asian Chicken ===")
    result = calculate_recipe_flavor(test_ingredients)
    
    print(f"\nFlavor Profile:")
    for dim, val in zip(FLAVOR_DIMENSIONS, result['normalized_vector']):
        bar = "█" * int(val * 20)
        print(f"  {dim:10}: {bar} ({val:.2f})")
    
    print(f"\nDominant: {result['dominant_flavors']}")
    print(f"Description: {result['flavor_description']}")
    
    print("\n=== Compatibility Test ===")
    print(f"Chicken + Lemon: {flavor_compatibility('chicken', 'lemon')}")
    print(f"Chocolate + Chili: {flavor_compatibility('chocolate', 'chili')}")
    print(f"Beef + Mushroom: {flavor_compatibility('beef', 'mushroom')}")
