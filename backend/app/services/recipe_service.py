"""Recipe database service for MyFridge - Database version."""
import json
import os
import random
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func

from ..database import SessionLocal
from ..models import Recipe, RecipeVector, RecipeFlavorProfile, RecipeIngredient


class RecipeService:
    """Service for recipe operations using database."""
    
    def __init__(self, db: Session = None):
        self.db = db or SessionLocal()
        self._fallback_recipes = None
    
    def _ensure_db(self):
        """Ensure database session is active."""
        if self.db is None:
            self.db = SessionLocal()
    
    def _use_fallback(self) -> bool:
        """Check if we need to use JSON fallback (no recipes in DB)."""
        try:
            count = self.db.query(Recipe).count()
            return count == 0
        except:
            return True
    
    def _load_fallback(self) -> List[Dict]:
        """Load recipes from JSON file as fallback."""
        if self._fallback_recipes is not None:
            return self._fallback_recipes
        
        try:
            data_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'data',
                'recipes.json'
            )
            with open(data_path, 'r', encoding='utf-8') as f:
                self._fallback_recipes = json.load(f)
            print(f"📁 Loaded {len(self._fallback_recipes)} recipes from JSON fallback")
        except Exception as e:
            print(f"⚠️ Error loading fallback recipes: {e}")
            self._fallback_recipes = []
        
        return self._fallback_recipes
    
    def get_all_recipes(self) -> List[Dict]:
        """Get all recipes."""
        self._ensure_db()
        
        if self._use_fallback():
            return self._load_fallback()
        
        recipes = self.db.query(Recipe).all()
        return [r.to_dict() for r in recipes]
    
    def get_recipe_by_id(self, recipe_id: str) -> Optional[Dict]:
        """Get a specific recipe by ID."""
        self._ensure_db()
        
        if self._use_fallback():
            for recipe in self._load_fallback():
                if recipe.get('id') == recipe_id:
                    return recipe
            return None
        
        # Try external_id first, then internal id
        recipe = self.db.query(Recipe).filter(
            or_(Recipe.external_id == recipe_id, Recipe.id == int(recipe_id) if recipe_id.isdigit() else -1)
        ).first()
        
        return recipe.to_dict() if recipe else None
    
    def get_recipe_db_object(self, recipe_id: str) -> Optional[Recipe]:
        """Get recipe as database object."""
        self._ensure_db()
        
        return self.db.query(Recipe).filter(
            or_(Recipe.external_id == recipe_id, Recipe.id == int(recipe_id) if recipe_id.isdigit() else -1)
        ).first()
    
    def search_recipes(
        self,
        query: Optional[str] = None,
        tags: Optional[List[str]] = None,
        max_time: Optional[int] = None,
        cuisine: Optional[str] = None,
        difficulty: Optional[str] = None
    ) -> List[Dict]:
        """Search recipes with filters."""
        self._ensure_db()
        
        if self._use_fallback():
            return self._search_fallback(query, tags, max_time, cuisine, difficulty)
        
        q = self.db.query(Recipe)
        
        # Text search
        if query:
            query_lower = f"%{query.lower()}%"
            q = q.filter(
                or_(
                    func.lower(Recipe.name).like(query_lower),
                    func.lower(Recipe.description).like(query_lower)
                )
            )
        
        # Time filter
        if max_time:
            q = q.filter(Recipe.total_time <= max_time)
        
        # Cuisine filter
        if cuisine:
            q = q.filter(func.lower(Recipe.cuisine) == cuisine.lower())
        
        # Difficulty filter
        if difficulty:
            q = q.filter(func.lower(Recipe.difficulty) == difficulty.lower())
        
        recipes = q.all()
        results = [r.to_dict() for r in recipes]
        
        # Tag filter (JSON field)
        if tags:
            results = [
                r for r in results
                if any(tag in (r.get('tags') or []) for tag in tags)
            ]
        
        return results
    
    def _search_fallback(
        self,
        query: Optional[str] = None,
        tags: Optional[List[str]] = None,
        max_time: Optional[int] = None,
        cuisine: Optional[str] = None,
        difficulty: Optional[str] = None
    ) -> List[Dict]:
        """Fallback search using JSON."""
        results = self._load_fallback().copy()
        
        if query:
            query_lower = query.lower()
            results = [
                r for r in results
                if query_lower in r.get('name', '').lower() or
                   query_lower in r.get('description', '').lower() or
                   any(query_lower in ing.lower() for ing in r.get('ingredients', []))
            ]
        
        if tags:
            results = [
                r for r in results
                if any(tag in r.get('tags', []) for tag in tags)
            ]
        
        if max_time:
            results = [
                r for r in results
                if r.get('total_time', 999) <= max_time
            ]
        
        if cuisine:
            results = [
                r for r in results
                if r.get('cuisine', '').lower() == cuisine.lower()
            ]
        
        if difficulty:
            results = [
                r for r in results
                if r.get('difficulty', '').lower() == difficulty.lower()
            ]
        
        return results
    
    def get_quick_recipes(self, max_time: int = 15, limit: int = 10) -> List[Dict]:
        """Get quick recipes (under specified time)."""
        quick = self.search_recipes(max_time=max_time)
        random.shuffle(quick)
        return quick[:limit]
    
    def get_recipes_by_ingredients(self, ingredients: List[str], limit: int = 10) -> List[Dict]:
        """Find recipes that use the given ingredients."""
        self._ensure_db()
        
        if self._use_fallback():
            return self._recipes_by_ingredients_fallback(ingredients, limit)
        
        # Use database query with ingredient matching
        all_recipes = self.db.query(Recipe).all()
        scored_recipes = []
        
        for recipe in all_recipes:
            recipe_dict = recipe.to_dict()
            recipe_ingredients = ' '.join(recipe_dict.get('ingredients', [])).lower()
            
            match_count = sum(1 for ing in ingredients if ing.lower() in recipe_ingredients)
            
            if match_count > 0:
                scored_recipes.append({
                    'recipe': recipe_dict,
                    'matches': match_count,
                    'match_ratio': match_count / len(ingredients)
                })
        
        scored_recipes.sort(key=lambda x: x['matches'], reverse=True)
        return [sr['recipe'] for sr in scored_recipes[:limit]]
    
    def _recipes_by_ingredients_fallback(self, ingredients: List[str], limit: int) -> List[Dict]:
        """Fallback ingredient search using JSON."""
        scored_recipes = []
        
        for recipe in self._load_fallback():
            recipe_ingredients = ' '.join(recipe.get('ingredients', [])).lower()
            match_count = sum(1 for ing in ingredients if ing.lower() in recipe_ingredients)
            
            if match_count > 0:
                scored_recipes.append({
                    'recipe': recipe,
                    'matches': match_count,
                    'match_ratio': match_count / len(ingredients)
                })
        
        scored_recipes.sort(key=lambda x: x['matches'], reverse=True)
        return [sr['recipe'] for sr in scored_recipes[:limit]]
    
    def get_random_recipes(self, count: int = 5) -> List[Dict]:
        """Get random recipes for exploration."""
        self._ensure_db()
        
        if self._use_fallback():
            shuffled = self._load_fallback().copy()
            random.shuffle(shuffled)
            return shuffled[:count]
        
        # Random sampling from database
        recipes = self.db.query(Recipe).order_by(func.random()).limit(count).all()
        return [r.to_dict() for r in recipes]
    
    def get_recipes_by_tags(self, tags: List[str], limit: int = 10) -> List[Dict]:
        """Get recipes filtered by specific tags."""
        return self.search_recipes(tags=tags)[:limit]
    
    # =========================================================================
    # NEW: Vector-based similarity methods
    # =========================================================================
    
    def get_recipe_vector(self, recipe_id: str) -> Optional[List[int]]:
        """Get the ingredient vector for a recipe."""
        self._ensure_db()
        
        recipe = self.get_recipe_db_object(recipe_id)
        if not recipe or not recipe.vector:
            return None
        
        return recipe.vector.to_list()
    
    def get_similar_recipes(self, recipe_id: str, limit: int = 5) -> List[Dict]:
        """Find similar recipes using cosine similarity on ingredient vectors."""
        self._ensure_db()
        
        target_recipe = self.get_recipe_db_object(recipe_id)
        if not target_recipe or not target_recipe.vector:
            return []
        
        target_vec = target_recipe.vector.to_list()
        
        # Get all other recipes with vectors
        recipes = self.db.query(Recipe).filter(Recipe.id != target_recipe.id).all()
        
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
        
        # Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        results = []
        for recipe, sim in similarities[:limit]:
            recipe_dict = recipe.to_dict()
            recipe_dict['similarity'] = round(sim, 3)
            results.append(recipe_dict)
        
        return results
    
    def get_recipe_flavor_profile(self, recipe_id: str) -> Optional[Dict]:
        """Get the flavor profile for a recipe."""
        self._ensure_db()
        
        recipe = self.get_recipe_db_object(recipe_id)
        if not recipe or not recipe.flavor_profile:
            return None
        
        return recipe.flavor_profile.to_dict()
    
    def get_recipes_by_flavor_profile(
        self,
        target_profile: Dict[str, float],
        limit: int = 10
    ) -> List[Dict]:
        """Find recipes that match a target flavor profile."""
        self._ensure_db()
        
        recipes = self.db.query(Recipe).join(RecipeFlavorProfile).all()
        
        distances = []
        for recipe in recipes:
            if not recipe.flavor_profile:
                continue
            
            # Calculate Euclidean distance
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
        
        # Sort by distance (lower is better match)
        distances.sort(key=lambda x: x[1])
        
        results = []
        for recipe, dist in distances[:limit]:
            recipe_dict = recipe.to_dict()
            recipe_dict['flavor_distance'] = round(dist, 3)
            recipe_dict['flavor_profile'] = recipe.flavor_profile.to_dict() if recipe.flavor_profile else None
            results.append(recipe_dict)
        
        return results
    
    def close(self):
        """Close the database session."""
        if self.db:
            self.db.close()


# Global recipe service instance
_recipe_service = None

def get_recipe_service() -> RecipeService:
    """Get or create recipe service singleton."""
    global _recipe_service
    if _recipe_service is None:
        _recipe_service = RecipeService()
    return _recipe_service


def get_recipe_service_with_db(db: Session) -> RecipeService:
    """Get recipe service with specific database session."""
    return RecipeService(db)
