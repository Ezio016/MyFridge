# Quick Start: Adding New Recipes

This guide shows you how to add new recipes to MyFridge without calling external APIs.

---

## 🚀 Quick Method (Recommended)

### Step 1: Copy a Template
Choose the template that best matches your recipe:

```bash
cd recipe_templates/

# For main dishes (dinner, lunch)
cp template_main_dish.json ../my_new_recipe.json

# For quick meals (under 30 min)
cp template_quick_meal.json ../my_new_recipe.json

# For desserts
cp template_dessert.json ../my_new_recipe.json

# Or start from scratch
cp BLANK_TEMPLATE.json ../my_new_recipe.json
```

### Step 2: Edit the Recipe
Open `my_new_recipe.json` in your text editor and fill in all fields:

```json
{
  "id": "my_awesome_pasta",           // ← Unique ID, lowercase with underscores
  "source": "MyFridge",                // ← Always "MyFridge" for manual recipes
  "name": "My Awesome Pasta",          // ← Display name
  "description": "Creamy garlic pasta with spinach, ready in 20 minutes",
  
  "prep_time": 10,                     // ← Minutes to prep
  "cook_time": 10,                     // ← Minutes to cook
  "total_time": 20,                    // ← prep + cook
  "servings": 4,                       // ← Number of servings
  "difficulty": "easy",                // ← easy, medium, or hard
  
  "ingredients": [
    "1 pound pasta",
    "2 cups fresh spinach",
    "3 cloves garlic, minced",
    "1/2 cup cream",
    "1/4 cup parmesan cheese",
    "2 tablespoons olive oil",
    "Salt and pepper to taste"
  ],
  
  "instructions": [
    "Cook pasta according to package directions.",
    "In a large pan, heat olive oil over medium heat.",
    "Add garlic and cook for 1 minute until fragrant.",
    "Add spinach and cook until wilted, about 2 minutes.",
    "Pour in cream and bring to a simmer.",
    "Drain pasta and add to sauce, toss to coat.",
    "Sprinkle with parmesan, season with salt and pepper, and serve."
  ],
  
  "tags": ["dinner", "italian", "quick", "vegetarian", "creamy"],
  "cuisine": "Italian",
  "category": "main",
  "image_url": "",
  
  "ingredients_structured": []         // ← Leave empty, will auto-fill!
}
```

### Step 3: Validate & Add to Database

Run the tool to automatically classify ingredients and add to database:

```bash
python tools/add_recipe.py my_new_recipe.json
```

**That's it!** Your recipe is now in the database with proper ingredient classification.

---

## 📋 What the Tool Does Automatically

✅ **Validates** all required fields  
✅ **Checks** for duplicate IDs  
✅ **Auto-classifies** ingredients (main/secondary/optional)  
✅ **Adds** to `backend/data/recipes.json`  
✅ **Preserves** existing recipes  

---

## 🔧 Advanced Options

### Validate Without Adding
Check if your recipe is valid before adding:

```bash
python tools/add_recipe.py my_new_recipe.json --validate-only
```

### Manual Ingredient Classification
If you want to manually classify ingredients instead of auto-classification:

```bash
python tools/add_recipe.py my_new_recipe.json --no-auto-classify
```

**Note:** You must have `ingredients_structured` filled in for this option.

---

## 📖 Field Reference

### Required Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `id` | string | Unique identifier, snake_case | `"chicken_stir_fry"` |
| `source` | string | Recipe source | `"MyFridge"` |
| `name` | string | Display name | `"Chicken Stir Fry"` |
| `description` | string | Brief description (50-200 chars) | `"Quick Asian-style chicken with vegetables"` |
| `prep_time` | number | Prep time in minutes | `15` |
| `cook_time` | number | Cook time in minutes | `10` |
| `total_time` | number | Total time (prep + cook) | `25` |
| `servings` | number | Number of servings | `4` |
| `difficulty` | string | `easy`, `medium`, or `hard` | `"easy"` |
| `ingredients` | array | List of ingredient strings | `["2 cups flour", "1 cup milk"]` |
| `instructions` | array | Step-by-step instructions | `["Step 1...", "Step 2..."]` |
| `category` | string | `main`, `side`, `dessert`, etc. | `"main"` |

### Optional but Recommended

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `tags` | array | Search/filter tags | `["quick", "healthy", "italian"]` |
| `cuisine` | string | Cuisine type | `"Italian"`, `"Mexican"`, `"Thai"` |
| `image_url` | string | Recipe image URL | `"https://..."` |

### Auto-Generated

| Field | Description |
|-------|-------------|
| `ingredients_structured` | Auto-classified ingredient objects |
| `popularity_score` | Initial score (50.0) |
| `popularity_last_updated` | Timestamp |

---

## 🎯 Ingredient Classification Guide

When the tool auto-classifies ingredients, it uses these rules:

### Main Ingredients (role: "main")
- Featured in recipe title
- Listed first (top 3-4 ingredients)
- Major component by weight/volume
- Defines the dish

**Examples:** Chicken in "Chicken Curry", Pasta in "Pasta Carbonara"

### Secondary Ingredients (role: "secondary")
- Supporting flavors and textures
- Aromatics (garlic, onions, ginger)
- Cooking fats (oil, butter)
- Sauces and liquids

**Examples:** Garlic, olive oil, soy sauce, vegetables

### Optional Ingredients (role: "optional")
- Marked "optional" in ingredient text
- Garnishes
- "To taste" seasonings
- Serving suggestions

**Examples:** "Salt and pepper to taste", "Fresh parsley (optional)"

---

## ✅ Quality Checklist

Before adding a recipe, verify:

- [ ] Unique ID (check database first!)
- [ ] Clear, descriptive name
- [ ] Helpful description (not too short)
- [ ] Realistic timing (prep + cook = total)
- [ ] Ingredients have amounts (not just names)
- [ ] Instructions are step-by-step
- [ ] Correct difficulty level
- [ ] At least 2-3 relevant tags
- [ ] Correct category

---

## 📁 File Structure

```
MyFridge/
├── RECIPE_SCHEMA.md              ← Full schema documentation
├── QUICK_START_ADD_RECIPE.md     ← This file
├── recipe_templates/
│   ├── BLANK_TEMPLATE.json       ← Empty template
│   ├── template_main_dish.json   ← Main dish example
│   ├── template_quick_meal.json  ← Quick meal example
│   └── template_dessert.json     ← Dessert example
├── tools/
│   └── add_recipe.py             ← Recipe validator/adder
└── backend/
    └── data/
        └── recipes.json          ← Database (225 recipes)
```

---

## 💡 Tips

### Good Ingredient Formatting
✅ `"2 cups all-purpose flour"`  
✅ `"1 pound chicken breast, diced"`  
✅ `"3 cloves garlic, minced"`  

❌ `"flour"` (no amount)  
❌ `"some chicken"` (vague)  

### Good Instructions
✅ `"Heat oil in a large skillet over medium-high heat."`  
✅ `"Cook chicken for 5-7 minutes until golden brown."`  

❌ `"Cook the chicken"` (not specific)  
❌ `"Heat until done"` (vague)  

### Good Descriptions
✅ `"Creamy Italian pasta with bacon and parmesan, ready in 20 minutes"`  
✅ `"Spicy Thai curry with coconut milk and fresh vegetables"`  

❌ `"A pasta dish"` (too generic)  
❌ `"Food"` (tells nothing)  

---

## 🆘 Troubleshooting

### "Recipe ID already exists"
**Solution:** Choose a different ID. Check `backend/data/recipes.json` for existing IDs.

### "Validation failed: missing required field"
**Solution:** Make sure all required fields from the schema are present.

### "ingredients_structured length mismatch"
**Solution:** Either leave `ingredients_structured` empty (auto-classify) or ensure it has the same number of items as `ingredients`.

### Tool not found
**Solution:** Make sure you're in the MyFridge root directory and run:
```bash
python tools/add_recipe.py your_recipe.json
```

---

## 📞 Need Help?

- Check `RECIPE_SCHEMA.md` for complete field documentation
- Look at existing recipes in `backend/data/recipes.json` for examples
- Use templates in `recipe_templates/` as starting points
- Run validator: `python tools/add_recipe.py recipe.json --validate-only`

---

**Happy Recipe Adding! 🍳**
