"""AI Chef service for recipe generation and chat."""
import os
import json
import re
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


SYSTEM_PROMPT = """You are an AI Chef companion for MyFridge - a smart cooking assistant for students.

YOUR ROLE:
- Help users understand and modify real recipes from our database
- Suggest ingredient substitutions when they're missing something
- Guide them through cooking with encouragement and tips
- Answer cooking questions in a friendly, patient way
- Adapt recipes to dietary needs (vegetarian, gluten-free, etc.)

YOUR APPROACH:

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

📝 CRITICAL RULES FOR STEPS:

1. **ALWAYS include exact quantities** when mentioning ingredients in steps
   - BAD: "Add oil to the pan"
   - GOOD: "Pour in 2 tablespoons (30ml) of oil into the pan"
   
2. **ALWAYS include measurements in steps**, even if listed in ingredients
   - BAD: "Add the flour"
   - GOOD: "Add 1 cup (120g) of flour"
   
3. **Be specific about amounts**:
   - BAD: "Add some salt"
   - GOOD: "Add 1/2 teaspoon (2.5ml) of salt"

📝 EXAMPLE OF DETAILED STEPS:

BAD (too vague): "Sauté the onions until soft"

GOOD (perfect detail with quantities in every step): 
"**Step 3: Cook the Onions** ⏱️ 5 minutes
1. Put your pan on the stove burner
2. Turn the knob to MEDIUM heat (the middle setting)
3. Wait 1 minute for the pan to warm up (hold your hand 6 inches above - you should feel gentle warmth)
4. Pour in 1 tablespoon (15ml) of oil - it should spread and shimmer (look shiny and wavy)
5. Take your chopped onion pieces (about 1/2 cup worth) and carefully slide them into the pan (stand back - it might sizzle!)
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
            timeout=30.0,  # 30 second timeout to prevent hanging
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


async def suggest_recipes_from_fridge(inventory_summary: dict) -> dict:
    """Suggest recipes from database based on fridge contents using AI."""
    from .recipe_service import get_recipe_service
    
    recipe_service = get_recipe_service()
    
    # Extract ingredient names from inventory
    ingredients = [item['name'] for item in inventory_summary['items']]
    
    if not ingredients:
        return {
            "response": "Your fridge is empty! Add some items and I'll suggest recipes you can make. 🥘",
            "recipes": []
        }
    
    # Get matching recipes from database
    matching_recipes = recipe_service.get_recipes_by_ingredients(ingredients, limit=5)
    
    if not matching_recipes:
        # Fallback to random recipes
        matching_recipes = recipe_service.get_random_recipes(count=3)
    
    # Build AI response about these recipes
    recipe_context = "\n\n".join([
        f"**{r['name']}** ({r['total_time']} min)\n"
        f"- {r['description']}\n"
        f"- Tags: {', '.join(r['tags'][:3])}"
        for r in matching_recipes
    ])
    
    inventory_context = build_inventory_context(inventory_summary)
    
    prompt = f"""Based on the user's fridge contents and these available recipes from our database, 
provide a friendly, encouraging message suggesting which recipes they should try.

{inventory_context}

Available recipes:
{recipe_context}

Mention:
1. Which recipes they can make right now
2. Which ingredients from their fridge match each recipe
3. Any ingredient substitutions they could make
4. Your personal recommendation for what to cook

Be enthusiastic and helpful! 🎉"""
    
    try:
        groq_client = get_groq_client()
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000,
            timeout=30.0,  # 30 second timeout
        )
        
        ai_message = response.choices[0].message.content
        
        return {
            "response": ai_message,
            "recipes": matching_recipes
        }
    except Exception as e:
        return {
            "response": f"Here are some recipes you can make with your ingredients! Check them out below. 👇",
            "recipes": matching_recipes
        }


async def modify_recipe(recipe: dict, modification_request: str, user_preferences: dict = None) -> dict:
    """Help user modify a recipe based on their needs."""
    try:
        groq_client = get_groq_client()
    except ValueError as e:
        return {
            "response": "AI Chef is not configured. Please set up your GROQ_API_KEY.",
            "modified_title": None,
            "ingredients": recipe.get('ingredients', []),
            "steps": recipe.get('instructions', []),
            "changes": {},
            "time": recipe.get('time') or recipe.get('total_time'),
            "difficulty": recipe.get('level') or recipe.get('difficulty')
        }
    
    recipe_name = recipe.get('name', 'Unknown Recipe')
    recipe_time = recipe.get('time') or recipe.get('total_time', 30)
    recipe_ingredients = recipe.get('ingredients', [])
    recipe_instructions = recipe.get('instructions', []) or recipe.get('steps', [])
    
    recipe_text = f"""
Recipe: {recipe_name}
Time: {recipe_time} minutes

Ingredients:
{chr(10).join(f'- {ing}' for ing in recipe_ingredients)}

Instructions:
{chr(10).join(f'{i+1}. {step}' for i, step in enumerate(recipe_instructions))}
"""
    
    prompt = f"""A user wants to modify this recipe:

{recipe_text}

Their request: "{modification_request}"

IMPORTANT: Return your response in the following JSON format (without markdown code blocks):
{{
  "explanation": "A friendly explanation of the modifications",
  "modified_title": "Modified Recipe Name (e.g., 'Modified Pad Thai with Chicken')",
  "ingredients": ["2 cups flour", "1 lb chicken breast", "3 tablespoons olive oil", ...],
  "steps": ["step 1", "step 2", ...],
  "ingredient_changes": [
    {{"index": 0, "type": "replaced", "original": "2 cups butter", "new": "2 cups olive oil"}},
    {{"index": 1, "type": "added", "new": "1 teaspoon salt"}},
    {{"index": 2, "type": "removed", "original": "1 cup sugar"}}
  ],
  "step_changes": [
    {{"index": 0, "type": "modified", "original": "original step", "new": "modified step"}},
    {{"index": 1, "type": "added", "new": "new step"}}
  ],
  "time": 35,
  "difficulty": "medium"
}}

CRITICAL RULES:
- ALWAYS include quantities, measurements, and portions with each ingredient (e.g., "2 cups flour" NOT just "flour")
- KEEP the original measurements unless the user specifically asks to change portions
- If replacing an ingredient, use the same measurement as the original (e.g., "2 cups butter" → "2 cups olive oil")
- ingredient_changes and step_changes should track what was modified
- type can be: "replaced", "added", "removed", "modified"
- If no changes to an item, don't include it in the changes arrays
- Be practical and safe with your modifications
- Make sure the modified recipe is still delicious!"""
    
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a helpful chef assistant. Always return valid JSON without markdown code blocks."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000,
            timeout=30.0,  # 30 second timeout
        )
        
        raw_response = response.choices[0].message.content.strip()
        
        # Clean up JSON from response
        import json
        cleaned = _clean_json_from_text(raw_response)
        
        try:
            data = json.loads(cleaned) if cleaned else {}
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return {
                "response": raw_response,
                "modified_title": f"Modified {recipe_name}",
                "ingredients": recipe_ingredients,
                "steps": recipe_instructions,
                "changes": {},
                "time": recipe_time,
                "difficulty": recipe.get('level') or recipe.get('difficulty', 'medium')
            }
        
        # Build changes dict from arrays
        changes = {
            "ingredients": {},
            "steps": {}
        }
        
        for change in data.get("ingredient_changes", []):
            idx = change.get("index")
            if idx is not None:
                changes["ingredients"][idx] = {
                    "type": change.get("type"),
                    "original": change.get("original"),
                    "new": change.get("new")
                }
        
        for change in data.get("step_changes", []):
            idx = change.get("index")
            if idx is not None:
                changes["steps"][idx] = {
                    "type": change.get("type"),
                    "original": change.get("original"),
                    "new": change.get("new")
                }
        
        return {
            "response": data.get("explanation", "Recipe modified successfully!"),
            "modified_title": data.get("modified_title", f"Modified {recipe_name}"),
            "ingredients": data.get("ingredients", recipe_ingredients),
            "steps": data.get("steps", recipe_instructions),
            "changes": changes,
            "time": data.get("time", recipe_time),
            "difficulty": data.get("difficulty", recipe.get('level') or recipe.get('difficulty', 'medium'))
        }
        
    except Exception as e:
        print(f"Error in modify_recipe: {e}")
        return {
            "response": f"Sorry, I couldn't help with that modification: {str(e)}",
            "modified_title": f"Modified {recipe_name}",
            "ingredients": recipe_ingredients,
            "steps": recipe_instructions,
            "changes": {},
            "time": recipe_time,
            "difficulty": recipe.get('level') or recipe.get('difficulty', 'medium')
        }


async def parse_voice_to_items(text: str) -> dict:
    """Parse voice input text into structured fridge items using AI."""
    import json
    import re
    
    print(f"🎤 Parsing voice input: '{text}'")
    result_text = ""  # Initialize to avoid UnboundLocalError
    
    try:
        groq_client = get_groq_client()
    except ValueError as e:
        print(f"❌ Groq client error: {e}")
        return {
            "items": [],
            "error": "AI not configured. Please add items manually."
        }
    
    # Smart voice parsing prompt with context-aware defaults
    prompt = f"""Extract food items from this text and return ONLY valid JSON. Be SMART about units, quantities, and categories.

Text: "{text}"

SMART UNIT SELECTION (DO NOT use "pieces" for everything!):
- Liquids (oil, vinegar, milk, juice, soy sauce): "bottles" or "ml" (default: 1 bottle)
- Powders/spices (salt, pepper, coriander, cumin, flour, sugar): "grams" or "teaspoons" (default: 100 grams)
- Vegetables (tomato, onion, carrot, potato): "pieces" (OK to use here)
- Leafy greens (lettuce, cabbage, kale): "heads" or "bunches"
- Meat/fish/protein (chicken, beef, pork, fish, tofu): "grams" or "pounds" (default: 500 grams)
- Dairy (cheese, butter): "blocks" or "grams" (default: 200 grams)
- Eggs: "pieces" or "dozen"
- Grains/pasta (rice, pasta, noodles): "bags" or "grams" (default: 500 grams)
- Bread: "loaves" or "pieces"

SMART CATEGORY SELECTION:
- dairy: milk, cheese, yogurt, butter, cream, eggs
- meat: chicken, beef, pork, lamb, bacon, ham, sausage
- seafood: fish, shrimp, salmon, tuna, crab, squid
- vegetable: tomato, onion, carrot, potato, lettuce, broccoli, pepper, garlic
- fruit: apple, banana, orange, lemon, lime, berries, mango
- grain: rice, pasta, bread, noodles, flour, oats
- beverage: juice, soda, coffee, tea, wine, beer
- condiment: oil, vinegar, soy sauce, ketchup, mustard, mayo, sauce, paste
- snack: chips, cookies, crackers, nuts

SMART LOCATION:
- Fresh produce, dairy, cooked food → "fridge"
- Meat, ice cream, long-term items → "freezer"  
- Dry goods, canned items, spices, oil → "pantry"

JSON format (copy exactly, adjust values smartly):
{{"items":[{{"name":"tomatoes","quantity":3,"unit":"pieces","location":"fridge","category":"vegetable","expiration_date":null,"notes":null}}]}}

IMPORTANT: 
1. Return ONLY the JSON object. No explanation, no markdown.
2. Use APPROPRIATE units (not "pieces" for oil/salt/powder!)
3. Categorize correctly (not everything is "other")
4. If quantity not mentioned, use sensible defaults based on item type"""

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
            timeout=30.0,  # 30 second timeout
        )
        
        result_text = response.choices[0].message.content.strip()
        print(f"📥 AI Response (first 300 chars): {result_text[:300]}")
        
        # Remove markdown code blocks
        result_text = re.sub(r'```json\s*', '', result_text)
        result_text = re.sub(r'```\s*', '', result_text)
        result_text = result_text.strip()
        
        # Find JSON object in the response
        json_match = re.search(r'\{[\s\S]*\}', result_text)
        if json_match:
            result_text = json_match.group(0)
        else:
            print("⚠️ No JSON object found in response")
            return {"items": [], "error": "AI didn't return valid JSON"}
        
        # Try to fix common JSON issues
        # Remove trailing commas before } or ]
        result_text = re.sub(r',(\s*[}\]])', r'\1', result_text)
        
        print(f"🔧 Cleaned JSON (first 300 chars): {result_text[:300]}")
        
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
        if result_text:
            print(f"📄 Full raw response:\n{result_text}")
        
        # Last resort: try to extract item names with regex
        try:
            print("🚑 Attempting fallback parsing...")
            if not result_text:
                return {"items": [], "error": "No response from AI"}
            
            # Look for quoted strings that might be item names
            item_matches = re.findall(r'"name"\s*:\s*"([^"]+)"', result_text)
            if item_matches:
                fallback_items = [
                    {
                        "name": name,
                        "quantity": 1,
                        "unit": "pieces",
                        "location": "fridge",
                        "category": "other",
                        "expiration_date": None,
                        "notes": None
                    }
                    for name in item_matches
                ]
                print(f"✅ Fallback found {len(fallback_items)} items")
                return {"items": fallback_items}
        except Exception as fallback_error:
            print(f"❌ Fallback also failed: {fallback_error}")
        
        return {
            "items": [],
            "error": f"AI returned invalid JSON. Try speaking more clearly."
        }
    except Exception as e:
        print(f"❌ Voice parsing error: {e}")
        return {
            "items": [],
            "error": f"Could not parse input: {str(e)}"
        }


# ==========================
# Chef Controls Assistant
# ==========================

CHEF_CONTROLS_SYSTEM_PROMPT = """You are an assistant that controls UI filters/sort/customization for an AI Chef recipe browsing page.

You MUST return ONLY valid JSON (no markdown).

Your job:
- Read the user's message and the current UI state.
- Produce a friendly assistant_message.
- Produce a list of actions to update the state.

Allowed action format:
{
  "op": "set",
  "path": "filters.expiringOnly|filters.readyOnly|filters.maxTimeMinutes|filters.maxMissingMain|filters.difficulty|filters.includeTags|filters.excludeTags|customization.diet|customization.excludeIngredients|customization.includeIngredients|customization.cuisine|customization.spiceLevel|sort.by|sort.direction",
  "value": <any>
}

CRITICAL RULES:
- Only use op='set'
- Do NOT invent new paths.
- ALWAYS PRESERVE EXISTING STATE: When adding to arrays like excludeIngredients or includeIngredients, you MUST merge with current_state values, not replace them!
- For ingredient searching:
  * Single ingredient word (e.g., "pork", "sour", "chicken") → ADD to includeIngredients (search FOR recipes WITH that ingredient)
  * Explicit exclusion (e.g., "no pork", "without onions") → ADD to excludeIngredients (exclude recipes with that ingredient)
  * COMMA-SEPARATED LISTS: "no onion, sour, beef" means "exclude onion" AND "include sour" AND "include beef" (3 separate actions!)
  * Exception: If diet filter is active (vegan/vegetarian) and user types meat/dairy, treat as exclusion
- ALL FILTERS WORK WITH AND LOGIC: If diet=vegan AND excludeIngredients=["pork"], then BOTH conditions must be satisfied (vegan AND no pork). This means even stricter filtering.
- If the user asks to 'reset', set filters/customization/sort back to empty objects ({}).

Examples of proper merging:
- Current: {}, User: "pork" → New: {"includeIngredients": ["pork"]} (search FOR pork recipes)
- Current: {}, User: "no pork" → New: {"excludeIngredients": ["pork"]} (exclude pork)
- Current: {"diet": "vegan"}, User: "pork" → New: {"diet": "vegan", "excludeIngredients": ["pork"]} (vegan context = exclusion)
- Current: {"includeIngredients": ["chicken"]}, User: "sour" → New: {"includeIngredients": ["chicken", "sour"]} (search for both)
- Current: {}, User: "no onion, sour, beef" → New: {"excludeIngredients": ["onion"], "includeIngredients": ["sour", "beef"]} (3 filters!)
"""


def _clean_json_from_text(text: str) -> str:
    """Extract the first JSON object from a model response."""
    t = text.strip()
    t = re.sub(r"```json\s*", "", t, flags=re.IGNORECASE)
    t = re.sub(r"```\s*", "", t)
    # Find first {...} block
    m = re.search(r"\{[\s\S]*\}", t)
    return m.group(0).strip() if m else ""


def _apply_set_action(state: dict, path: str, value):
    """Apply a dot-path set into a nested dict."""
    parts = path.split(".")
    cur = state
    for p in parts[:-1]:
        if p not in cur or not isinstance(cur[p], dict):
            cur[p] = {}
        cur = cur[p]
    cur[parts[-1]] = value


def _normalize_controls_state(state: Optional[dict]) -> dict:
    if not isinstance(state, dict):
        state = {}
    return {
        "filters": state.get("filters") if isinstance(state.get("filters"), dict) else {},
        "customization": state.get("customization") if isinstance(state.get("customization"), dict) else {},
        "sort": state.get("sort") if isinstance(state.get("sort"), dict) else {},
    }


def _fallback_controls_parser(message: str, current_state: dict) -> dict:
    """Non-LLM fallback: basic keyword/regex parsing into actions."""
    msg = (message or "").strip().lower()
    actions = []
    assistant_bits = []

    def set_(path, value):
        actions.append({"op": "set", "path": path, "value": value})

    # Reset
    if any(k in msg for k in ["reset", "clear filters", "clear all", "start over"]):
        set_("filters", {})
        set_("customization", {})
        set_("sort", {})
        assistant_bits.append("Reset filters, customization, and sorting.")
        return {"assistant_message": "✅ Reset everything back to default.", "actions": actions}
    
    # Generic search/filter - if it's just a word or two, treat it as a tag/name filter
    if len(msg.split()) <= 2 and not any(k in msg for k in ["show", "sort", "filter", "only", "under", "over"]):
        # Simple query like "stews", "pasta", "chicken", etc.
        assistant_bits.append(f"Searching for recipes with '{msg}'")
        # Note: This would need backend support for general search
        # For now, we'll just acknowledge it
        return {
            "assistant_message": f"🔍 Looking for recipes with '{msg}'. Try being more specific like 'Show me {msg}' or 'Sort by fastest'.",
            "actions": []
        }

    # Filters
    if "expiring" in msg:
        if any(k in msg for k in ["only", "just", "show expiring"]):
            set_("filters.expiringOnly", True)
            assistant_bits.append("Showing only expiring recipes.")
        if any(k in msg for k in ["off", "disable", "stop", "no expiring", "remove expiring"]):
            set_("filters.expiringOnly", False)
            assistant_bits.append("Turned off expiring-only filter.")

    if any(k in msg for k in ["ready only", "only ready", "ready to cook only", "green only"]):
        set_("filters.readyOnly", True)
        assistant_bits.append("Showing only recipes you can cook right now.")
    if any(k in msg for k in ["show all", "include not ready", "not ready too"]):
        # Only toggle readyOnly off if user explicitly broadens results
        if current_state.get("filters", {}).get("readyOnly") is True:
            set_("filters.readyOnly", False)
            assistant_bits.append("Including recipes that need extra items too.")

    # Time: "under 20 minutes", "<= 15 min", "max 30"
    m = re.search(r"(?:under|<=|less than|max)\s*(\d{1,3})\s*(?:m|min|minute|minutes)\b", msg)
    if m:
        set_("filters.maxTimeMinutes", int(m.group(1)))
        assistant_bits.append(f"Filtering to recipes under {m.group(1)} minutes.")

    # Missing main count: "missing at most 2", "max missing 1"
    m = re.search(r"(?:max missing|missing at most|at most)\s*(\d{1,2})", msg)
    if m:
        set_("filters.maxMissingMain", int(m.group(1)))
        assistant_bits.append(f"Allowing up to {m.group(1)} missing main ingredients.")

    # Difficulty
    diffs = []
    for d in ["easy", "medium", "hard"]:
        if re.search(rf"\b{d}\b", msg):
            diffs.append(d)
    if diffs and any(k in msg for k in ["only", "just", "filter"]):
        set_("filters.difficulty", sorted(set(diffs)))
        assistant_bits.append(f"Filtering difficulty to: {', '.join(sorted(set(diffs)))}.")

    # Customization: diet
    diet_set = False
    if "vegan" in msg:
        set_("customization.diet", "vegan")
        assistant_bits.append("Applying vegan-friendly filtering.")
        diet_set = True
    elif "vegetarian" in msg:
        set_("customization.diet", "vegetarian")
        assistant_bits.append("Applying vegetarian-friendly filtering.")
        diet_set = True
    elif any(k in msg for k in ["gluten free", "gluten-free"]):
        set_("customization.diet", "gluten_free")
        assistant_bits.append("Applying gluten-free-friendly filtering.")
        diet_set = True

    # Parse ingredients - handle both exclusions and inclusions
    excluded_items = []
    included_items = []
    
    # Step 1: Extract explicit exclusions (no/exclude/without)
    # Match patterns like "no onion", "exclude garlic", "without pork"
    exclusion_pattern = r"\b(?:no|exclude|without)\s+([a-z][a-z\s-]{0,20}?)(?=\s*[,;]|\s+(?:and|or)\s+|\s*$)"
    exclusion_matches = re.findall(exclusion_pattern, msg, re.IGNORECASE)
    if exclusion_matches:
        excluded_items = [x.strip(" ,.;") for x in exclusion_matches if x.strip()]
    
    # Step 2: Remove exclusion phrases from message to find remaining ingredients
    msg_without_exclusions = msg
    for exclusion_keyword in ["no ", "exclude ", "without "]:
        msg_without_exclusions = re.sub(rf"\b{exclusion_keyword}[a-z\s-]{{1,25}}(?=[,;]|$|\s+(?:and|or)\s+)", "", msg_without_exclusions, flags=re.IGNORECASE)
    
    # Step 3: Extract remaining comma/and-separated ingredients as inclusions
    # Split by commas, semicolons, "and", "or"
    remaining = re.split(r'[,;]|\s+(?:and|or)\s+', msg_without_exclusions)
    for item in remaining:
        item = item.strip(" ,.;")
        # Filter out common filler words and action words
        words = [w for w in item.split() if w not in ["with", "have", "contains", "includes", "show", "find", "get", "the", "some"]]
        if words and len(words) <= 3:
            ingredient = " ".join(words)
            # Don't add if it's a command word or already excluded
            if ingredient not in ["sort", "filter", "only", "reset"] and ingredient not in excluded_items:
                # If diet filter is active and it's meat/dairy, exclude instead
                if diet_set:
                    common_animal_products = ["pork", "beef", "chicken", "fish", "shellfish", "dairy", "milk", "eggs", 
                                             "shrimp", "lamb", "bacon", "sausage", "turkey"]
                    if any(prod in ingredient for prod in common_animal_products):
                        excluded_items.append(ingredient)
                        continue
                included_items.append(ingredient)
    
    # Debug logging
    print(f"🔍 Fallback Parser Debug:")
    print(f"   Message: '{msg}'")
    print(f"   Excluded items: {excluded_items}")
    print(f"   Included items: {included_items}")
    
    # Debug: Print parsed ingredients
    print(f"🔍 Parsed ingredients from '{msg}':")
    print(f"   Excluded: {excluded_items}")
    print(f"   Included: {included_items}")
    
    # Apply exclusions
    if excluded_items:
        existing = current_state.get("customization", {}).get("excludeIngredients")
        if not isinstance(existing, list):
            existing = []
        merged = list(set(existing + excluded_items))  # Remove duplicates
        set_("customization.excludeIngredients", merged)
        assistant_bits.append(f"Excluding: {', '.join(excluded_items)}.")
        print(f"   ✅ Set excludeIngredients to: {merged}")
    
    # Apply inclusions
    if included_items:
        existing = current_state.get("customization", {}).get("includeIngredients")
        if not isinstance(existing, list):
            existing = []
        merged = list(set(existing + included_items))  # Remove duplicates
        set_("customization.includeIngredients", merged)
        assistant_bits.append(f"Looking for recipes with: {', '.join(included_items)}.")
        print(f"   ✅ Set includeIngredients to: {merged}")
    
    print(f"   Final actions: {len(actions)} actions created")
    
    # Spice level / cuisine preferences
    if any(k in msg for k in ["spicy", "hot", "heat", "spice"]):
        set_("customization.spiceLevel", "spicy")
        assistant_bits.append("Filtering for spicy recipes.")
    
    # Cuisine
    cuisines = ["italian", "mexican", "chinese", "indian", "thai", "japanese", "korean", 
                "french", "spanish", "greek", "mediterranean", "american", "cajun"]
    for cuisine in cuisines:
        if cuisine in msg:
            set_("customization.cuisine", cuisine.capitalize())
            assistant_bits.append(f"Filtering for {cuisine.capitalize()} cuisine.")
            break

    # Sorting
    if "sort" in msg or "order" in msg:
        if any(k in msg for k in ["fastest", "quickest", "shortest time"]):
            set_("sort.by", "fastest")
            set_("sort.direction", "asc")
            assistant_bits.append("Sorting by fastest first.")
        elif any(k in msg for k in ["popular", "popularity", "top rated", "best"]):
            set_("sort.by", "most_popular")
            set_("sort.direction", "desc")
            assistant_bits.append("Sorting by popularity.")
        elif any(k in msg for k in ["fewest missing", "least missing", "missing"]):
            set_("sort.by", "fewest_missing")
            set_("sort.direction", "asc")
            assistant_bits.append("Sorting by fewest missing main ingredients.")
        elif any(k in msg for k in ["a-z", "alphabetical", "name"]):
            set_("sort.by", "alphabetical")
            set_("sort.direction", "asc")
            assistant_bits.append("Sorting alphabetically (A–Z).")
        elif any(k in msg for k in ["default", "ranked", "recommended"]):
            set_("sort.by", "ranked")
            assistant_bits.append("Using the default ranked order.")

    if not actions:
        return {
            "assistant_message": "Tell me what to change (e.g. “under 20 min”, “ready-only”, “sort by fastest”, “no onions”).",
            "actions": []
        }

    return {
        "assistant_message": "✅ " + " ".join(assistant_bits) if assistant_bits else "✅ Updated your filters/sort.",
        "actions": actions
    }


async def chat_for_chef_controls(message: str, state: dict, facets: Optional[dict] = None) -> dict:
    """
    Parse a user message into UI control actions for filters/sort/customization.
    Returns: { assistant_message, actions, new_state }
    """
    facets = facets or {}
    normalized = _normalize_controls_state(state)

    # Try Groq if configured; fallback otherwise.
    try:
        groq_client = get_groq_client()
    except (ValueError, Exception) as e:
        print(f"⚠️ Groq not available ({e}), using fallback parser")
        parsed = _fallback_controls_parser(message, normalized)
        new_state = _normalize_controls_state(normalized)
        for a in parsed.get("actions", []):
            if a.get("op") == "set" and isinstance(a.get("path"), str):
                _apply_set_action(new_state, a["path"], a.get("value"))
        return {
            "assistant_message": parsed.get("assistant_message", ""),
            "actions": parsed.get("actions", []),
            "new_state": new_state
        }

    allowed_paths = [
        "filters", "customization", "sort",
        "filters.expiringOnly", "filters.readyOnly", "filters.maxTimeMinutes", "filters.maxMissingMain",
        "filters.difficulty", "filters.includeTags", "filters.excludeTags",
        "customization.diet", "customization.excludeIngredients", "customization.includeIngredients",
        "customization.cuisine", "customization.spiceLevel",
        "sort.by", "sort.direction",
    ]

    prompt = {
        "message": message,
        "current_state": normalized,
        "facets": facets,
        "allowed_paths": allowed_paths,
        "examples": [
            {
                "user": "Show only ready recipes under 20 minutes. Sort by fastest.",
                "current_state": {"filters": {}, "customization": {}, "sort": {}},
                "json": {
                    "assistant_message": "Got it — ready-only, under 20 minutes, fastest first.",
                    "actions": [
                        {"op": "set", "path": "filters.readyOnly", "value": True},
                        {"op": "set", "path": "filters.maxTimeMinutes", "value": 20},
                        {"op": "set", "path": "sort.by", "value": "fastest"},
                        {"op": "set", "path": "sort.direction", "value": "asc"},
                    ],
                },
            },
            {
                "user": "pork",
                "current_state": {"filters": {}, "customization": {}, "sort": {}},
                "json": {
                    "assistant_message": "Searching for recipes with pork.",
                    "actions": [
                        {"op": "set", "path": "customization.includeIngredients", "value": ["pork"]},
                    ],
                },
            },
            {
                "user": "no dairy",
                "current_state": {"filters": {}, "customization": {"includeIngredients": ["pork"]}, "sort": {}},
                "json": {
                    "assistant_message": "Excluding dairy. Looking for pork recipes without dairy.",
                    "actions": [
                        {"op": "set", "path": "customization.excludeIngredients", "value": ["dairy"]},
                    ],
                },
            },
            {
                "user": "chicken",
                "current_state": {"filters": {}, "customization": {"diet": "vegan"}, "sort": {}},
                "json": {
                    "assistant_message": "Added chicken to excluded ingredients since you're filtering for vegan recipes.",
                    "actions": [
                        {"op": "set", "path": "customization.excludeIngredients", "value": ["chicken"]},
                    ],
                },
            },
            {
                "user": "beef",
                "current_state": {"filters": {}, "customization": {"includeIngredients": ["pork"]}, "sort": {}},
                "json": {
                    "assistant_message": "Looking for recipes with pork and beef.",
                    "actions": [
                        {"op": "set", "path": "customization.includeIngredients", "value": ["pork", "beef"]},
                    ],
                },
            },
            {
                "user": "no onion",
                "current_state": {"filters": {}, "customization": {"excludeIngredients": ["dairy"]}, "sort": {}},
                "json": {
                    "assistant_message": "Excluding onion and dairy.",
                    "actions": [
                        {"op": "set", "path": "customization.excludeIngredients", "value": ["dairy", "onion"]},
                    ],
                },
            },
            {
                "user": "no onion, sour, beef",
                "current_state": {"filters": {}, "customization": {}, "sort": {}},
                "json": {
                    "assistant_message": "Excluding onion. Looking for recipes with sour and beef.",
                    "actions": [
                        {"op": "set", "path": "customization.excludeIngredients", "value": ["onion"]},
                        {"op": "set", "path": "customization.includeIngredients", "value": ["sour", "beef"]},
                    ],
                },
            },
        ],
    }

    try:
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": CHEF_CONTROLS_SYSTEM_PROMPT},
                {"role": "user", "content": json.dumps(prompt)},
            ],
            temperature=0.2,
            max_tokens=1200,
            timeout=30.0,  # 30 second timeout
        )
        raw = response.choices[0].message.content or ""
        cleaned = _clean_json_from_text(raw)
        data = json.loads(cleaned) if cleaned else {}
    except Exception as e:
        print(f"⚠️ Groq API call failed: {e}")
        data = {}

    # Validate / fallback if model output is unusable
    if not isinstance(data, dict) or "actions" not in data:
        parsed = _fallback_controls_parser(message, normalized)
        data = parsed

    actions = data.get("actions", [])
    if not isinstance(actions, list):
        actions = []

    # Apply actions (only allowed paths + set op)
    new_state = _normalize_controls_state(normalized)
    safe_actions = []
    for a in actions:
        if not isinstance(a, dict):
            continue
        if a.get("op") != "set":
            continue
        path = a.get("path")
        if not isinstance(path, str) or path not in allowed_paths:
            continue
        safe_actions.append({"op": "set", "path": path, "value": a.get("value")})
        _apply_set_action(new_state, path, a.get("value"))

    assistant_message = data.get("assistant_message")
    if not isinstance(assistant_message, str) or not assistant_message.strip():
        assistant_message = "✅ Updated your filters/sort."

    return {
        "assistant_message": assistant_message.strip(),
        "actions": safe_actions,
        "new_state": new_state,
        }
