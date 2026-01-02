"""Recipe database service for MyFridge."""
import json
import os
from typing import List, Dict, Optional
import random

class RecipeService:
    def __init__(self):
        self.recipes = []
        self.load_recipes()
    
    def load_recipes(self):
        """Load recipes from JSON file."""
        try:
            data_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                'data',
                'recipes.json'
            )
            with open(data_path, 'r', encoding='utf-8') as f:
                self.recipes = json.load(f)
            print(f"✅ Loaded {len(self.recipes)} recipes from database")
        except Exception as e:
            print(f"⚠️ Error loading recipes: {e}")
            self.recipes = []
    
    def get_all_recipes(self) -> List[Dict]:
        """Get all recipes."""
        return self.recipes
    
    def get_recipe_by_id(self, recipe_id: str) -> Optional[Dict]:
        """Get a specific recipe by ID."""
        for recipe in self.recipes:
            if recipe.get('id') == recipe_id:
                return recipe
        return None
    
    def search_recipes(
        self,
        query: Optional[str] = None,
        tags: Optional[List[str]] = None,
        max_time: Optional[int] = None,
        cuisine: Optional[str] = None,
        difficulty: Optional[str] = None
    ) -> List[Dict]:
        """
        Search recipes with filters.
        
        Args:
            query: Search in recipe name and description
            tags: Filter by tags (e.g., 'vegetarian', 'quick')
            max_time: Maximum total cooking time in minutes
            cuisine: Filter by cuisine type
            difficulty: Filter by difficulty level
        """
        results = self.recipes.copy()
        
        # Text search
        if query:
            query_lower = query.lower()
            results = [
                r for r in results
                if query_lower in r['name'].lower() or
                   query_lower in r['description'].lower() or
                   any(query_lower in ing.lower() for ing in r['ingredients'])
            ]
        
        # Tag filter
        if tags:
            results = [
                r for r in results
                if any(tag in r['tags'] for tag in tags)
            ]
        
        # Time filter
        if max_time:
            results = [
                r for r in results
                if r['total_time'] <= max_time
            ]
        
        # Cuisine filter
        if cuisine:
            results = [
                r for r in results
                if r['cuisine'].lower() == cuisine.lower()
            ]
        
        # Difficulty filter
        if difficulty:
            results = [
                r for r in results
                if r['difficulty'].lower() == difficulty.lower()
            ]
        
        return results
    
    def get_quick_recipes(self, max_time: int = 15, limit: int = 10) -> List[Dict]:
        """Get quick recipes (under specified time)."""
        quick = self.search_recipes(max_time=max_time)
        random.shuffle(quick)
        return quick[:limit]
    
    def get_recipes_by_ingredients(self, ingredients: List[str], limit: int = 10) -> List[Dict]:
        """Find recipes that use the given ingredients."""
        scored_recipes = []
        
        for recipe in self.recipes:
            match_count = 0
            recipe_ingredients = ' '.join(recipe['ingredients']).lower()
            
            for ingredient in ingredients:
                if ingredient.lower() in recipe_ingredients:
                    match_count += 1
            
            if match_count > 0:
                scored_recipes.append({
                    'recipe': recipe,
                    'matches': match_count,
                    'match_ratio': match_count / len(ingredients)
                })
        
        # Sort by number of matching ingredients
        scored_recipes.sort(key=lambda x: x['matches'], reverse=True)
        
        return [sr['recipe'] for sr in scored_recipes[:limit]]
    
    def get_random_recipes(self, count: int = 5) -> List[Dict]:
        """Get random recipes for exploration."""
        shuffled = self.recipes.copy()
        random.shuffle(shuffled)
        return shuffled[:count]
    
    def get_recipes_by_tags(self, tags: List[str], limit: int = 10) -> List[Dict]:
        """Get recipes filtered by specific tags."""
        return self.search_recipes(tags=tags)[:limit]


# Global recipe service instance
_recipe_service = None

def get_recipe_service() -> RecipeService:
    """Get or create recipe service singleton."""
    global _recipe_service
    if _recipe_service is None:
        _recipe_service = RecipeService()
    return _recipe_service

