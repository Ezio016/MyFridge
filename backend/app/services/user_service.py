"""User service for profile management and personalized recommendations."""
from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from sqlalchemy import desc

from ..models import (
    User, UserFlavorProfile, UserRecipeInteraction,
    FavoriteRecipe, Recipe, RecipeFlavorProfile, UserFollow
)
from .flavor_matrix import update_user_flavor_profile as update_flavor


def get_user_profile(db: Session, user_id: int) -> Optional[Dict]:
    """Get user's complete profile including flavor preferences."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None
    
    flavor_profile = None
    if user.flavor_profile:
        fp = user.flavor_profile
        flavor_profile = {
            "sweet": fp.sweet,
            "salty": fp.salty,
            "sour": fp.sour,
            "bitter": fp.bitter,
            "umami": fp.umami,
            "spicy": fp.spicy,
            "fatty": fp.fatty,
            "aromatic": fp.aromatic,
            "interaction_count": fp.interaction_count,
        }
    
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "created_at": user.created_at,
        "flavor_profile": flavor_profile,
        "favorite_count": len(user.favorites) if user.favorites else 0,
    }


def get_user_flavor_profile(db: Session, user_id: int) -> Optional[Dict]:
    """Get user's flavor profile."""
    profile = db.query(UserFlavorProfile).filter(
        UserFlavorProfile.user_id == user_id
    ).first()
    
    if not profile:
        return None
    
    return {
        "sweet": profile.sweet,
        "salty": profile.salty,
        "sour": profile.sour,
        "bitter": profile.bitter,
        "umami": profile.umami,
        "spicy": profile.spicy,
        "fatty": profile.fatty,
        "aromatic": profile.aromatic,
        "interaction_count": profile.interaction_count,
        "updated_at": profile.updated_at,
    }


def log_recipe_interaction(
    db: Session,
    user_id: int,
    recipe_id: str,
    interaction_type: str
) -> Dict:
    """
    Log a user's interaction with a recipe and update flavor profile.
    
    interaction_type: view, like, cook, shop, unlike
    """
    # Get recipe
    recipe = db.query(Recipe).filter(
        (Recipe.external_id == recipe_id) | 
        (Recipe.id == (int(recipe_id) if recipe_id.isdigit() else -1))
    ).first()
    
    if not recipe:
        return {"success": False, "error": "Recipe not found"}
    
    # Handle unlike (remove from favorites)
    if interaction_type == "unlike":
        favorite = db.query(FavoriteRecipe).filter(
            FavoriteRecipe.user_id == user_id,
            FavoriteRecipe.recipe_id == recipe.id
        ).first()
        
        if favorite:
            db.delete(favorite)
            db.commit()
        
        return {"success": True, "action": "unfavorited"}
    
    # Log interaction
    interaction = UserRecipeInteraction(
        user_id=user_id,
        recipe_id=recipe.id,
        interaction_type=interaction_type
    )
    db.add(interaction)
    
    # Handle like / save (add to favorites)
    if interaction_type in ("like", "save"):
        existing = db.query(FavoriteRecipe).filter(
            FavoriteRecipe.user_id == user_id,
            FavoriteRecipe.recipe_id == recipe.id
        ).first()
        
        if not existing:
            favorite = FavoriteRecipe(
                user_id=user_id,
                recipe_id=recipe.id
            )
            db.add(favorite)
    
    db.commit()
    
    # Update flavor profile
    updated_profile = update_flavor(db, user_id, recipe_id, interaction_type)
    
    return {
        "success": True,
        "interaction_type": interaction_type,
        "updated_flavor_profile": updated_profile
    }


def get_user_favorites(db: Session, user_id: int, limit: int = 50) -> List[Dict]:
    """Get user's favorite recipes."""
    favorites = db.query(FavoriteRecipe).filter(
        FavoriteRecipe.user_id == user_id
    ).order_by(desc(FavoriteRecipe.created_at)).limit(limit).all()
    
    return [
        {
            "recipe": f.recipe.to_dict() if f.recipe else None,
            "favorited_at": f.created_at
        }
        for f in favorites if f.recipe
    ]


def get_user_recent_interactions(
    db: Session,
    user_id: int,
    limit: int = 20
) -> List[Dict]:
    """Get user's recent recipe interactions."""
    interactions = db.query(UserRecipeInteraction).filter(
        UserRecipeInteraction.user_id == user_id
    ).order_by(desc(UserRecipeInteraction.created_at)).limit(limit).all()
    
    return [
        {
            "recipe_id": i.recipe.external_id if i.recipe else None,
            "recipe_name": i.recipe.name if i.recipe else None,
            "interaction_type": i.interaction_type,
            "created_at": i.created_at
        }
        for i in interactions
    ]


def get_personalized_recommendations(
    db: Session,
    user_id: int,
    limit: int = 10,
    exclude_ids: List[str] = None,
    cuisine: str = None,
    max_time: int = None,
    difficulty: str = None
) -> List[Dict]:
    """
    Get personalized recipe recommendations based on user's flavor profile.
    
    Uses Euclidean distance between user profile and recipe profiles.
    """
    # Get user flavor profile
    user_profile = db.query(UserFlavorProfile).filter(
        UserFlavorProfile.user_id == user_id
    ).first()
    
    if not user_profile or user_profile.interaction_count < 3:
        # Not enough data, return popular recipes
        query = db.query(Recipe)
        if cuisine:
            query = query.filter(Recipe.cuisine.ilike(f"%{cuisine}%"))
        if max_time:
            query = query.filter(Recipe.total_time <= max_time)
        if difficulty:
            query = query.filter(Recipe.difficulty == difficulty)
        
        recipes = query.order_by(desc(Recipe.popularity_score)).limit(limit).all()
        return [
            {
                "recipe": r.to_dict(),
                "match_score": r.popularity_score / 100,
                "recommendation_type": "popular"
            }
            for r in recipes
        ]
    
    # Get all recipes with flavor profiles
    query = db.query(Recipe).join(RecipeFlavorProfile)
    
    if cuisine:
        query = query.filter(Recipe.cuisine.ilike(f"%{cuisine}%"))
    if max_time:
        query = query.filter(Recipe.total_time <= max_time)
    if difficulty:
        query = query.filter(Recipe.difficulty == difficulty)
    
    recipes = query.all()
    
    # Exclude specified recipes
    exclude_set = set(exclude_ids or [])
    
    # Get user's recently viewed recipes to avoid repetition
    recent = db.query(UserRecipeInteraction.recipe_id).filter(
        UserRecipeInteraction.user_id == user_id
    ).order_by(desc(UserRecipeInteraction.created_at)).limit(20).all()
    recent_ids = {r[0] for r in recent}
    
    # Calculate distances
    scored_recipes = []
    for recipe in recipes:
        if recipe.external_id in exclude_set:
            continue
        if not recipe.flavor_profile:
            continue
        
        fp = recipe.flavor_profile
        
        # Euclidean distance (lower is better)
        distance = (
            (user_profile.sweet - fp.sweet) ** 2 +
            (user_profile.salty - fp.salty) ** 2 +
            (user_profile.sour - fp.sour) ** 2 +
            (user_profile.bitter - fp.bitter) ** 2 +
            (user_profile.umami - fp.umami) ** 2 +
            (user_profile.spicy - fp.spicy) ** 2 +
            (user_profile.fatty - fp.fatty) ** 2 +
            (user_profile.aromatic - fp.aromatic) ** 2
        ) ** 0.5
        
        # Convert to similarity score (0-1, higher is better)
        max_distance = 8 ** 0.5  # Maximum possible distance
        match_score = 1 - (distance / max_distance)
        
        # Penalize recently viewed
        if recipe.id in recent_ids:
            match_score *= 0.7
        
        scored_recipes.append((recipe, match_score))
    
    # Sort by match score
    scored_recipes.sort(key=lambda x: x[1], reverse=True)
    
    return [
        {
            "recipe": r.to_dict(),
            "match_score": round(score, 3),
            "flavor_profile": r.flavor_profile.to_dict() if r.flavor_profile else None,
            "recommendation_type": "personalized"
        }
        for r, score in scored_recipes[:limit]
    ]


def add_to_favorites(db: Session, user_id: int, recipe_id: str) -> Dict:
    """Add a recipe to user's favorites."""
    recipe = db.query(Recipe).filter(
        (Recipe.external_id == recipe_id) | 
        (Recipe.id == (int(recipe_id) if recipe_id.isdigit() else -1))
    ).first()
    
    if not recipe:
        return {"success": False, "error": "Recipe not found"}
    
    existing = db.query(FavoriteRecipe).filter(
        FavoriteRecipe.user_id == user_id,
        FavoriteRecipe.recipe_id == recipe.id
    ).first()
    
    if existing:
        return {"success": True, "message": "Already in favorites"}
    
    favorite = FavoriteRecipe(user_id=user_id, recipe_id=recipe.id)
    db.add(favorite)
    db.commit()
    
    return {"success": True, "message": "Added to favorites"}


def remove_from_favorites(db: Session, user_id: int, recipe_id: str) -> Dict:
    """Remove a recipe from user's favorites."""
    recipe = db.query(Recipe).filter(
        (Recipe.external_id == recipe_id) | 
        (Recipe.id == (int(recipe_id) if recipe_id.isdigit() else -1))
    ).first()
    
    if not recipe:
        return {"success": False, "error": "Recipe not found"}
    
    favorite = db.query(FavoriteRecipe).filter(
        FavoriteRecipe.user_id == user_id,
        FavoriteRecipe.recipe_id == recipe.id
    ).first()
    
    if not favorite:
        return {"success": True, "message": "Not in favorites"}
    
    db.delete(favorite)
    db.commit()
    
    return {"success": True, "message": "Removed from favorites"}


# ============================================================
# SOCIAL GRAPH (follow / unfollow)
# ============================================================

def follow_user(db: Session, follower_id: int, followee_id: int) -> Dict:
    """Create a follow edge from ``follower_id`` to ``followee_id``."""
    if follower_id == followee_id:
        return {"success": False, "error": "You cannot follow yourself"}

    followee = db.query(User).filter(User.id == followee_id).first()
    if not followee:
        return {"success": False, "error": "User to follow not found"}

    existing = db.query(UserFollow).filter(
        UserFollow.follower_id == follower_id,
        UserFollow.followee_id == followee_id,
    ).first()

    if existing:
        return {
            "success": True,
            "following": True,
            "follower_id": follower_id,
            "followee_id": followee_id,
            "message": "Already following",
        }

    db.add(UserFollow(follower_id=follower_id, followee_id=followee_id))
    db.commit()

    return {
        "success": True,
        "following": True,
        "follower_id": follower_id,
        "followee_id": followee_id,
        "message": "Now following",
    }


def unfollow_user(db: Session, follower_id: int, followee_id: int) -> Dict:
    """Remove the follow edge from ``follower_id`` to ``followee_id``."""
    edge = db.query(UserFollow).filter(
        UserFollow.follower_id == follower_id,
        UserFollow.followee_id == followee_id,
    ).first()

    if edge:
        db.delete(edge)
        db.commit()

    return {
        "success": True,
        "following": False,
        "follower_id": follower_id,
        "followee_id": followee_id,
        "message": "Unfollowed",
    }


def get_following(db: Session, user_id: int) -> List[Dict]:
    """Return the list of users that ``user_id`` follows."""
    edges = db.query(UserFollow).filter(UserFollow.follower_id == user_id).all()
    return [
        {"id": e.followee.id, "name": e.followee.name, "email": e.followee.email}
        for e in edges if e.followee
    ]


def get_followers(db: Session, user_id: int) -> List[Dict]:
    """Return the list of users that follow ``user_id``."""
    edges = db.query(UserFollow).filter(UserFollow.followee_id == user_id).all()
    return [
        {"id": e.follower.id, "name": e.follower.name, "email": e.follower.email}
        for e in edges if e.follower
    ]
