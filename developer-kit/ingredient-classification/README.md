# Ingredient Classification Algorithm - Developer Kit

**Version:** 2.0 (Main/Optional System)  
**Last Updated:** January 2026  
**For:** MyFridge Development Team

---

## Overview

This developer kit contains the complete documentation, tools, and utilities for maintaining and extending the MyFridge ingredient classification system. The classification algorithm determines which ingredients are **main** (defining), **secondary** (supporting), or **optional** (toppings/garnishes) in recipes.

## What's Included

```
developer-kit/ingredient-classification/
├── README.md                          # This file
├── ALGORITHM.md                       # Complete algorithm specification
├── TUNING_GUIDE.md                   # How to tune classification rules
├── EXAMPLES.md                        # Classification examples & test cases
├── tools/
│   ├── classify_single_recipe.py     # Test classification on one recipe
│   ├── batch_tune.py                 # Tune thresholds on gold-standard set
│   ├── diff_classifications.py       # Compare before/after classifications
│   └── export_for_review.py          # Export to spreadsheet for review
└── test-data/
    ├── gold_standard_recipes.json    # Manually validated recipes
    └── edge_cases.json               # Tricky classification cases
```

---

## Quick Start

### 1. Understanding the System

The classification system uses a **scoring-based algorithm** that evaluates each ingredient across multiple dimensions:

**Position** → Earlier ingredients score higher  
**Weight/Proportion** → Larger quantities score higher  
**Standards of Identity (SOI)** → Required components for food types  
**Defining Characteristic** → Ingredients matching recipe title  
**Explicit Markers** → "optional", "for serving", etc.

### 2. Running Classification

```bash
# Classify entire database
cd MyFridge/backend
source venv/bin/activate
python scraper/classify_ingredients.py

# Verify results
python scraper/verify_classification.py

# Test single recipe
cd ../developer-kit/ingredient-classification/tools
python classify_single_recipe.py "Classic French Toast"
```

### 3. Reviewing Classifications

```bash
# Export to CSV for team review
python tools/export_for_review.py

# Compare with previous classification
python tools/diff_classifications.py \
  data/recipes.pre_main_optional.json \
  data/recipes.json
```

---

## The Classification Algorithm

### Input
A recipe with a flat list of ingredient strings:
```json
{
  "name": "Classic French Toast",
  "ingredients": [
    "8 slices bread (brioche or thick white bread)",
    "4 large eggs",
    "1/2 cup milk",
    "1 teaspoon vanilla extract",
    "1 teaspoon cinnamon",
    "2 tablespoons butter",
    "Maple syrup for serving",
    "Powdered sugar for dusting (optional)",
    "Fresh berries (optional)"
  ]
}
```

### Output
Structured ingredients with roles and classifications:
```json
{
  "ingredients_structured": [
    {
      "original": "8 slices bread (brioche or thick white bread)",
      "item": "bread",
      "amount": "8 slices",
      "role": "main",
      "classification": "essential",
      "category": "carb"
    },
    {
      "original": "Maple syrup for serving",
      "item": "Maple syrup for serving",
      "amount": "",
      "role": "optional",
      "classification": "optional",
      "category": "topping"
    }
    // ... more ingredients
  ]
}
```

### Scoring Steps

**Step 1: Parse ingredient**
- Extract amount (quantity + unit)
- Extract item name (clean ingredient)
- Detect explicit optional markers

**Step 2: Calculate base score**
```python
score = 0

# Position bonus (FDA regulation - ingredients by descending weight)
position_bonus = max(0, 100 - (position * 10))
score += position_bonus

# Weight/proportion (estimated grams)
if estimated_grams > 100:
    score += 40
elif estimated_grams > 50:
    score += 20
elif estimated_grams > 10:
    score += 10

# Recipe title match (defining characteristic)
if ingredient_tokens_in_title:
    score += 50
```

**Step 3: Apply modifiers**
- Spice/seasoning penalty (-30 if < 2 tbsp)
- Cooking fat demotion (oil/butter)
- SOI/archetype boost (e.g., "mayo" in mayonnaise)
- Dish-specific rules (taco toppings, etc.)

**Step 4: Classify by threshold**
```python
if has_optional_marker:
    role = "optional"
elif score >= 60:
    role = "main"
elif score >= 20:
    role = "secondary"
else:
    role = "secondary"  # Default safe classification
```

**Step 5: Force-promote top N**
- Ensure at least 2-3 ingredients are "main" per recipe
- Respect position order
- Never promote cooking fats or tiny spice amounts

---

## Key Configuration Points

### Thresholds (in `classify_ingredients.py`)

```python
# Main classification threshold
MAIN_THRESHOLD = 60  # Adjust higher → fewer main ingredients

# Secondary threshold (rarely changed)
SECONDARY_THRESHOLD = 20

# Minimum main ingredients per recipe
MIN_MAIN_INGREDIENTS = 2

# Maximum main ingredients to force-promote
MAX_PROMOTED_MAIN = 5
```

### Weight Estimates

```python
UNIT_TO_GRAMS = {
    'cup': 240,
    'tablespoon': 15,
    'teaspoon': 5,
    'ounce': 28,
    'pound': 454,
    'gram': 1,
    'kg': 1000,
    'ml': 1,
    'liter': 1000,
}

COUNT_TO_GRAMS = {
    'egg': 50,
    'slice': 30,
    'clove': 3,
    'can': 400,
}
```

### Standards of Identity (SOI)

```python
SOI_ARCHETYPES = {
    'mayo': {'egg', 'oil'},
    'mayonnaise': {'egg', 'oil'},
    'chocolate': {'cocoa', 'chocolate'},
    'bread': {'flour', 'water', 'yeast'},
    'taco': {'tortilla', 'meat'},
    'pizza': {'dough', 'cheese', 'tomato'},
}
```

### Dish-Specific Optional Overrides

```python
DISH_OPTIONAL_TOPPINGS = {
    'taco': ['lettuce', 'tomato', 'cheese', 'sour cream', 'lime', 'salsa'],
    'burger': ['lettuce', 'tomato', 'onion', 'cheese', 'pickle'],
    'salad': ['dressing', 'croutons', 'cheese', 'nuts'],
    'pizza': ['basil', 'oregano'],
    'pasta': ['parmesan', 'basil', 'parsley'],
}
```

---

## Tuning the Algorithm

### When to Tune

**Tune when:**
- Reviewing team feedback on recipe classifications
- Adding new cuisine types with different conventions
- Noticing systematic misclassifications
- Preparing for new product categories

**Don't tune for:**
- One-off edge cases (add dish-specific override instead)
- Legacy data quality issues (fix the source data)
- Regional variations (use dish overrides)

### Tuning Process

1. **Collect gold standard set** (20-50 recipes manually reviewed)
2. **Run batch tuning tool** to find optimal thresholds
3. **Review changes** with classification diff tool
4. **Spot-check edge cases**
5. **Deploy and monitor**

```bash
# Step 1: Create gold standard (manual)
vim test-data/gold_standard_recipes.json

# Step 2: Run automated tuning
python tools/batch_tune.py test-data/gold_standard_recipes.json

# Step 3: Review proposed changes
python tools/diff_classifications.py old.json new.json

# Step 4: Spot check
python tools/classify_single_recipe.py "Edge Case Recipe Name"

# Step 5: Deploy
python scraper/classify_ingredients.py
```

---

## Common Tasks

### Adding a New Cuisine Type

1. Identify cuisine-specific main ingredients
2. Add to `SOI_ARCHETYPES` if there's a standard composition
3. Add common toppings to `DISH_OPTIONAL_TOPPINGS`
4. Test on 5-10 sample recipes
5. Adjust if needed

**Example: Adding Japanese cuisine**
```python
# In classify_ingredients.py
SOI_ARCHETYPES.update({
    'sushi': {'rice', 'fish', 'nori'},
    'ramen': {'noodles', 'broth'},
})

DISH_OPTIONAL_TOPPINGS.update({
    'ramen': ['egg', 'green onion', 'nori', 'sesame seeds'],
    'sushi': ['wasabi', 'ginger', 'soy sauce'],
})
```

### Fixing a Systematic Misclassification

**Problem:** All recipes with "herbs" classify them as main

**Solution:**
1. Check if it's a weight estimation issue
2. Add "herbs" to spice demotion list if not there
3. Reduce weight estimate for "herbs"
4. Re-run classification

```python
# Add to SPICE_KEYWORDS if missing
SPICE_KEYWORDS = [
    # ... existing ...
    'herbs', 'mixed herbs', 'dried herbs',
]

# Or adjust weight estimate
COUNT_TO_GRAMS.update({
    'bunch herbs': 20,  # Small amount
})
```

### Reviewing Team-Flagged Recipes

```bash
# Export specific recipes for review
python tools/export_for_review.py --recipe-ids "recipe_001,recipe_042,recipe_089"

# Review in spreadsheet, update gold standard
# Then re-tune if pattern emerges
```

---

## Data Quality Guidelines

### Input Data Requirements

**Good ingredient strings:**
- ✅ "2 cups all-purpose flour"
- ✅ "500g chicken breast, diced"
- ✅ "1 large onion, chopped"
- ✅ "Salt and pepper to taste"

**Poor ingredient strings:**
- ❌ "flour" (no amount)
- ❌ "Some chicken" (vague)
- ❌ "2" (no unit or item)
- ❌ "Spices" (too generic)

### Scraper Team Guidelines

When adding new scrapers or data sources:

1. **Parse quantities properly** - Extract amount and unit
2. **Preserve original text** - Keep "for serving", "optional" markers
3. **Clean consistently** - Remove HTML, normalize whitespace
4. **Validate completeness** - Every ingredient should have item name
5. **Test classification** - Run on sample before bulk import

---

## Testing & Validation

### Unit Tests

```python
# Test individual scoring components
def test_position_score():
    assert calculate_position_score(0, 10) > calculate_position_score(5, 10)

def test_weight_estimation():
    assert estimate_grams("2 cups flour") > 400
    assert estimate_grams("1 teaspoon salt") < 10

def test_title_matching():
    recipe_name = "Chocolate Chip Cookies"
    assert matches_title("chocolate chips", recipe_name) == True
    assert matches_title("flour", recipe_name) == False
```

### Integration Tests

```bash
# Test full classification pipeline
python -m pytest tests/test_classification_pipeline.py

# Test against gold standard
python tools/validate_against_gold_standard.py
```

### Manual Review Checklist

For each major cuisine or recipe category:
- [ ] 5 breakfast recipes reviewed
- [ ] 5 lunch/dinner recipes reviewed
- [ ] 3 dessert recipes reviewed
- [ ] 2 soup/stew recipes reviewed
- [ ] 2 salad recipes reviewed

---

## Performance Considerations

### Runtime Performance
- Classification is **O(n)** per recipe (n = number of ingredients)
- Typical recipe: 8-12 ingredients → ~0.1ms per recipe
- Full database (225 recipes): ~30ms total
- **Bottleneck:** Not the classification algorithm, but I/O

### Memory Usage
- Structured data adds ~200 bytes per ingredient
- 225 recipes × 10 ingredients × 200 bytes ≈ 450KB
- **Negligible impact** on application

### Optimization Tips
- Classification happens **once** during data import
- Frontend uses pre-classified data (no runtime cost)
- Only re-classify when:
  - Adding new recipes
  - Updating algorithm
  - Fixing data quality issues

---

## Troubleshooting

### "Too many main ingredients"

**Symptom:** Most ingredients classified as main  
**Likely cause:** Threshold too low  
**Fix:** Increase `MAIN_THRESHOLD` from 60 to 70-80

### "Not enough main ingredients"

**Symptom:** Only 1 main per recipe  
**Likely cause:** Position scoring too weak or threshold too high  
**Fix:** Increase position bonus or decrease `MAIN_THRESHOLD`

### "Spices classified as main"

**Symptom:** Cumin, paprika, etc. showing as main  
**Likely cause:** Large quantities or missing spice keywords  
**Fix:** Add to `SPICE_KEYWORDS` and ensure weight penalty applies

### "Toppings not marked optional"

**Symptom:** Garnishes showing as main/secondary  
**Likely cause:** Missing dish override or no explicit marker  
**Fix:** Add to `DISH_OPTIONAL_TOPPINGS` or update scraper to preserve "for serving"

---

## Integration Points

### Backend API
- Classification happens during data import (scraper level)
- API returns `ingredients_structured` field
- No runtime classification overhead

### Frontend
- Reads `role` field to determine main vs optional
- Falls back to `classification` for backward compatibility
- Uses main ingredients for "Best Match" sorting

### Scraper Pipeline
```
Raw Recipe → Legal Importer → Classifier → Database
```

All scrapers call `classify_recipe_ingredients()` automatically.

---

## Version History

### v2.0 (Current) - Main/Optional System
- Added position-based scoring (FDA guideline)
- Weight/proportion estimation from parsed amounts
- SOI/archetype rules
- Title matching for defining characteristic
- Dish-specific optional overrides
- Force-promotion to ensure minimum main ingredients

### v1.0 - Keyword System (Deprecated)
- Simple keyword matching
- Three levels: essential/common/optional
- No context awareness
- ~46% common, ~47% essential, ~6% optional

---

## Support & Maintenance

### For Development Team

**Primary Contact:** System Architect  
**Classification Issues:** Open ticket in dev-tools repo  
**Algorithm Questions:** See ALGORITHM.md (detailed spec)  
**Tuning Requests:** Use batch_tune tool first, then escalate

### Update Checklist

When modifying the algorithm:
- [ ] Update thresholds/rules in `classify_ingredients.py`
- [ ] Update documentation in developer-kit
- [ ] Run verification script
- [ ] Test on gold standard set
- [ ] Update version number
- [ ] Document changes in CHANGELOG

---

## Additional Resources

- `ALGORITHM.md` - Complete mathematical specification
- `TUNING_GUIDE.md` - Step-by-step tuning procedures
- `EXAMPLES.md` - 50+ classification examples with explanations
- `tools/` - Utilities for testing and tuning
- `test-data/` - Gold standard and edge cases

---

## Quick Reference

### Key Files
```
backend/scraper/classify_ingredients.py   # Main algorithm
backend/scraper/verify_classification.py  # Verification tool
backend/data/recipes.json                 # Classified database
developer-kit/ingredient-classification/  # This kit
```

### Key Functions
```python
classify_recipe_ingredients(recipe)  # Main entry point
_score_ingredient(ing, idx, total, recipe_name)  # Scoring
_estimate_grams(amount_str, item_str)  # Weight estimation
_is_optional_marker(text)  # Detect explicit optionals
```

### Key Constants
```python
MAIN_THRESHOLD = 60           # Main classification cutoff
MIN_MAIN_INGREDIENTS = 2      # Force-promote minimum
SPICE_KEYWORDS = [...]        # Spice demotion list
DISH_OPTIONAL_TOPPINGS = {...}  # Dish overrides
```

---

**Questions?** See detailed docs in ALGORITHM.md and TUNING_GUIDE.md

