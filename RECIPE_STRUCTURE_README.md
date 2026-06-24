# Recipe Database Structure System

**Complete Guide to Adding and Managing Recipes in MyFridge**

---

## 📚 Overview

This system allows you to add new recipes to MyFridge without calling external APIs. Everything is structured, validated, and automatically classified.

### What's Included

1. **Complete Schema Documentation** - Every field explained
2. **Recipe Templates** - Pre-filled examples for different recipe types
3. **Validation Tool** - Automatically checks recipes for errors
4. **Auto-Classification** - Ingredients are automatically categorized
5. **Quick Start Guide** - Get started in 5 minutes

---

## 🚀 Quick Start

### 1. Copy a Template
```bash
cd recipe_templates/
cp template_main_dish.json ../my_new_recipe.json
```

### 2. Edit the Recipe
Fill in all fields in `my_new_recipe.json`:
- Recipe name and description
- Timing (prep, cook, total)
- Ingredients with amounts
- Step-by-step instructions
- Tags and category

### 3. Add to Database
```bash
python tools/add_recipe.py my_new_recipe.json
```

**Done!** Your recipe is now in the database with proper structure.

---

## 📁 File Organization

```
MyFridge/
├── 📘 RECIPE_SCHEMA.md                    Complete field documentation
├── 🚀 QUICK_START_ADD_RECIPE.md           5-minute getting started guide
├── 📖 RECIPE_STRUCTURE_README.md          This file
├── 📊 RECIPE_DATABASE_VALIDATION_REPORT.md Current database status
│
├── recipe_templates/                      Recipe templates
│   ├── BLANK_TEMPLATE.json                Empty template (fill everything)
│   ├── template_main_dish.json            Main course example
│   ├── template_quick_meal.json           Quick meal (<30 min) example
│   └── template_dessert.json              Dessert example
│
├── tools/                                 Helper tools
│   └── add_recipe.py                      Validate & add recipes
│
└── backend/
    ├── data/
    │   └── recipes.json                   Main database (225 recipes)
    └── scraper/
        └── classify_ingredients.py        Classification algorithm
```

---

## 📋 Recipe Structure

Every recipe has this structure:

### Core Fields (Required)
```json
{
  "id": "unique_recipe_id",
  "source": "MyFridge",
  "name": "Recipe Name",
  "description": "Brief, appetizing description",
  "prep_time": 15,
  "cook_time": 30,
  "total_time": 45,
  "servings": 4,
  "difficulty": "easy|medium|hard",
  "category": "main|side|dessert|breakfast|snack|appetizer|beverage"
}
```

### Ingredients & Instructions
```json
{
  "ingredients": [
    "2 cups flour",
    "1 cup milk",
    "..."
  ],
  "instructions": [
    "Step 1: Do this...",
    "Step 2: Do that...",
    "..."
  ]
}
```

### Metadata (Optional but Recommended)
```json
{
  "tags": ["quick", "healthy", "italian"],
  "cuisine": "Italian",
  "image_url": "https://..."
}
```

### Structured Ingredients (Auto-Generated)
```json
{
  "ingredients_structured": [
    {
      "item": "chicken breast",
      "amount": "1 pound",
      "original": "1 pound chicken breast, diced",
      "role": "main",              // main, secondary, or optional
      "classification": "essential", // essential, common, or optional
      "category": "protein"         // protein, produce, dairy, carb, spice, etc.
    }
  ]
}
```

---

## 🎯 Ingredient Classification

The system automatically classifies ingredients into three roles:

### Main Ingredients
- Define the dish's identity
- Featured in recipe title
- Listed first (top 3-4 ingredients)
- Substantial portion by weight

**Examples:**
- Chicken in "Chicken Curry"
- Pasta in "Pasta Carbonara"
- Eggs in "Scrambled Eggs"

### Secondary Ingredients
- Support the main ingredients
- Provide flavor, texture, moisture
- Aromatics (garlic, onions, ginger)
- Cooking fats (oil, butter)
- Sauces and liquids

**Examples:**
- Garlic and onions
- Olive oil
- Soy sauce, broth
- Bell peppers, tomatoes

### Optional Ingredients
- Can be omitted without affecting core recipe
- Garnishes and toppings
- "To taste" seasonings
- Serving suggestions

**Examples:**
- "Fresh parsley (optional)"
- "Salt and pepper to taste"
- "Parmesan for serving"

---

## 🛠️ Using the Recipe Tool

### Validate a Recipe
Check if your recipe is valid without adding it:

```bash
python tools/add_recipe.py my_recipe.json --validate-only
```

Output:
```
✅ VALIDATION PASSED!

📊 RECIPE SUMMARY:
   ID: my_recipe
   Name: My Amazing Recipe
   ...

✅ Validation complete (not added to database)
```

### Add a Recipe
Validate and add to database with auto-classification:

```bash
python tools/add_recipe.py my_recipe.json
```

Output:
```
✅ VALIDATION PASSED!
🤖 Auto-classifying ingredients...
✅ Classified 9 ingredients
   Main: 3, Secondary: 5, Optional: 1
📝 Adding recipe to database...
✅ Recipe added successfully!
🎉 Recipe 'My Amazing Recipe' is now in the database!
```

### Manual Classification
If you've already classified ingredients manually:

```bash
python tools/add_recipe.py my_recipe.json --no-auto-classify
```

---

## ✅ Quality Standards

### Good Ingredient Formatting
✅ **Include amounts and preparation:**
- `"2 cups all-purpose flour"`
- `"1 pound chicken breast, diced into 1-inch cubes"`
- `"3 cloves garlic, minced"`
- `"1/4 cup olive oil"`

❌ **Avoid vague or incomplete:**
- `"flour"` (no amount)
- `"some chicken"` (vague quantity)
- `"garlic"` (no amount or prep)

### Good Instruction Writing
✅ **Be specific and detailed:**
- `"Heat olive oil in a large skillet over medium-high heat."`
- `"Cook chicken for 5-7 minutes until golden brown and cooked through."`
- `"Bake at 375°F for 25-30 minutes until a toothpick comes out clean."`

❌ **Avoid vague instructions:**
- `"Cook the chicken"` (no details)
- `"Bake until done"` (no temperature/time)
- `"Mix everything"` (not specific)

### Good Descriptions
✅ **Appetizing and informative:**
- `"Creamy Italian pasta with crispy bacon and parmesan, ready in 20 minutes"`
- `"Spicy Thai curry with tender chicken, coconut milk, and fresh vegetables"`
- `"Classic chocolate cake with rich frosting, perfect for birthdays"`

❌ **Avoid generic descriptions:**
- `"A pasta dish"` (too vague)
- `"Yummy food"` (not descriptive)
- `"Recipe"` (tells nothing)

---

## 📖 Complete Documentation

### For Quick Reference
- **QUICK_START_ADD_RECIPE.md** - Get started in 5 minutes

### For Complete Details
- **RECIPE_SCHEMA.md** - Every field explained with examples

### For Developers
- **developer-kit/ingredient-classification/ALGORITHM.md** - Classification algorithm details

### Current Status
- **RECIPE_DATABASE_VALIDATION_REPORT.md** - Latest validation results

---

## 🔄 Workflow Examples

### Example 1: Adding a Quick Pasta Recipe

```bash
# 1. Copy template
cp recipe_templates/template_main_dish.json garlic_pasta.json

# 2. Edit garlic_pasta.json with your favorite editor
# ... (fill in all fields) ...

# 3. Validate first
python tools/add_recipe.py garlic_pasta.json --validate-only

# 4. If valid, add to database
python tools/add_recipe.py garlic_pasta.json

# 5. Done! Recipe is now in backend/data/recipes.json
```

### Example 2: Adding a Dessert

```bash
# 1. Copy dessert template
cp recipe_templates/template_dessert.json chocolate_cake.json

# 2. Edit and customize
nano chocolate_cake.json

# 3. Add directly (auto-validates)
python tools/add_recipe.py chocolate_cake.json

# 4. Recipe added with auto-classified ingredients!
```

### Example 3: Batch Adding Multiple Recipes

```bash
# Create multiple recipe files
cp recipe_templates/template_main_dish.json recipe1.json
cp recipe_templates/template_quick_meal.json recipe2.json
cp recipe_templates/template_dessert.json recipe3.json

# Edit each file...

# Add them all
for recipe in recipe*.json; do
    python tools/add_recipe.py "$recipe"
done
```

---

## 🎨 Recipe Templates

### Main Dish Template
**Use for:** Dinner, lunch, main courses
- 9 ingredients (typical)
- 9 steps (typical)
- 45 minutes total time
- Medium difficulty

### Quick Meal Template
**Use for:** Fast meals under 30 minutes
- 7 ingredients (minimal)
- 6 steps (streamlined)
- 25 minutes total time
- Easy difficulty

### Dessert Template
**Use for:** Cakes, cookies, sweets
- 8 ingredients (typical baking)
- 8 steps (baking process)
- 50 minutes total time
- Medium difficulty

### Blank Template
**Use for:** Any recipe type
- Minimal structure
- Fill everything from scratch
- Most flexible

---

## 📊 Database Statistics

Current database (as of validation):
- **Total Recipes:** 225
- **Properly Structured:** 225 (100%)
- **Total Ingredients:** 2,248
- **Dietary Options:**
  - Vegetarian: 91 (40.4%)
  - Vegan: 30 (13.3%)
  - Gluten-Free: 114 (50.7%)

---

## 🔍 Validation Rules

The tool checks for:

✅ **Required Fields**
- All core fields present
- Correct field types
- Valid enum values

✅ **Data Consistency**
- prep_time + cook_time ≈ total_time
- ingredients count = ingredients_structured count
- Valid difficulty and category values

✅ **Quality Standards**
- Description length (20+ chars recommended)
- At least 2-3 tags recommended
- Proper ingredient formatting

✅ **Uniqueness**
- Recipe ID not already in database

---

## 🆘 Troubleshooting

### Problem: "Recipe ID already exists"
**Solution:** Check `backend/data/recipes.json` for existing IDs and choose a unique one.

### Problem: "Missing required field"
**Solution:** Compare your recipe with a template to ensure all required fields are present.

### Problem: "Invalid JSON"
**Solution:** Use a JSON validator (jsonlint.com) to check for syntax errors.

### Problem: "ingredients_structured length mismatch"
**Solution:** Either:
- Leave `ingredients_structured` empty (auto-classify), or
- Ensure it has exactly the same number of items as `ingredients`

### Problem: "Tool not working"
**Solution:** 
1. Make sure you're in the MyFridge root directory
2. Check that Python and required modules are installed
3. Try: `python tools/add_recipe.py --help`

---

## 💡 Best Practices

### 1. Start with Templates
Always start with a template rather than a blank file. It's faster and less error-prone.

### 2. Validate First
Use `--validate-only` to check your recipe before adding it to the database.

### 3. Use Meaningful IDs
Make IDs descriptive:
- ✅ `chicken_tikka_masala`
- ✅ `vegan_chocolate_cake`
- ❌ `recipe1`, `food`, `new`

### 4. Write Clear Instructions
Each step should be actionable and specific. Include temperatures, times, and visual cues.

### 5. Add Relevant Tags
Tags improve searchability. Include:
- Dietary tags (vegetarian, vegan, gluten-free)
- Meal type (breakfast, lunch, dinner, snack)
- Features (quick, easy, healthy, budget-friendly)
- Cuisine (italian, mexican, chinese)

### 6. Test Your Recipe
Make sure your recipe works before adding it. The tool can't check if the recipe actually tastes good! 😄

---

## 🎓 Learning Resources

### Beginner
1. Read: **QUICK_START_ADD_RECIPE.md**
2. Copy: **template_main_dish.json**
3. Try: `python tools/add_recipe.py --validate-only`

### Intermediate
1. Read: **RECIPE_SCHEMA.md** (full documentation)
2. Create custom recipes from scratch
3. Understand ingredient classification

### Advanced
1. Read: **developer-kit/ingredient-classification/ALGORITHM.md**
2. Modify classification rules
3. Contribute improvements

---

## 📞 Support

### Documentation Files
- `RECIPE_SCHEMA.md` - Complete field reference
- `QUICK_START_ADD_RECIPE.md` - Quick start guide
- `RECIPE_DATABASE_VALIDATION_REPORT.md` - Current status

### Example Recipes
- Check `backend/data/recipes.json` for 225 real examples
- Use templates in `recipe_templates/`

### Validation
- Run: `python backend/validate_recipes.py` to check entire database
- Run: `python tools/add_recipe.py recipe.json --validate-only` for single recipe

---

## ✨ Summary

With this system, you can:
- ✅ Add recipes without external API calls
- ✅ Automatic ingredient classification
- ✅ Complete validation before adding
- ✅ Consistent structure across all recipes
- ✅ Easy to maintain and extend
- ✅ Professional quality standards

**Start adding recipes now and build your perfect recipe collection! 🍳**
