"""AI Chef service for recipe generation and chat."""
import os
from groq import Groq
from typing import Optional

# Initialize Groq client
client = None

def get_groq_client():
    """Get or create Groq client (free tier!)."""
    global client
    if client is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable is not set")
        client = Groq(api_key=api_key)
    return client


SYSTEM_PROMPT = """You are an AI Chef assistant for a smart fridge app called MyFridge. 
Your job is to help students cook delicious, practical meals using ingredients they have available.

Guidelines:
1. Always prioritize ingredients that are expiring soon
2. Suggest simple, student-friendly recipes (quick, affordable, minimal equipment)
3. Be encouraging and make cooking feel accessible
4. If asked for meal plans, provide breakfast, lunch, and dinner options
5. Consider the storage location (frozen items need thawing time)
6. Be concise but helpful

When suggesting recipes, format them clearly with:
- Recipe name
- Ingredients needed (mark which ones are from their fridge)
- Simple step-by-step instructions
- Approximate time to prepare

If the fridge is empty or missing key ingredients, suggest simple grocery additions."""


def build_inventory_context(inventory_summary: dict) -> str:
    """Build a context string from inventory for the AI."""
    if not inventory_summary["items"]:
        return "The fridge is currently empty."
    
    context_parts = ["Current fridge inventory:"]
    
    # Add expiring soon items first
    if inventory_summary["expiring_soon"]:
        context_parts.append("\n⚠️ EXPIRING SOON (use these first!):")
        for item in inventory_summary["expiring_soon"]:
            days = item["days_until_expiry"]
            context_parts.append(f"  - {item['name']}: {item['quantity']} (expires in {days} days)")
    
    # Add items by location
    for location, items in inventory_summary["by_location"].items():
        if items:
            context_parts.append(f"\n📍 In {location.upper()}:")
            for item in items:
                if item["expiry_status"] != "expiring_soon":
                    context_parts.append(f"  - {item['name']}: {item['quantity']}")
    
    return "\n".join(context_parts)


async def chat_with_chef(
    message: str, 
    inventory_summary: dict,
    conversation_history: Optional[list] = None
) -> dict:
    """Send a message to the AI chef and get a response."""
    try:
        groq_client = get_groq_client()
    except ValueError as e:
        # Return a helpful message if API key is not set
        return {
            "response": "🔧 AI Chef is not configured yet. Please set up your GROQ_API_KEY to enable smart recipe suggestions!\n\n📝 Get your FREE API key at: https://console.groq.com/keys\n\nIn the meantime, here's a tip: Check your expiring items first and try searching for simple recipes online using those ingredients.",
            "recipes": None
        }
    
    # Build context from inventory
    inventory_context = build_inventory_context(inventory_summary)
    
    # Build messages
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "system", "content": f"Current inventory state:\n{inventory_context}"},
    ]
    
    # Add conversation history if provided
    if conversation_history:
        messages.extend(conversation_history[-10:])  # Keep last 10 messages for context
    
    # Add current user message
    messages.append({"role": "user", "content": message})
    
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",  # Free, fast, and good quality!
            messages=messages,
            temperature=0.7,
            max_tokens=8000,  # Increased for 50 recipes
        )
        
        assistant_message = response.choices[0].message.content
        
        return {
            "response": assistant_message,
            "recipes": None  # Could parse structured recipes here in the future
        }
        
    except Exception as e:
        return {
            "response": f"Sorry, I encountered an error: {str(e)}. Please try again!",
            "recipes": None
        }


async def generate_meal_plan(inventory_summary: dict) -> dict:
    """Generate a meal plan (breakfast, lunch, dinner) from available ingredients."""
    prompt = """Based on the ingredients available, create a simple meal plan for today with:
1. **Breakfast** - Quick and energizing
2. **Lunch** - Satisfying mid-day meal  
3. **Dinner** - Comfortable evening meal

For each meal, provide:
- Recipe name
- Key ingredients from the fridge
- Brief instructions (3-5 steps max)
- Time to prepare

Prioritize using items that are expiring soon!"""
    
    return await chat_with_chef(prompt, inventory_summary)


async def suggest_quick_recipe(inventory_summary: dict, meal_type: str = "any") -> dict:
    """Suggest a quick recipe for a specific meal type."""
    prompt = f"Suggest one quick, easy {meal_type} recipe I can make right now with what's in my fridge. Keep it simple and student-friendly!"
    
    return await chat_with_chef(prompt, inventory_summary)
