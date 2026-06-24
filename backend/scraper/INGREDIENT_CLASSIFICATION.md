# Ingredient Classification System

## Overview

MyFridge now uses a sophisticated ingredient classification system that categorizes recipe ingredients into three levels:

- **Essential**: Main ingredients that define the dish (proteins, main carbs, key produce)
- **Common**: Pantry staples and common cooking ingredients (oils, basic seasonings, dairy)
- **Optional**: Toppings, garnishes, and enhancement ingredients (maple syrup, fresh herbs for garnish)

This system dramatically improves recipe matching and "Best Match" sorting by distinguishing between ingredients you MUST have vs nice-to-have items.

## Classification Categories

### Essential Ingredients (47.4% of all ingredients)

These are the core ingredients that define a recipe. If you're missing these, you can't really make the dish:

- **Proteins**: chicken, beef, pork, fish, tofu, eggs (when used as main ingredient)
- **Main Carbs**: pasta, rice, specific bread types (when the main focus)
- **Key Produce**: Main vegetables and fruits that define the dish
- **Signature Ingredients**: Unique items that make the recipe special

**Examples:**
- French Toast: eggs (binding agent)
- Pasta Marinara: pasta, crushed tomatoes
- Chicken Tacos: chicken, tortillas, taco seasoning

### Common Ingredients (46.3% of all ingredients)

These are pantry staples and cooking basics that most people have or can easily substitute:

- **Cooking Fats**: olive oil, vegetable oil, butter
- **Basic Seasonings**: salt, pepper, garlic, onion
- **Baking Basics**: vanilla extract, cinnamon, baking powder
- **Basic Dairy**: milk, common cheeses
- **Common Sauces**: soy sauce, ketchup, mustard

**Examples:**
- French Toast: bread, milk, vanilla extract, cinnamon, butter
- Pasta Marinara: olive oil, garlic
- Fried Rice: vegetable oil, soy sauce

### Optional Ingredients (6.3% of all ingredients)

These are toppings, garnishes, and enhancements that improve the dish but aren't necessary:

- **Toppings**: maple syrup, powdered sugar, whipped cream
- **Garnishes**: fresh herbs for serving, lemon wedges
- **Enhancements**: optional spices, serving suggestions

**Examples:**
- French Toast: maple syrup, powdered sugar, fresh berries
- Pasta Marinara: fresh basil for garnish, parmesan for serving

## How It Works

### 1. Classification Rules (`classify_ingredients.py`)

The system uses keyword-based classification rules to automatically categorize ingredients:

```python
CLASSIFICATION_RULES = {
    'topping': {
        'keywords': ['for serving', 'for garnish', 'optional', 'to taste'],
        'classification': 'optional',
        'category': 'topping'
    },
    'protein': {
        'keywords': ['chicken breast', 'beef', 'eggs', 'tofu'],
        'classification': 'essential',
        'category': 'protein'
    },
    # ... more rules
}
```

### 2. Structured Ingredient Format

Each ingredient is converted from a simple string to a structured object:

```json
{
  "item": "eggs",
  "amount": "4 large",
  "original": "4 large eggs",
  "classification": "essential",
  "category": "protein"
}
```

### 3. Recipe Matching in Frontend

The frontend now uses this classification for smarter matching:

```javascript
// Old way: keyword-based pantry detection
if (isPantryStaple(ing)) return true

// New way: use structured classification
if (structuredIng.classification === 'optional' || 
    structuredIng.classification === 'common') {
  return true
}
```

## Benefits

### 1. Better Recipe Matching

**Before:** French Toast would show as "missing 3 ingredients" if you don't have maple syrup, powdered sugar, and fresh berries.

**After:** French Toast shows as "ready to cook" if you have bread, eggs, and milk. The optional toppings don't count against it.

### 2. Smarter "Best Match" Sorting

The algorithm now considers:
1. **Essential ingredients you have** (highest priority)
2. **Common ingredients you have** (medium priority)
3. **Optional ingredients** (don't count as missing)

### 3. Accurate Readiness Indicators

Recipes marked as "Ready to Cook" now truly represent dishes you can make without creative substitution.

### 4. Better Filtering

The "Only Use ingredients in Fridge" filter now correctly identifies recipes where you have all the ESSENTIAL ingredients, not counting optional garnishes.

## Database Schema

### Recipe Structure

```json
{
  "id": "recipe_123",
  "name": "Classic French Toast",
  "ingredients": [
    "8 slices bread",
    "4 large eggs",
    "1/2 cup milk",
    "Maple syrup for serving"
  ],
  "ingredients_structured": [
    {
      "item": "bread",
      "amount": "8 slices",
      "original": "8 slices bread",
      "classification": "common",
      "category": "pantry"
    },
    {
      "item": "eggs",
      "amount": "4 large",
      "original": "4 large eggs",
      "classification": "essential",
      "category": "protein"
    },
    {
      "item": "milk",
      "amount": "1/2 cup",
      "original": "1/2 cup milk",
      "classification": "common",
      "category": "dairy"
    },
    {
      "item": "Maple syrup",
      "amount": "for serving",
      "original": "Maple syrup for serving",
      "classification": "optional",
      "category": "topping"
    }
  ]
}
```

## Scraper Integration

All scraper scripts now automatically classify ingredients:

### api_recipe_importer.py
```python
legal_recipe = self.legal_importer.create_legal_recipe(raw_recipe, use_ai=use_ai)
legal_recipe = classify_recipe_ingredients(legal_recipe)  # Auto-classify
new_recipes.append(legal_recipe)
```

### legal_recipe_importer.py
```python
if CLASSIFIER_AVAILABLE:
    recipe = classify_recipe_ingredients(recipe)
```

### simple_recipe_bootstrap.py
```python
processed = importer.create_legal_recipe(recipe, use_ai=False)
processed = classify_recipe_ingredients(processed)  # Auto-classify
```

## Usage

### Classifying Existing Recipes

```bash
cd MyFridge/backend
source venv/bin/activate
python scraper/classify_ingredients.py
```

This will:
1. Read `data/recipes.json`
2. Classify all ingredients
3. Create `data/recipes.classified.json`
4. Show statistics and examples

### Verifying Classification

```bash
python scraper/verify_classification.py
```

Shows:
- Count of recipes with structured ingredients
- Classification breakdown (essential/common/optional)
- Sample recipes with classifications
- Specific examples (French Toast, etc.)

### Adding New Recipes

New recipes added via any scraper will automatically be classified. No action needed!

## Future Improvements

1. **ML-Based Classification**: Train a model to better understand ingredient importance based on recipe context.

2. **User Preferences**: Learn which ingredients a user considers "pantry staples" vs "specialty."

3. **Substitution Suggestions**: "You're missing eggs, but you can use flax eggs" for essential ingredients.

4. **Cuisine-Specific Rules**: Japanese recipes might treat soy sauce as common, while Italian recipes treat it as specialty.

5. **Seasonal Adjustments**: Fresh berries might be common in summer, specialty in winter.

## Statistics (Current Database)

- **Total Recipes**: 225
- **Total Ingredients**: 2,248
- **Essential**: 1,066 (47.4%)
- **Common**: 1,041 (46.3%)
- **Optional**: 141 (6.3%)

## Maintenance

The classification system requires minimal maintenance:

1. **Rules Updates**: Edit `CLASSIFICATION_RULES` in `classify_ingredients.py` if needed.
2. **Re-classify**: Run classification script after rule updates.
3. **Verification**: Run verify script to check results.

## Example Impact

### French Toast Before:
```
Missing: 3 ingredients
- Maple syrup
- Powdered sugar  
- Fresh berries
```

### French Toast After:
```
Ready to Cook! ✓
Optional (if available):
- Maple syrup
- Powdered sugar
- Fresh berries
```

This makes a HUGE difference in user experience!

