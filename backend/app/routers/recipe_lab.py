"""
Recipe Lab API Endpoints

Linear algebra operations on recipes:
- Fusion: Combine two recipes
- Generate: Create random recipes
- Remix: Swap ingredients
- Similar: Find similar recipes
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import json
from pathlib import Path

from ..services.recipe_lab import (
    fuse_recipes,
    generate_random_recipe,
    remix_recipe,
    find_similar_recipes,
    load_recipes,
    ingredient_to_vector,
    INGREDIENTS,
)
from ..services.flavor_matrix import (
    calculate_recipe_flavor,
    predict_combination_flavor,
    suggest_balancing_ingredient,
    flavor_compatibility,
    FLAVOR_DIMENSIONS,
    INGREDIENT_FLAVORS,
)

router = APIRouter(prefix="/api/lab", tags=["Recipe Lab"])


class FusionRequest(BaseModel):
    recipe_a_id: str
    recipe_b_id: str
    ratio: float = 0.5  # 0.5 = equal blend


class RandomRequest(BaseModel):
    cuisine: Optional[str] = None
    protein: Optional[str] = None
    difficulty: str = "easy"


class RemixRequest(BaseModel):
    recipe_id: str
    swap_ingredient: str
    new_ingredient: str


class SimilarRequest(BaseModel):
    recipe_id: str
    top_n: int = 5


def get_recipe_by_id(recipes: list, recipe_id: str) -> dict:
    """Find recipe by ID."""
    for r in recipes:
        if str(r.get('id')) == str(recipe_id):
            return r
    return None


@router.post("/fuse")
async def fuse_two_recipes(request: FusionRequest):
    """
    Fuse two recipes together using vector addition.
    
    The fusion combines ingredients from both recipes and blends
    cooking techniques.
    """
    recipes = load_recipes()
    
    recipe_a = get_recipe_by_id(recipes, request.recipe_a_id)
    recipe_b = get_recipe_by_id(recipes, request.recipe_b_id)
    
    if not recipe_a:
        raise HTTPException(status_code=404, detail=f"Recipe A not found: {request.recipe_a_id}")
    if not recipe_b:
        raise HTTPException(status_code=404, detail=f"Recipe B not found: {request.recipe_b_id}")
    
    fused = fuse_recipes(recipe_a, recipe_b, request.ratio)
    
    return {
        "success": True,
        "fused_recipe": fused,
        "source_a": recipe_a.get('name'),
        "source_b": recipe_b.get('name'),
        "operation": f"Recipe_Fusion = {request.ratio:.0%} × A + {1-request.ratio:.0%} × B"
    }


@router.post("/random")
async def generate_random(request: RandomRequest):
    """
    Generate a random recipe by sampling from ingredient space.
    
    Optionally specify cuisine, protein preference, or difficulty.
    """
    recipe = generate_random_recipe(
        base_cuisine=request.cuisine,
        protein=request.protein,
        difficulty=request.difficulty
    )
    
    return {
        "success": True,
        "recipe": recipe,
        "operation": "Recipe_Random = sample(ingredient_space) × method_matrix"
    }


@router.post("/remix")
async def remix_existing_recipe(request: RemixRequest):
    """
    Remix a recipe by swapping one ingredient for another.
    
    This performs: Recipe_New = Recipe - old_ingredient + new_ingredient
    """
    recipes = load_recipes()
    
    original = get_recipe_by_id(recipes, request.recipe_id)
    if not original:
        raise HTTPException(status_code=404, detail=f"Recipe not found: {request.recipe_id}")
    
    remixed = remix_recipe(original, request.swap_ingredient, request.new_ingredient)
    
    return {
        "success": True,
        "original_recipe": original.get('name'),
        "remixed_recipe": remixed,
        "operation": f"Recipe_New = Recipe - {request.swap_ingredient} + {request.new_ingredient}"
    }


@router.post("/similar")
async def find_similar(request: SimilarRequest):
    """
    Find similar recipes using cosine similarity on ingredient vectors.
    """
    recipes = load_recipes()
    
    target = get_recipe_by_id(recipes, request.recipe_id)
    if not target:
        raise HTTPException(status_code=404, detail=f"Recipe not found: {request.recipe_id}")
    
    similar = find_similar_recipes(target, recipes, request.top_n)
    
    return {
        "success": True,
        "target_recipe": target.get('name'),
        "similar_recipes": similar,
        "operation": "similarity = cos(θ) = (A · B) / (||A|| × ||B||)"
    }


@router.get("/ingredients")
async def get_ingredient_space():
    """
    Get the ingredient vector space definition.
    """
    return {
        "ingredients": INGREDIENTS,
        "dimension": len(INGREDIENTS),
        "description": "Standard ingredient basis vectors for recipe representation"
    }


@router.get("/recipe-vector/{recipe_id}")
async def get_recipe_vector(recipe_id: str):
    """
    Get the ingredient vector representation of a recipe.
    """
    recipes = load_recipes()
    recipe = get_recipe_by_id(recipes, recipe_id)
    
    if not recipe:
        raise HTTPException(status_code=404, detail=f"Recipe not found: {recipe_id}")
    
    vector = ingredient_to_vector(recipe.get('ingredients', []))
    
    # Create labeled vector
    labeled = {INGREDIENTS[i]: vector[i] for i in range(len(INGREDIENTS)) if vector[i] > 0}
    
    return {
        "recipe_name": recipe.get('name'),
        "vector": vector,
        "labeled_vector": labeled,
        "dimension": len(vector),
        "non_zero_count": sum(vector)
    }


# ============================================================
# FLAVOR ANALYSIS ENDPOINTS
# ============================================================

class FlavorRequest(BaseModel):
    recipe_id: Optional[str] = None
    ingredients: Optional[list[str]] = None


class CompatibilityRequest(BaseModel):
    ingredient_a: str
    ingredient_b: str


class BalanceRequest(BaseModel):
    recipe_id: str
    target_flavor: str


@router.post("/flavor/analyze")
async def analyze_flavor(request: FlavorRequest):
    """
    Analyze the flavor profile of a recipe.
    
    Each ingredient has a flavor vector: [sweet, salty, sour, bitter, umami, spicy, fatty, aromatic]
    The recipe's flavor is the sum of all ingredient flavor vectors.
    """
    if request.recipe_id:
        recipes = load_recipes()
        recipe = get_recipe_by_id(recipes, request.recipe_id)
        if not recipe:
            raise HTTPException(status_code=404, detail=f"Recipe not found: {request.recipe_id}")
        ingredients = recipe.get('ingredients', [])
        recipe_name = recipe.get('name')
    elif request.ingredients:
        ingredients = request.ingredients
        recipe_name = "Custom ingredients"
    else:
        raise HTTPException(status_code=400, detail="Provide recipe_id or ingredients")
    
    flavor = calculate_recipe_flavor(ingredients)
    
    return {
        "success": True,
        "recipe_name": recipe_name,
        "flavor_profile": flavor,
        "operation": "Flavor = Σ (ingredient_i × flavor_vector_i)"
    }


@router.post("/flavor/compatibility")
async def check_compatibility(request: CompatibilityRequest):
    """
    Check flavor compatibility between two ingredients.
    Uses cosine similarity of flavor vectors.
    """
    score = flavor_compatibility(request.ingredient_a, request.ingredient_b)
    
    if score >= 0.7:
        rating = "Excellent pairing"
    elif score >= 0.5:
        rating = "Good pairing"
    elif score >= 0.3:
        rating = "Interesting contrast"
    else:
        rating = "Bold/unusual pairing"
    
    return {
        "success": True,
        "ingredient_a": request.ingredient_a,
        "ingredient_b": request.ingredient_b,
        "compatibility_score": score,
        "rating": rating,
        "operation": "compatibility = cos(θ) = (A · B) / (||A|| × ||B||)"
    }


@router.post("/flavor/balance")
async def suggest_balance(request: BalanceRequest):
    """
    Suggest ingredients to balance or enhance a specific flavor in a recipe.
    """
    recipes = load_recipes()
    recipe = get_recipe_by_id(recipes, request.recipe_id)
    
    if not recipe:
        raise HTTPException(status_code=404, detail=f"Recipe not found: {request.recipe_id}")
    
    if request.target_flavor not in FLAVOR_DIMENSIONS:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid flavor. Choose from: {FLAVOR_DIMENSIONS}"
        )
    
    # Get current flavor profile
    current = calculate_recipe_flavor(recipe.get('ingredients', []))
    
    # Get suggestions
    suggestions = suggest_balancing_ingredient(current, request.target_flavor)
    
    return {
        "success": True,
        "recipe_name": recipe.get('name'),
        "current_flavor": current,
        "target_flavor": request.target_flavor,
        "suggestions": suggestions,
        "operation": f"Find ingredients where {request.target_flavor} >= 0.5"
    }


@router.get("/flavor/dimensions")
async def get_flavor_dimensions():
    """
    Get the flavor space dimensions.
    """
    return {
        "dimensions": FLAVOR_DIMENSIONS,
        "count": len(FLAVOR_DIMENSIONS),
        "description": "Each ingredient is a vector in this 8-dimensional flavor space"
    }


@router.get("/flavor/ingredient/{ingredient}")
async def get_ingredient_flavor(ingredient: str):
    """
    Get the flavor vector for a specific ingredient.
    """
    ing_lower = ingredient.lower()
    
    if ing_lower in INGREDIENT_FLAVORS:
        vector = INGREDIENT_FLAVORS[ing_lower]
        labeled = {FLAVOR_DIMENSIONS[i]: vector[i] for i in range(len(FLAVOR_DIMENSIONS))}
        
        return {
            "ingredient": ingredient,
            "vector": vector,
            "labeled": labeled,
            "dominant": [FLAVOR_DIMENSIONS[i] for i, v in enumerate(vector) if v >= 0.5]
        }
    
    raise HTTPException(status_code=404, detail=f"Ingredient not found: {ingredient}")
