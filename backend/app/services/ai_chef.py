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

🎯 YOUR TEACHING STYLE:
You explain cooking like teaching a 5-year-old who has NEVER cooked before. Every single step must be:
- Extremely detailed and explicit
- Written in simple, friendly language
- Include exactly what to look for, feel, hear, and smell
- Never assume they know anything about cooking

📋 RECIPE FORMAT (follow this exactly):

## 🍳 [RECIPE NAME]

### ⏰ Time & Difficulty
- **Prep Time:** X minutes
- **Cook Time:** X minutes  
- **Difficulty:** Easy/Medium/Hard
- **Servings:** X

### 🧺 Ingredients (What You Need)
List each ingredient with:
- Exact amount
- ✅ if it's from their fridge
- What it looks like if they might not know

### 🍴 Kitchen Tools (Gather These First!)
List every pot, pan, spoon, etc. they'll need

### 👨‍🍳 Step-by-Step Instructions

**Step 1: [Action Name]** ⏱️ X minutes
1. First, do this exact thing...
2. It should look like THIS... (describe what they'll see)
3. You'll know it's ready when... (describe the sign)
💡 **Tip:** Helpful hint here
⚠️ **Be Careful:** Safety warning if needed

**Step 2: [Action Name]** ⏱️ X minutes
(continue same detailed format)

### ✅ How to Know It's Done
- Describe exactly what the finished dish looks like
- What it should smell like
- What texture to expect

### 🍽️ Serving Suggestion
How to plate it nicely

---

📝 EXAMPLE OF DETAILED STEPS:

BAD (too vague): "Sauté the onions until soft"

GOOD (perfect detail): 
"**Step 3: Cook the Onions** ⏱️ 5 minutes
1. Put your pan on the stove burner
2. Turn the knob to MEDIUM heat (the middle setting)
3. Wait 1 minute for the pan to warm up (hold your hand 6 inches above - you should feel gentle warmth)
4. Add 1 tablespoon of oil - it should spread and shimmer (look shiny and wavy)
5. Carefully slide the onion pieces into the pan (stand back - it might sizzle!)
6. You'll hear a nice 'sssssss' sound - that's good!
7. Use your wooden spoon to push the onions around every 30 seconds
8. Watch the onions change: White → Slightly see-through → Soft and floppy
9. They're done when they look translucent (you can almost see through them) and smell sweet
💡 **Tip:** If they start turning brown too fast, turn the heat DOWN
⚠️ **Be Careful:** The pan is hot! Always hold the handle with an oven mitt"

---

OTHER GUIDELINES:
1. Always prioritize ingredients that are expiring soon
2. Suggest simple, student-friendly recipes (quick, affordable, minimal equipment)
3. Be encouraging and make cooking feel FUN and accessible
4. Use emojis to make it friendly and easy to scan
5. If asked for meal plans, provide breakfast, lunch, and dinner options
6. Consider the storage location (frozen items need thawing time)
7. Include cleanup tips at the end

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
1. 🌅 **Breakfast** - Quick and energizing
2. ☀️ **Lunch** - Satisfying mid-day meal  
3. 🌙 **Dinner** - Comfortable evening meal

For each meal, provide the FULL detailed recipe format with:
- Recipe name with emoji
- All ingredients needed (mark ✅ for items from fridge)
- Kitchen tools needed
- SUPER DETAILED step-by-step instructions (like teaching a 5-year-old!)
- Time for each step
- Tips and safety warnings
- How to know it's done

Prioritize using items that are expiring soon! Make it fun and encouraging! 🎉"""
    
    return await chat_with_chef(prompt, inventory_summary)


async def suggest_quick_recipe(inventory_summary: dict, meal_type: str = "any") -> dict:
    """Suggest a quick recipe for a specific meal type."""
    prompt = f"""Suggest one quick, easy {meal_type} recipe I can make right now with what's in my fridge.

Please give me the FULL detailed recipe with:
- Recipe name with emoji
- All ingredients (mark ✅ for items from fridge)  
- Kitchen tools I'll need
- SUPER DETAILED step-by-step instructions (explain like I'm 5 years old and never cooked before!)
- Exact times, temperatures, and what to look/smell/listen for
- Tips and safety warnings
- How to know when it's perfectly done

Make it fun and encouraging! I can do this! 💪"""
    
    return await chat_with_chef(prompt, inventory_summary)


async def parse_voice_to_items(text: str) -> dict:
    """Parse voice input text into structured fridge items using AI."""
    print(f"🎤 Parsing voice input: '{text}'")
    
    try:
        groq_client = get_groq_client()
    except ValueError as e:
        print(f"❌ Groq client error: {e}")
        return {
            "items": [],
            "error": "AI not configured. Please add items manually."
        }
    
    # Simplified, more direct prompt
    prompt = f"""You are a food item parser. Extract food items from this text and return ONLY valid JSON.

Text: "{text}"

Return this exact JSON format:
{{
  "items": [
    {{
      "name": "item name",
      "quantity": 1,
      "unit": "pieces",
      "location": "fridge",
      "category": "other",
      "expiration_date": null,
      "notes": null
    }}
  ]
}}

Rules:
- Extract ALL food items mentioned
- Use simple category: dairy, meat, seafood, vegetable, fruit, grain, beverage, condiment, snack, leftover, other
- Default quantity to 1 if not mentioned
- Default unit to "pieces"
- Default location to "fridge"
- Return ONLY JSON, no explanation"""

    try:
        print("🤖 Sending to Groq AI...")
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a JSON parser. Always return valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=800,
        )
        
        result_text = response.choices[0].message.content.strip()
        print(f"📥 AI Response: {result_text[:200]}...")
        
        # Try to extract JSON if there's extra text
        import json
        import re
        
        # Remove markdown code blocks if present
        result_text = re.sub(r'```json\s*', '', result_text)
        result_text = re.sub(r'```\s*', '', result_text)
        
        # Find JSON in the response
        json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
        if json_match:
            result_text = json_match.group(0)
        
        result = json.loads(result_text)
        print(f"✅ Parsed {len(result.get('items', []))} items")
        
        # Validate structure
        if "items" not in result or not isinstance(result["items"], list):
            print("⚠️ Invalid structure, no items array found")
            result = {"items": []}
        
        # Log items found
        for item in result.get("items", []):
            print(f"  - {item.get('name')}: {item.get('quantity')} {item.get('unit')}")
        
        return result
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON parse error: {e}")
        print(f"Raw response: {result_text}")
        return {
            "items": [],
            "error": f"Invalid JSON from AI: {str(e)}"
        }
    except Exception as e:
        print(f"❌ Voice parsing error: {e}")
        return {
            "items": [],
            "error": f"Could not parse input: {str(e)}"
        }
