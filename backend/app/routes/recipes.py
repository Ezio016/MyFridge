"""Recipe routes for MyFridge."""
from fastapi import APIRouter, Query
from typing import List, Optional
from pydantic import BaseModel

from ..services.recipe_service import get_recipe_service

router = APIRouter(prefix="/recipes", tags=["recipes"])

class RecipeSearchRequest(BaseModel):
    """Request model for recipe search."""
    query: Optional[str] = None
    tags: Optional[List[str]] = None
    max_time: Optional[int] = None
    cuisine: Optional[str] = None
    difficulty: Optional[str] = None


@router.get("/")
async def get_all_recipes():
    """Get all recipes from the database."""
    recipe_service = get_recipe_service()
    recipes = recipe_service.get_all_recipes()
    return {"recipes": recipes, "count": len(recipes)}


@router.get("/random")
async def get_random_recipes(count: int = Query(default=5, ge=1, le=20)):
    """Get random recipes for exploration."""
    recipe_service = get_recipe_service()
    recipes = recipe_service.get_random_recipes(count)
    return {"recipes": recipes, "count": len(recipes)}


@router.get("/quick")
async def get_quick_recipes(
    max_time: int = Query(default=15, ge=1, le=120),
    limit: int = Query(default=10, ge=1, le=50)
):
    """Get quick recipes under specified time."""
    recipe_service = get_recipe_service()
    recipes = recipe_service.get_quick_recipes(max_time, limit)
    return {"recipes": recipes, "count": len(recipes), "max_time": max_time}


@router.get("/{recipe_id}")
async def get_recipe(recipe_id: str):
    """Get a specific recipe by ID."""
    recipe_service = get_recipe_service()
    recipe = recipe_service.get_recipe_by_id(recipe_id)
    
    if not recipe:
        return {"error": "Recipe not found"}, 404
    
    return {"recipe": recipe}


@router.post("/search")
async def search_recipes(search_request: RecipeSearchRequest):
    """Search recipes with various filters."""
    recipe_service = get_recipe_service()
    recipes = recipe_service.search_recipes(
        query=search_request.query,
        tags=search_request.tags,
        max_time=search_request.max_time,
        cuisine=search_request.cuisine,
        difficulty=search_request.difficulty
    )
    return {"recipes": recipes, "count": len(recipes)}


@router.post("/by-ingredients")
async def get_recipes_by_ingredients(
    ingredients: List[str],
    limit: int = Query(default=10, ge=1, le=50)
):
    """Find recipes that match given ingredients."""
    recipe_service = get_recipe_service()
    recipes = recipe_service.get_recipes_by_ingredients(ingredients, limit)
    return {
        "recipes": recipes,
        "count": len(recipes),
        "searched_ingredients": ingredients
    }


@router.get("/tags/{tag}")
async def get_recipes_by_tag(
    tag: str,
    limit: int = Query(default=10, ge=1, le=50)
):
    """Get recipes filtered by a specific tag."""
    recipe_service = get_recipe_service()
    recipes = recipe_service.get_recipes_by_tags([tag], limit)
    return {"recipes": recipes, "count": len(recipes), "tag": tag}

