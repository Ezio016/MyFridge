"""User profile and recommendations API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from ..database import get_db
from ..models import User
from ..schemas import (
    UserFlavorProfileResponse, RecipeInteractionRequest,
    RecipeInteractionResponse, RecommendationRequest, RecommendationResponse,
    FlavorVector, RecipeResponse
)
from ..services import user_service
from .auth import get_current_user, get_current_user_required

router = APIRouter(prefix="/api/user", tags=["user"])


@router.get("/profile")
async def get_profile(
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """Get current user's complete profile."""
    profile = user_service.get_user_profile(db, current_user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@router.get("/flavor-profile")
async def get_flavor_profile(
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """Get current user's flavor profile."""
    profile = user_service.get_user_flavor_profile(db, current_user.id)
    if not profile:
        return {
            "sweet": 0, "salty": 0, "sour": 0, "bitter": 0,
            "umami": 0, "spicy": 0, "fatty": 0, "aromatic": 0,
            "interaction_count": 0
        }
    return profile


@router.post("/interact", response_model=RecipeInteractionResponse)
async def log_interaction(
    interaction: RecipeInteractionRequest,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """Log a recipe interaction and update flavor profile."""
    result = user_service.log_recipe_interaction(
        db,
        current_user.id,
        interaction.recipe_id,
        interaction.interaction_type.value
    )
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Failed"))
    
    return RecipeInteractionResponse(
        success=True,
        interaction_type=interaction.interaction_type.value,
        updated_flavor_profile=FlavorVector(**result.get("updated_flavor_profile", {})) if result.get("updated_flavor_profile") else None
    )


@router.get("/favorites")
async def get_favorites(
    limit: int = Query(default=50, ge=1, le=100),
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """Get user's favorite recipes."""
    favorites = user_service.get_user_favorites(db, current_user.id, limit)
    return {"favorites": favorites, "count": len(favorites)}


@router.post("/favorites/{recipe_id}")
async def add_favorite(
    recipe_id: str,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """Add a recipe to favorites."""
    result = user_service.add_to_favorites(db, current_user.id, recipe_id)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Failed"))
    return result


@router.delete("/favorites/{recipe_id}")
async def remove_favorite(
    recipe_id: str,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """Remove a recipe from favorites."""
    result = user_service.remove_from_favorites(db, current_user.id, recipe_id)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Failed"))
    return result


@router.get("/history")
async def get_history(
    limit: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """Get user's recent recipe interactions."""
    history = user_service.get_user_recent_interactions(db, current_user.id, limit)
    return {"history": history, "count": len(history)}


@router.get("/recommendations")
async def get_recommendations(
    limit: int = Query(default=10, ge=1, le=50),
    cuisine: Optional[str] = None,
    max_time: Optional[int] = None,
    difficulty: Optional[str] = None,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """Get personalized recipe recommendations based on flavor profile."""
    recommendations = user_service.get_personalized_recommendations(
        db,
        current_user.id,
        limit=limit,
        cuisine=cuisine,
        max_time=max_time,
        difficulty=difficulty
    )
    
    # Get user's current flavor profile
    flavor_profile = user_service.get_user_flavor_profile(db, current_user.id)
    
    return {
        "recommendations": recommendations,
        "count": len(recommendations),
        "user_flavor_profile": flavor_profile
    }


@router.post("/recommendations")
async def get_recommendations_post(
    request: RecommendationRequest,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """Get personalized recommendations (POST version with more options)."""
    recommendations = user_service.get_personalized_recommendations(
        db,
        current_user.id,
        limit=request.limit,
        exclude_ids=request.exclude_ids,
        cuisine=request.cuisine,
        max_time=request.max_time,
        difficulty=request.difficulty
    )
    
    flavor_profile = user_service.get_user_flavor_profile(db, current_user.id)
    
    return RecommendationResponse(
        recipes=[RecipeResponse(**r["recipe"]) for r in recommendations],
        user_flavor_profile=FlavorVector(**flavor_profile) if flavor_profile else None,
        match_scores=[r["match_score"] for r in recommendations]
    )
