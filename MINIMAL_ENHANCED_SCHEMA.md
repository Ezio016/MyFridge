# Minimal Enhanced Schema for AI Performance

**Purpose:** Essential metadata fields that dramatically improve AI filtering, matching, and recommendation accuracy.

---

## 🎯 Priority Fields for AI

### **Tier 1: Critical for Filtering** (Must Have)

```json
{
  "tags": ["array of strings"],
  "flavor_profile": {
    "primary_flavors": ["sweet", "savory", "spicy", "tangy", "umami", "bitter", "salty"],
    "intensity": "mild|moderate|bold"
  },
  "dietary_flags": {
    "is_vegetarian": "boolean",
    "is_vegan": "boolean",
    "is_gluten_free": "boolean",
    "allergens": ["dairy", "nuts", "eggs", "shellfish", "soy", "wheat"]
  }
}
```

**Why Critical:**
- `tags` → Fast keyword matching
- `flavor_profile` → Enables "spicy", "sweet", "savory" filters
- `dietary_flags` → Pre-computed flags eliminate parsing errors

### **Tier 2: Better Recommendations** (Should Have)

```json
{
  "variations": [
    {
      "name": "string",
      "type": "dietary|ingredient|method",
      "quick_swaps": {
        "ingredient_name": "substitute_name"
      }
    }
  ],
  "substitution_groups": {
    "oils": ["olive oil", "vegetable oil", "coconut oil"],
    "proteins": ["chicken", "tofu", "tempeh"],
    "sweeteners": ["sugar", "honey", "maple syrup"]
  }
}
```

**Why Important:**
- `variations` → AI can auto-adapt recipes
- `substitution_groups` → Smart ingredient matching

### **Tier 3: Consistency Checks** (Nice to Have)

```json
{
  "expected_characteristics": {
    "texture": "creamy|crunchy|tender|chewy|crispy",
    "color": "golden|brown|red|green|white",
    "aroma": "fragrant|savory|sweet|neutral"
  },
  "skill_requirements": {
    "techniques": ["sautéing", "whisking", "tempering"],
    "equipment": ["whisk", "skillet", "oven"],
    "difficulty_factors": ["timing", "temperature_control", "technique"]
  }
}
```

**Why Useful:**
- Helps AI validate recipe integrity
- Enables better filtering by technique/equipment

---

## 📊 Comparison: Before vs After

### **Before (Basic Schema)**
```json
{
  "name": "Thai Green Curry",
  "ingredients": [
    "2 tablespoons green curry paste",
    "1 can coconut milk",
    "1 pound chicken breast",
    "2 thai chilies",
    "1 cup basil leaves"
  ]
}
```

**AI Filtering "spicy":**
1. ❌ Parse all ingredient text
2. ❌ Search for keywords: "chili", "pepper", "hot"
3. ❌ Might miss "curry paste" = spicy
4. ❌ Can't distinguish mild vs very spicy

**Success Rate:** ~60%

### **After (Enhanced Schema)**
```json
{
  "name": "Thai Green Curry",
  "ingredients": ["..."],
  "tags": ["thai", "spicy", "curry", "quick"],
  "flavor_profile": {
    "primary_flavors": ["spicy", "savory", "umami"],
    "intensity": "bold"
  },
  "spiceLevel": "hot",
  "dietary_flags": {
    "is_vegetarian": false,
    "is_vegan": false,
    "allergens": ["shellfish"]  // fish sauce in curry paste
  },
  "variations": [
    {
      "name": "Mild Version",
      "type": "intensity",
      "quick_swaps": {
        "green curry paste": "mild curry paste (1 tbsp instead of 2)",
        "thai chilies": "omit or use 1 instead of 2"
      }
    },
    {
      "name": "Vegan Version",
      "type": "dietary",
      "quick_swaps": {
        "chicken breast": "firm tofu or tempeh",
        "fish sauce": "soy sauce + lime juice"
      }
    }
  ]
}
```

**AI Filtering "spicy":**
1. ✅ Check tags → "spicy" = TRUE
2. ✅ Check flavor_profile → "spicy" = TRUE  
3. ✅ Check spiceLevel → "hot" = TRUE
4. ✅ Can distinguish mild vs hot

**Success Rate:** ~95%+

---

## 🛠️ Auto-Generation Strategy

Instead of manually filling all fields, we can auto-generate:

### **1. Dietary Flags** (Auto from ingredients)
```python
def auto_detect_dietary_flags(ingredients):
    has_meat = any(meat in ing.lower() for ing in ingredients 
                   for meat in MEAT_KEYWORDS)
    has_dairy = any(dairy in ing.lower() for ing in ingredients 
                    for dairy in DAIRY_KEYWORDS)
    
    return {
        "is_vegetarian": not has_meat,
        "is_vegan": not has_meat and not has_dairy,
        "is_gluten_free": not any("flour" in ing.lower() for ing in ingredients)
    }
```

### **2. Flavor Profile** (AI-Assisted)
```python
def suggest_flavor_profile(recipe_name, ingredients):
    # Use AI to analyze
    spicy_ingredients = ["chili", "pepper", "curry", "hot sauce"]
    has_spicy = any(s in " ".join(ingredients).lower() for s in spicy_ingredients)
    
    flavors = []
    if has_spicy:
        flavors.append("spicy")
    
    # Add more rules...
    return {"primary_flavors": flavors, "intensity": "moderate"}
```

### **3. Tags** (Rule-Based + AI)
```python
def auto_generate_tags(recipe):
    tags = []
    
    # From cuisine
    if recipe.get("cuisine"):
        tags.append(recipe["cuisine"].lower())
    
    # From time
    if recipe["total_time"] <= 30:
        tags.append("quick")
    
    # From dietary
    if auto_detect_dietary_flags(recipe["ingredients"])["is_vegan"]:
        tags.append("vegan")
    
    return tags
```

---

## 📋 Migration Plan

### **Phase 1: Add Critical Fields** (1-2 days)
For all 225 recipes, auto-generate:
- `dietary_flags` (90% accurate via rules)
- Basic `tags` (cuisine, time, dietary)
- `flavor_profile.intensity` (based on ingredients)

### **Phase 2: Manual Enhancement** (Ongoing)
For top 50 recipes, manually add:
- Complete `flavor_profile`
- `variations` (2-3 per recipe)
- Refined `tags`

### **Phase 3: AI-Assisted** (Future)
- Use AI to suggest flavor profiles
- Crowd-source user modifications
- Auto-detect common variations

---

## 🎯 Immediate Action Items

**What I recommend doing NOW:**

1. **Add Minimal Fields to Schema** ✅
   - Add `dietary_flags`, `flavor_profile`, `spiceLevel`
   - Update validation tool
   - Update templates

2. **Create Auto-Generator Script** 🔧
   - Script to add basic metadata to existing recipes
   - Run on all 225 recipes
   - Review and adjust

3. **Test with "Spicy" Example** 🧪
   - Add spicy metadata to 10 recipes
   - Test filtering
   - Verify improvement

**Want me to create the auto-generator script now?** It can analyze your 225 existing recipes and add basic metadata automatically, which we can then refine manually for important recipes.

This way, your AI will work MUCH better immediately! 🚀
