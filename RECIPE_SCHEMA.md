# Recipe Database Schema & Structure Guide

**Version:** 2.0  
**Last Updated:** 2026-01-29

This document defines the complete structure for recipes in the MyFridge database. Use this as a reference when adding new recipes manually.

---

## 📋 Complete Recipe Schema

```json
{
  "id": "string (required, unique, snake_case)",
  "source": "string (required)",
  "name": "string (required)",
  "description": "string (required, 50-200 chars)",
  "prep_time": "number (minutes, required)",
  "cook_time": "number (minutes, required)",
  "total_time": "number (minutes, required)",
  "servings": "number (required)",
  "difficulty": "string (required: easy|medium|hard)",
  "ingredients": ["array of strings (required)"],
  "instructions": ["array of strings (required)"],
  "tags": ["array of strings (optional)"],
  "cuisine": "string (optional)",
  "category": "string (required: main|side|appetizer|dessert|breakfast|snack|beverage)",
  "image_url": "string (optional, URL)",
  "popularity_score": "number (optional, 0-100)",
  "popularity_score_old": "number (optional)",
  "popularity_last_updated": "string (optional, ISO 8601 datetime)",
  "ingredients_structured": ["array of objects (required, see below)"]
}
```

---

## 🔑 Required Fields Explained

### **1. id** (string, unique, snake_case)
- **Format:** lowercase with underscores
- **Examples:** 
  - `"chicken_stir_fry"`
  - `"classic_carbonara"`
  - `"vegan_chocolate_cake"`
- **Rules:** Must be unique across all recipes

### **2. source** (string)
- Where the recipe came from
- **Examples:**
  - `"MyFridge"` (original recipes)
  - `"TheMealDB (facts), MyFridge (content)"`
  - `"Spoonacular API"`
  - `"User Submitted"`

### **3. name** (string)
- Display name of the recipe
- **Examples:** 
  - `"Classic Carbonara"`
  - `"Vegan Chocolate Cake"`
  - `"Thai Green Curry"`

### **4. description** (string, 50-200 characters)
- Brief, appetizing description
- **Good:** `"Creamy Italian pasta with crispy bacon and parmesan, ready in 20 minutes"`
- **Bad:** `"Pasta"` (too short)

### **5. Timing Fields**
- **prep_time:** Time to prepare ingredients (minutes)
- **cook_time:** Actual cooking time (minutes)
- **total_time:** prep_time + cook_time
- **Example:** Prep 15 min, Cook 30 min → Total 45 min

### **6. servings** (number)
- Number of people this recipe serves
- **Examples:** `2`, `4`, `6`, `8`

### **7. difficulty** (enum)
- **Options:** `"easy"`, `"medium"`, `"hard"`
- **Easy:** 3-5 steps, basic techniques, minimal ingredients
- **Medium:** 5-10 steps, some technique required
- **Hard:** 10+ steps, advanced techniques, precise timing

### **8. ingredients** (array of strings)
- List of ingredients with amounts
- **Format:** `"[amount] [unit] [ingredient], [preparation]"`
- **Examples:**
  ```json
  [
    "2 cups all-purpose flour",
    "1 pound chicken breast, diced",
    "3 cloves garlic, minced",
    "1/4 cup olive oil",
    "Salt and pepper to taste"
  ]
  ```

### **9. instructions** (array of strings)
- Step-by-step cooking instructions
- **Format:** One step per array item, clear and concise
- **Examples:**
  ```json
  [
    "Preheat oven to 375°F (190°C).",
    "Mix flour, sugar, and salt in a large bowl.",
    "Add eggs and milk, whisk until smooth.",
    "Pour into greased baking dish.",
    "Bake for 25-30 minutes until golden brown."
  ]
  ```

### **10. category** (enum, required)
- **Options:** 
  - `"main"` - Main dishes/entrees
  - `"side"` - Side dishes
  - `"appetizer"` - Starters, appetizers
  - `"dessert"` - Desserts, sweets
  - `"breakfast"` - Breakfast items
  - `"snack"` - Snacks, small bites
  - `"beverage"` - Drinks

### **11. ingredients_structured** (array of objects, REQUIRED)
This is the most important field for filtering and matching!

**Object Structure:**
```json
{
  "item": "string (required, the ingredient name)",
  "amount": "string (required, the quantity)",
  "original": "string (required, full original text)",
  "role": "string (required: main|secondary|optional)",
  "classification": "string (required: essential|common|optional)",
  "category": "string (required: protein|produce|dairy|carb|spice|condiment|other)"
}
```

**Example:**
```json
{
  "item": "chicken breast",
  "amount": "1 pound",
  "original": "1 pound chicken breast, diced",
  "role": "main",
  "classification": "essential",
  "category": "protein"
}
```

---

## 🎯 Ingredient Classification Rules

### **Role Classification** (main vs secondary vs optional)

#### **Main Ingredients** (role: "main", classification: "essential")
These define the dish's core identity. Removing them fundamentally changes the recipe.

**Criteria:**
- ✅ Appears in recipe title (e.g., "Chicken" in "Chicken Stir Fry")
- ✅ Listed in first 3-4 ingredients
- ✅ Substantial portion by weight (>20% of dish)
- ✅ Featured protein, main carb, or star ingredient
- ✅ SOI (Standards of Identity) requirement (e.g., tomatoes in marinara)

**Examples:**
- Pasta in "Pasta Carbonara"
- Chicken in "Chicken Curry"
- Beef in "Beef Tacos"
- Eggs in "Scrambled Eggs"
- Chocolate in "Chocolate Cake"

#### **Secondary Ingredients** (role: "secondary", classification: "common")
Important for flavor, texture, or technique, but not the star.

**Criteria:**
- ✅ Listed after main ingredients
- ✅ Provides flavor, texture, or moisture
- ✅ Aromatics (onions, garlic, ginger)
- ✅ Cooking fats (oil, butter)
- ✅ Sauces and liquids (broth, soy sauce)
- ✅ Key vegetables or supporting ingredients

**Examples:**
- Garlic and onions in most savory dishes
- Olive oil for cooking
- Soy sauce in stir-fry
- Tomatoes in pasta sauce (if not marinara)
- Bell peppers in fajitas

#### **Optional Ingredients** (role: "optional", classification: "optional")
Garnishes, seasonings, or enhancements that can be omitted.

**Criteria:**
- ✅ Marked as "optional" or "to taste" in original text
- ✅ Garnishes (fresh herbs for topping)
- ✅ Basic seasonings (salt, pepper, generic spices)
- ✅ Serving suggestions (parmesan for topping)
- ✅ Can be omitted without affecting core recipe

**Examples:**
- "Fresh parsley for garnish (optional)"
- "Salt and pepper to taste"
- "Parmesan cheese for serving"
- "Lemon wedges for serving"
- "Red pepper flakes (optional)"

---

## 📁 Ingredient Categories

| Category | Examples | When to Use |
|----------|----------|-------------|
| **protein** | Chicken, beef, pork, fish, eggs, tofu, beans | Any meat, seafood, or protein source |
| **produce** | Vegetables, fruits, herbs | Fresh produce items |
| **dairy** | Milk, cheese, butter, yogurt, cream | Dairy products |
| **carb** | Pasta, rice, bread, flour, potatoes | Starches and grains |
| **spice** | Basil, oregano, cumin, paprika | Dried herbs and spices |
| **condiment** | Soy sauce, ketchup, mustard, vinegar | Sauces and condiments |
| **other** | Sugar, salt, baking powder, vanilla | Anything that doesn't fit above |

---

## 🏷️ Tags (Optional but Recommended)

Tags help with filtering and search. Include relevant tags:

### Dietary Tags
- `"vegetarian"`, `"vegan"`, `"gluten-free"`, `"dairy-free"`, `"nut-free"`

### Meal Type Tags
- `"breakfast"`, `"lunch"`, `"dinner"`, `"snack"`, `"dessert"`

### Cuisine Tags
- `"italian"`, `"mexican"`, `"chinese"`, `"indian"`, `"thai"`, `"american"`, etc.

### Feature Tags
- `"quick"` (under 30 min), `"budget-friendly"`, `"one-pot"`, `"no-cook"`, `"meal-prep"`
- `"comfort-food"`, `"healthy"`, `"kid-friendly"`, `"party"`, `"holiday"`

### Cooking Method Tags
- `"baked"`, `"grilled"`, `"fried"`, `"steamed"`, `"slow-cooker"`, `"instant-pot"`

**Example tags array:**
```json
"tags": [
  "dinner",
  "italian",
  "vegetarian",
  "quick",
  "comfort-food",
  "budget-friendly"
]
```

---

## 📐 Recipe Template Examples

See the `recipe_templates/` folder for complete examples:
- `template_main_dish.json` - Main course template
- `template_quick_meal.json` - Quick meal (under 30 min)
- `template_dessert.json` - Dessert template
- `template_vegan.json` - Vegan recipe template

---

## ✅ Validation Checklist

Before adding a recipe to the database, verify:

- [ ] **Unique ID** - Not used by any other recipe
- [ ] **All required fields** present
- [ ] **Timing** - prep_time + cook_time = total_time
- [ ] **Difficulty** - Matches number of steps and complexity
- [ ] **Ingredients** - Each has amount and description
- [ ] **Instructions** - Clear, step-by-step, numbered
- [ ] **Structured ingredients** - Same count as `ingredients` array
- [ ] **Role classification** - At least 2-3 "main" ingredients
- [ ] **Categories** - Correct category for each ingredient
- [ ] **Tags** - At least 3-5 relevant tags

---

## 🛠️ Tools

### Validate a Recipe
```bash
python tools/validate_recipe.py path/to/recipe.json
```

### Add a Recipe to Database
```bash
python tools/add_recipe.py path/to/recipe.json
```

### Classify Ingredients Automatically
```bash
python tools/classify_ingredients.py path/to/recipe.json
```

---

## 💡 Tips for Writing Great Recipes

### Good Ingredient Formatting
✅ **Good:**
- `"2 cups all-purpose flour"`
- `"1 pound chicken breast, diced into 1-inch cubes"`
- `"3 cloves garlic, minced"`

❌ **Bad:**
- `"flour"` (no amount)
- `"2 cups flour type"` (unclear)
- `"garlic"` (no amount or preparation)

### Good Instruction Writing
✅ **Good:**
- `"Heat olive oil in a large skillet over medium-high heat."`
- `"Cook chicken for 5-7 minutes until golden brown and cooked through."`
- `"Bake at 375°F for 25-30 minutes until a toothpick comes out clean."`

❌ **Bad:**
- `"Cook the chicken"` (no details)
- `"Bake until done"` (vague)
- `"Mix everything together"` (not specific)

### Good Descriptions
✅ **Good:**
- `"Creamy Italian pasta with crispy bacon and parmesan, ready in 20 minutes"`
- `"Spicy Thai curry with tender chicken, coconut milk, and fresh vegetables"`
- `"Classic American dessert with rich chocolate and fluffy marshmallow topping"`

❌ **Bad:**
- `"A pasta dish"` (too generic)
- `"Yummy food"` (not descriptive)
- `"Recipe for dinner"` (tells nothing)

---

## 📞 Questions?

If you're unsure about classification, refer to:
- `ALGORITHM.md` in `developer-kit/ingredient-classification/`
- `validate_recipes.py` for automated checks
- Existing recipes in `data/recipes.json` for examples
