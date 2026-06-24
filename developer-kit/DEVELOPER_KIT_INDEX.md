# MyFridge Developer Kit - Complete Index

**Version:** 1.0  
**Last Updated:** January 2026  
**Purpose:** Development team resources (not part of production app)

---

## What is This?

The MyFridge Developer Kit contains all documentation, tools, and utilities needed by the **development team** to maintain and extend the application. This is **NOT** part of the production app package—it's for developers only.

---

## Directory Structure

```
developer-kit/
│
├── DEVELOPER_KIT_INDEX.md          # This file
│
└── ingredient-classification/       # Ingredient classification system
    │
    ├── README.md                    # Quick start & overview
    ├── ALGORITHM.md                 # Complete algorithm specification
    ├── TUNING_GUIDE.md             # How to tune thresholds
    ├── EXAMPLES.md                  # Classification examples
    │
    ├── tools/                       # Development utilities
    │   ├── classify_single_recipe.py    # Test one recipe
    │   ├── batch_tune.py                # Auto-tune thresholds
    │   ├── diff_classifications.py      # Compare versions
    │   └── export_for_review.py         # Export to CSV
    │
    └── test-data/                   # Test datasets
        ├── gold_standard_recipes.json   # Validated recipes
        └── edge_cases.json              # Tricky cases
```

---

## Quick Navigation

### For Product Managers

**Want to understand how recipe classification works?**
→ Read: `ingredient-classification/README.md`

**Want to review classification quality?**
→ Run: `ingredient-classification/tools/export_for_review.py`

**Want specific examples?**
→ Read: `ingredient-classification/EXAMPLES.md`

### For Developers

**Need to modify the algorithm?**
→ Read: `ingredient-classification/ALGORITHM.md`  
→ Edit: `backend/scraper/classify_ingredients.py`

**Need to tune thresholds?**
→ Read: `ingredient-classification/TUNING_GUIDE.md`  
→ Run: `ingredient-classification/tools/batch_tune.py`

**Need to test a single recipe?**
→ Run: `ingredient-classification/tools/classify_single_recipe.py "Recipe Name"`

**Need to compare before/after?**
→ Run: `ingredient-classification/tools/diff_classifications.py`

### For QA/Testing

**Need to validate classification quality?**
→ Run: `backend/scraper/verify_classification.py`

**Need test data?**
→ Check: `ingredient-classification/test-data/`

**Need to create review CSV?**
→ Run: `ingredient-classification/tools/export_for_review.py`

### For Data Team

**Adding new recipes from scrapers?**
→ Algorithm auto-runs during scraping (no action needed)

**Updating classification rules?**
→ Edit constants in `backend/scraper/classify_ingredients.py`  
→ Re-run: `python backend/scraper/classify_ingredients.py`

**Need to understand data structure?**
→ Read: `ingredient-classification/ALGORITHM.md` (Data Schema section)

---

## Common Tasks

### Task 1: Review Classification Quality

```bash
# Export all recipes to CSV for review
cd MyFridge/developer-kit/ingredient-classification/tools
python export_for_review.py --summary

# Open the generated CSV in Excel
open recipe_review_summary_*.csv
```

### Task 2: Test a Single Recipe

```bash
cd MyFridge/developer-kit/ingredient-classification/tools
python classify_single_recipe.py "French Toast"

# Or test with mock data
python classify_single_recipe.py --test
```

### Task 3: Tune Algorithm

```bash
# 1. Create/update gold standard
vim MyFridge/developer-kit/ingredient-classification/test-data/gold_standard_recipes.json

# 2. Run tuning (finds optimal thresholds)
cd MyFridge/developer-kit/ingredient-classification/tools
python batch_tune.py ../test-data/gold_standard_recipes.json

# 3. Review results and update classify_ingredients.py if needed
```

### Task 4: Update Database

```bash
# After modifying classification algorithm
cd MyFridge/backend
source venv/bin/activate
python scraper/classify_ingredients.py

# Verify results
python scraper/verify_classification.py
```

### Task 5: Compare Versions

```bash
cd MyFridge/developer-kit/ingredient-classification/tools

# Compare old vs new classification
python diff_classifications.py \
  ../../backend/data/recipes.pre_main_optional.json \
  ../../backend/data/recipes.json
```

---

## Key Concepts

### Ingredient Roles (Main/Secondary/Optional)

**Main** → Defining ingredients that characterize the dish
- Examples: pasta in pasta marinara, eggs in French toast, chicken in chicken tacos
- Typically 2-5 per recipe
- Listed first in ingredient list (FDA regulation)

**Secondary** → Supporting ingredients that contribute but aren't defining
- Examples: garlic, olive oil, spices, butter
- Typically 4-8 per recipe
- Important but substitutable

**Optional** → Toppings, garnishes, serving suggestions
- Examples: maple syrup for serving, fresh herbs for garnish, optional cheese
- Typically 0-3 per recipe
- Nice to have but not required

### Classification Algorithm

The system uses a **scoring pipeline**:

1. **Position** → Earlier = more important (FDA guideline)
2. **Weight/Proportion** → Larger quantity = more important
3. **Standards of Identity** → Required ingredients for defined foods
4. **Title Matching** → Ingredients in recipe name = defining
5. **Modifiers** → Demote spices, oils, toppings

Score ≥ 60 → Main  
Score ≥ 20 → Secondary  
Score < 20 → Secondary (default)

Explicit markers ("optional", "for serving") → always Optional

### Why This Matters

**Better Recipe Matching:**
- French Toast with just "bread, eggs, milk" shows as "Ready to Cook!"
- Before: showed "Missing 3 ingredients" (maple syrup, berries, powdered sugar)

**Smarter Filtering:**
- "Only Use ingredients in Fridge" filter now works correctly
- Doesn't penalize for missing optional garnishes

**Accurate Sorting:**
- "Best Match" prioritizes recipes where you have main ingredients
- Secondary ingredients matter less

---

## Integration Points

### Scrapers
All recipe scrapers automatically call the classifier:
```python
from scraper.classify_ingredients import classify_recipe_ingredients

recipe = {...}  # Raw scraped recipe
recipe = classify_recipe_ingredients(recipe)  # Auto-classifies
save_to_database(recipe)
```

### Backend API
The classification happens during data import, not at runtime:
```
Raw Recipe → Scraper → Classifier → Database → API → Frontend
                           ▲
                     (one-time, offline)
```

### Frontend
Frontend reads pre-classified data:
```javascript
const recipe = await fetchRecipe(id);
const mainIngredients = recipe.ingredients_structured
  .filter(ing => ing.role === 'main');
```

---

## Performance

### Classification Speed
- 1 recipe: ~0.1ms
- 225 recipes: ~30ms
- **Bottleneck:** I/O (loading JSON), not classification

### Production Impact
- **Zero runtime overhead** (pre-classified during import)
- ~200 bytes additional storage per ingredient
- Total: ~450KB for 225 recipes (negligible)

---

## Maintenance Schedule

### Weekly
- [ ] Review team-flagged recipes
- [ ] Update gold standard if patterns found

### Monthly
- [ ] Export sample for QA review
- [ ] Check classification metrics
- [ ] Update documentation if rules changed

### Quarterly
- [ ] Full database re-classification (if algorithm updated)
- [ ] Tune thresholds based on feedback
- [ ] Review edge cases

### As Needed
- [ ] Add new cuisine-specific rules
- [ ] Handle new recipe formats
- [ ] Update SOI archetypes

---

## Support & Questions

### For Algorithm Questions
→ See: `ingredient-classification/ALGORITHM.md`

### For Tuning Help
→ See: `ingredient-classification/TUNING_GUIDE.md`

### For Examples
→ See: `ingredient-classification/EXAMPLES.md`

### For Bug Reports
→ Include: recipe name/ID, expected vs actual classification, context

### For Feature Requests
→ Describe: use case, affected recipes, desired behavior

---

## Version History

### v1.0 (January 2026)
- Initial developer kit release
- Ingredient classification system v2.0
- Complete documentation
- Developer tools suite

---

## What's NOT in This Kit

**Not included (part of production app):**
- Actual application code (in `backend/` and `frontend/`)
- Recipe database (in `backend/data/`)
- Scraper code (in `backend/scraper/`)

**Included (for developers only):**
- Documentation
- Tuning tools
- Test utilities
- Gold standard datasets
- Development guides

---

## Quick Reference Card

```bash
# Test single recipe
python tools/classify_single_recipe.py "Recipe Name"

# Export for review
python tools/export_for_review.py --summary

# Re-classify database
cd ../../backend && python scraper/classify_ingredients.py

# Verify classification
cd ../../backend && python scraper/verify_classification.py

# Compare versions
python tools/diff_classifications.py old.json new.json
```

---

**Remember:** This developer kit is for the development team only. Do not include in production builds or deployments.

For questions, contact the system architect or see individual README files in each directory.

