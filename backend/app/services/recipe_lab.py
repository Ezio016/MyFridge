"""
Recipe Lab - Linear Algebra Operations on Recipes (Database Version)

Features:
1. Recipe Fusion - Combine two recipes into one
2. Random Recipe Generation - Create new recipes from ingredient space
3. Recipe Remix - Swap ingredients while keeping cooking style
4. Recipe Arithmetic - Recipe_A - Ingredient + New_Ingredient
5. Vector Similarity - Find similar recipes using pre-computed vectors
"""

import random
from typing import Optional, List, Dict
from sqlalchemy.orm import Session

from ..database import SessionLocal
from ..models import Recipe, RecipeVector, RecipeFlavorProfile
from .recipe_service import get_recipe_service


# Standard ingredients for vector representation
INGREDIENTS = [
    "chicken", "beef", "pork", "fish", "eggs", "tofu",
    "milk", "butter", "cheese", "cream",
    "onion", "garlic", "tomato", "potato", "carrot",
    "pepper", "mushroom", "spinach", "broccoli", "zucchini",
    "rice", "pasta", "bread", "flour", "noodles",
    "olive oil", "vegetable oil", "sesame oil",
    "salt", "sugar", "soy sauce", "vinegar", "lemon",
    "basil", "parsley", "cilantro", "thyme", "oregano",
    "cumin", "paprika", "chili", "ginger", "garlic powder"
]

COOKING_METHODS = [
    "fry", "sauté", "stir-fry", "boil", "simmer", "steam",
    "bake", "roast", "grill", "broil", "poach", "braise"
]


def ingredient_to_vector(ingredients_list: list[str]) -> list[int]:
    """Convert ingredient list to binary vector."""
    vector = [0] * len(INGREDIENTS)
    for ing in ingredients_list:
        ing_lower = ing.lower()
        for i, std_ing in enumerate(INGREDIENTS):
            if std_ing in ing_lower:
                vector[i] = 1
                break
    return vector


def vector_to_ingredients(vector: list[int], original_ingredients: dict = None) -> list[str]:
    """Convert binary vector back to ingredient list."""
    result = []
    for i, val in enumerate(vector):
        if val >= 1:
            if original_ingredients and INGREDIENTS[i] in original_ingredients:
                result.append(original_ingredients[INGREDIENTS[i]])
            else:
                result.append(f"1 {INGREDIENTS[i]}")
    return result


def extract_cooking_method(instructions: list[str]) -> list[str]:
    """Extract cooking methods from instructions."""
    text = " ".join(instructions).lower()
    found = []
    for method in COOKING_METHODS:
        if method in text:
            found.append(method)
    return found


def get_recipe_vector_from_db(db: Session, recipe_id: str) -> Optional[List[int]]:
    """Get pre-computed vector from database."""
    recipe = db.query(Recipe).filter(
        (Recipe.external_id == recipe_id) | 
        (Recipe.id == (int(recipe_id) if recipe_id.isdigit() else -1))
    ).first()
    
    if recipe and recipe.vector:
        return recipe.vector.to_list()
    return None


def fuse_recipes(recipe_a: dict, recipe_b: dict, ratio: float = 0.5, db: Session = None) -> dict:
    """
    Fuse two recipes together using vector addition.
    
    ratio: 0.5 = equal blend, 0.7 = 70% recipe A, 30% recipe B
    """
    # Try to get pre-computed vectors from database
    vec_a = None
    vec_b = None
    
    if db:
        vec_a = get_recipe_vector_from_db(db, recipe_a.get('id', ''))
        vec_b = get_recipe_vector_from_db(db, recipe_b.get('id', ''))
    
    # Fall back to computing on the fly
    if vec_a is None:
        vec_a = ingredient_to_vector(recipe_a.get('ingredients', []))
    if vec_b is None:
        vec_b = ingredient_to_vector(recipe_b.get('ingredients', []))
    
    # Weighted combination (union of ingredients)
    fused_vector = []
    for i in range(len(INGREDIENTS)):
        if vec_a[i] or vec_b[i]:
            fused_vector.append(1)
        else:
            fused_vector.append(0)
    
    # Build original ingredients map for better names
    orig_ings = {}
    for ing in recipe_a.get('ingredients', []):
        for std in INGREDIENTS:
            if std in ing.lower():
                orig_ings[std] = ing
                break
    for ing in recipe_b.get('ingredients', []):
        for std in INGREDIENTS:
            if std in ing.lower():
                if std not in orig_ings:
                    orig_ings[std] = ing
                break
    
    # Combine cooking methods
    methods_a = extract_cooking_method(recipe_a.get('instructions', []))
    methods_b = extract_cooking_method(recipe_b.get('instructions', []))
    combined_methods = list(set(methods_a + methods_b))
    
    # Generate fusion name
    name_a = recipe_a.get('name', 'Recipe A').split()[0]
    name_b = recipe_b.get('name', 'Recipe B').split()[-1]
    fusion_name = f"{name_a}-{name_b} Fusion"
    
    # Blend times
    time_a = recipe_a.get('total_time', 30)
    time_b = recipe_b.get('total_time', 30)
    if isinstance(time_a, str):
        time_a = 30
    if isinstance(time_b, str):
        time_b = 30
    avg_time = int(time_a * ratio + time_b * (1 - ratio))
    
    # Create fused recipe
    fused = {
        "id": f"fusion_{random.randint(1000, 9999)}",
        "name": fusion_name,
        "description": f"A creative fusion of {recipe_a.get('name', 'Recipe A')} and {recipe_b.get('name', 'Recipe B')}",
        "ingredients": vector_to_ingredients(fused_vector, orig_ings),
        "instructions": [
            f"This fusion combines techniques from both recipes.",
            f"Primary cooking methods: {', '.join(combined_methods) if combined_methods else 'various'}",
            f"Prepare ingredients from both original recipes.",
            f"Follow the cooking style of {recipe_a.get('name', 'Recipe A')} as the base.",
            f"Incorporate elements from {recipe_b.get('name', 'Recipe B')}.",
            "Adjust seasoning to taste and serve."
        ],
        "prep_time": 15,
        "cook_time": avg_time - 15 if avg_time > 15 else avg_time,
        "total_time": avg_time,
        "servings": 4,
        "difficulty": "medium",
        "cuisine": "Fusion",
        "category": recipe_a.get('category', 'main'),
        "tags": ["fusion", "creative", "experimental"],
        "source_recipes": [recipe_a.get('name'), recipe_b.get('name')],
        "fusion_ratio": ratio,
        "ingredient_vector": fused_vector,
    }
    
    return fused


def generate_random_recipe(
    base_cuisine: Optional[str] = None,
    protein: Optional[str] = None,
    difficulty: str = "easy"
) -> dict:
    """Generate a random recipe by sampling from ingredient space."""
    proteins = ["chicken", "beef", "pork", "fish", "eggs", "tofu"]
    vegetables = ["onion", "garlic", "tomato", "potato", "carrot", "pepper", "mushroom", "spinach", "broccoli"]
    carbs = ["rice", "pasta", "bread", "noodles"]
    seasonings = ["salt", "pepper", "soy sauce", "olive oil", "garlic powder", "paprika", "cumin"]
    herbs = ["basil", "parsley", "cilantro", "thyme", "oregano"]
    
    selected_protein = protein if protein else random.choice(proteins)
    selected_veggies = random.sample(vegetables, k=random.randint(2, 4))
    selected_carb = random.choice(carbs)
    selected_seasonings = random.sample(seasonings, k=random.randint(2, 4))
    selected_herb = random.choice(herbs)
    method = random.choice(COOKING_METHODS)
    
    ingredients = [f"1 lb {selected_protein}"]
    for veg in selected_veggies:
        qty = random.choice(["1 cup", "2", "1/2 cup", "1 large"])
        ingredients.append(f"{qty} {veg}")
    ingredients.append(f"2 cups {selected_carb}")
    for season in selected_seasonings:
        ingredients.append(f"1 tbsp {season}" if "oil" in season else f"1 tsp {season}")
    ingredients.append(f"Fresh {selected_herb} for garnish")
    
    adjectives = ["Quick", "Easy", "Savory", "Delicious", "Homestyle", "Classic"]
    name = f"{random.choice(adjectives)} {selected_protein.title()} with {selected_veggies[0].title()}"
    
    recipe = {
        "id": f"random_{random.randint(1000, 9999)}",
        "name": name,
        "description": f"A randomly generated recipe featuring {selected_protein} and fresh vegetables.",
        "ingredients": ingredients,
        "instructions": [
            f"Prepare all ingredients. Cut {selected_protein} into bite-sized pieces.",
            f"Chop {', '.join(selected_veggies)} into similar sizes.",
            f"Heat oil in a large pan over medium-high heat.",
            f"{method.title()} the {selected_protein} until cooked through, about 5-7 minutes.",
            f"Add vegetables and {method} for another 3-4 minutes.",
            f"Season with {', '.join(selected_seasonings[:2])}.",
            f"Serve over {selected_carb}, garnished with fresh {selected_herb}."
        ],
        "prep_time": 10,
        "cook_time": 20,
        "total_time": 30,
        "servings": 4,
        "difficulty": difficulty,
        "cuisine": base_cuisine or "International",
        "category": "main",
        "tags": ["random", "generated", "quick"],
        "cooking_method": method,
        "generated": True,
        "ingredient_vector": ingredient_to_vector(ingredients),
    }
    
    return recipe


def remix_recipe(
    original_recipe: dict,
    swap_ingredient: str,
    new_ingredient: str
) -> dict:
    """
    Remix a recipe by swapping one ingredient for another.
    Recipe_New = Recipe_Original - old_ingredient + new_ingredient
    """
    remixed = original_recipe.copy()
    remixed['id'] = f"remix_{random.randint(1000, 9999)}"
    
    new_ingredients = []
    swapped = False
    for ing in original_recipe.get('ingredients', []):
        if swap_ingredient.lower() in ing.lower() and not swapped:
            parts = ing.split()
            if len(parts) > 1 and (parts[0].replace('.', '').replace('/', '').isdigit() or parts[0] in ['a', 'an']):
                new_ing = f"{parts[0]} {new_ingredient}"
            else:
                new_ing = new_ingredient
            new_ingredients.append(new_ing)
            swapped = True
        else:
            new_ingredients.append(ing)
    
    if not swapped:
        new_ingredients.append(f"1 {new_ingredient}")
    
    remixed['ingredients'] = new_ingredients
    
    old_name = original_recipe.get('name', 'Recipe')
    if swap_ingredient.lower() in old_name.lower():
        remixed['name'] = old_name.replace(swap_ingredient, new_ingredient).replace(swap_ingredient.title(), new_ingredient.title())
    else:
        remixed['name'] = f"{old_name} (with {new_ingredient})"
    
    remixed['description'] = f"A remix of {old_name}, substituting {swap_ingredient} with {new_ingredient}."
    remixed['tags'] = original_recipe.get('tags', []) + ['remix', 'substitution']
    remixed['original_recipe'] = old_name
    remixed['substitution'] = {"from": swap_ingredient, "to": new_ingredient}
    remixed['ingredient_vector'] = ingredient_to_vector(new_ingredients)
    
    return remixed


def find_similar_recipes_db(
    recipe_id: str,
    db: Session,
    top_n: int = 5
) -> List[Dict]:
    """Find similar recipes using pre-computed vectors from database."""
    # Get target recipe vector
    target_recipe = db.query(Recipe).filter(
        (Recipe.external_id == recipe_id) | 
        (Recipe.id == (int(recipe_id) if recipe_id.isdigit() else -1))
    ).first()
    
    if not target_recipe or not target_recipe.vector:
        return []
    
    target_vec = target_recipe.vector.to_list()
    
    # Get all other recipes with vectors
    recipes = db.query(Recipe).filter(Recipe.id != target_recipe.id).all()
    
    similarities = []
    for recipe in recipes:
        if not recipe.vector:
            continue
        
        r_vec = recipe.vector.to_list()
        
        # Cosine similarity
        dot_product = sum(a * b for a, b in zip(target_vec, r_vec))
        norm_a = sum(a * a for a in target_vec) ** 0.5
        norm_b = sum(b * b for b in r_vec) ** 0.5
        
        if norm_a > 0 and norm_b > 0:
            similarity = dot_product / (norm_a * norm_b)
        else:
            similarity = 0
        
        similarities.append((recipe, similarity))
    
    similarities.sort(key=lambda x: x[1], reverse=True)
    
    return [
        {"recipe": r.to_dict(), "similarity": round(s, 3)}
        for r, s in similarities[:top_n]
    ]


def find_similar_recipes(recipe: dict, all_recipes: list[dict] = None, top_n: int = 5) -> list[dict]:
    """Find similar recipes using cosine similarity on ingredient vectors."""
    # Try database first
    if recipe.get('id'):
        db = SessionLocal()
        try:
            results = find_similar_recipes_db(recipe['id'], db, top_n)
            if results:
                return results
        finally:
            db.close()
    
    # Fall back to in-memory calculation
    if all_recipes is None:
        service = get_recipe_service()
        all_recipes = service.get_all_recipes()
    
    target_vec = ingredient_to_vector(recipe.get('ingredients', []))
    
    similarities = []
    for r in all_recipes:
        if r.get('id') == recipe.get('id'):
            continue
        r_vec = ingredient_to_vector(r.get('ingredients', []))
        
        dot_product = sum(a * b for a, b in zip(target_vec, r_vec))
        norm_a = sum(a * a for a in target_vec) ** 0.5
        norm_b = sum(b * b for b in r_vec) ** 0.5
        
        if norm_a > 0 and norm_b > 0:
            similarity = dot_product / (norm_a * norm_b)
        else:
            similarity = 0
        
        similarities.append((r, similarity))
    
    similarities.sort(key=lambda x: x[1], reverse=True)
    
    return [{"recipe": r, "similarity": round(s, 3)} for r, s in similarities[:top_n]]


def load_recipes():
    """Load recipes from database or JSON fallback."""
    service = get_recipe_service()
    return service.get_all_recipes()
