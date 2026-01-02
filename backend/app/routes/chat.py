"""Chat API routes for AI Chef."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas import ChatMessage, ChatResponse
from ..services import inventory_service
from ..services.ai_chef import chat_with_chef, generate_meal_plan, suggest_quick_recipe

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
    result = await suggest_quick_recipe(inventory_summary, meal_type)
    
    return ChatResponse(
        response=result["response"],
        recipes=result.get("recipes")
    )

