"""Chat API routes for AI Chef."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas import ChatMessage, ChatResponse, ChefControlsRequest, ChefControlsResponse, ChefControlsState, ChefControlAction, RecipeCustomizationRequest, RecipeCustomizationResponse
from ..services import inventory_service
from ..services.ai_chef import chat_with_chef, generate_meal_plan, suggest_recipes_from_fridge, chat_for_chef_controls, modify_recipe

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/", response_model=ChatResponse)
async def chat(message: ChatMessage, db: Session = Depends(get_db)):
    """Send a message to the AI Chef."""
    # Get current inventory for context
    inventory_summary = inventory_service.get_inventory_summary(db)
    
    # Chat with AI
    result = await chat_with_chef(message.message, inventory_summary)
    
    return ChatResponse(
        response=result["response"],
        recipes=result.get("recipes")
    )


@router.get("/meal-plan", response_model=ChatResponse)
async def get_meal_plan(db: Session = Depends(get_db)):
    """Generate a meal plan for today."""
    inventory_summary = inventory_service.get_inventory_summary(db)
    result = await generate_meal_plan(inventory_summary)
    
    return ChatResponse(
        response=result["response"],
        recipes=result.get("recipes")
    )


@router.get("/quick-recipe", response_model=ChatResponse)
async def get_quick_recipe(
    meal_type: str = "any",
    db: Session = Depends(get_db)
):
    """Get a quick recipe suggestion."""
    inventory_summary = inventory_service.get_inventory_summary(db)
    result = await suggest_recipes_from_fridge(inventory_summary)
    
    return ChatResponse(
        response=result["response"],
        recipes=result.get("recipes")
    )


@router.post("/controls", response_model=ChefControlsResponse)
async def chef_controls(req: ChefControlsRequest):
    """
    Chat endpoint dedicated to managing Chef page UI controls:
    filtering, customization, and sorting (no recipe ranking changes).
    """
    result = await chat_for_chef_controls(
        message=req.message,
        state=req.state.model_dump() if hasattr(req.state, "model_dump") else dict(req.state),
        facets=req.facets,
    )

    new_state = result.get("new_state") or {"filters": {}, "customization": {}, "sort": {}}
    actions = result.get("actions") or []

    # Convert to schema objects (ensures response validation)
    return ChefControlsResponse(
        assistant_message=result.get("assistant_message", ""),
        actions=[ChefControlAction(**a) for a in actions if isinstance(a, dict)],
        new_state=ChefControlsState(**new_state),
    )


@router.post("/customize-recipe", response_model=RecipeCustomizationResponse)
async def customize_recipe(req: RecipeCustomizationRequest):
    """
    Customize a recipe based on user's modification request.
    Returns the modified recipe with tracked changes.
    """
    result = await modify_recipe(
        recipe=req.recipe,
        modification_request=req.modification_request
    )
    
    return RecipeCustomizationResponse(
        ai_response=result.get("response", ""),
        modified_title=result.get("modified_title"),
        ingredients=result.get("ingredients", req.recipe.get("ingredients", [])),
        steps=result.get("steps", req.recipe.get("instructions", [])),
        changes=result.get("changes", {}),
        time=result.get("time", req.recipe.get("time", 0)),
        difficulty=result.get("difficulty", req.recipe.get("difficulty", "medium"))
    )

