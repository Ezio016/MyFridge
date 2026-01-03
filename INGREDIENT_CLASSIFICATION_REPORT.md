# Ingredient Classification Report

**Date:** January 2, 2026  
**Total Recipes Analyzed:** 225  
**Total Ingredients:** 2,248  
**Specialty Ingredients Found:** 537  

---

## 🔴 SPECIALTY INGREDIENTS (NEVER Optional)

These are ingredients that define the recipe's identity. Without them, it's a different dish.

### Top Specialty Ingredients in Database:

| Ingredient | Count | Examples |
|------------|-------|----------|
| **Paprika** | 15 | Quick Chicken Tacos, Beef Empanadas |
| **Chorizo** | 13 | Chicken Basquaise, Spanish meatballs |
| **Bacon** | 13 | Beef Bourguignon, Lasagne |
| **Chicken Stock** | 12 | Chicken & chorizo rice pot, Chicken Couscous |
| **Parsley** | 11 | Chicken Alfredo, Lamb Tagine |
| **Cumin** | 8 | Quick Chicken Tacos, Lamb chops |
| **Greek Yogurt** | 8 | Turkish delight mess, Beetroot pancakes |
| **Lamb** | 7 | Norwegian Fårikål, Kofta burgers |
| **Almonds** | 7 | Baklava, Turkish delight mess |
| **White Wine** | 6 | Chicken Parmentier, Duck Confit |
| **Thyme** | 5 | Classic Chicken Noodle Soup, Brown Stew Chicken |
| **Heavy Cream** | 4 | Creamy Tomato Soup, Chicken Alfredo |
| **Parmesan Cheese** | 4 | Spaghetti Aglio e Olio, Caesar Salad |
| **Sour Cream** | 4 | Tacos, Chicken & halloumi burgers |
| **Chickpeas** | 4 | Chicken Couscous, Hummus |
| **Oyster Sauce** | 3 | Easy Chicken Stir-Fry, Egg Foo Young |
| **Fish Sauce** | 3 | Easy Pad Thai, Beef pho |
| **Cardamom** | 3 | Beef Bourguignon, Lamb Biryani |
| **Cayenne Pepper** | 3 | Cajun fish tacos, Gambas al ajillo |
| **Walnuts** | 3 | Baklava, Canadian Butter Tarts |
| **Saffron** | 3 | Lamb Pilaf, Spanish paella |
| **Fresh Mozzarella** | 2 | Classic Caprese Salad, Margherita Pizza |
| **Honey** | 2 | Teriyaki Chicken Bowl, Overnight Oats |
| **Avocado** | 2 | Fresh Guacamole, Avocado Toast |

---

## ✅ MAIN INGREDIENTS (The Core of Each Recipe)

These are the primary ingredients that aren't pantry staples or specialty items. They're what you buy specifically for the recipe.

### Top 30 Main Ingredients:

1. **Bay Leaf** (20 recipes) - Actually should be pantry staple? Consider moving
2. **Milk** (18 recipes) - Core dairy ingredient
3. **Eggs** (17 recipes) - Core protein
4. **Potatoes** (13 recipes) - Core vegetable
5. **Cornstarch** (7 recipes) - Thickening agent
6. **Tomato** (7 recipes) - Core produce
7. **Beef** (7 recipes) - Core protein
8. **Carrots** (7 recipes) - Core vegetable
9. **Double Cream** (7 recipes) - Specialty dairy (UK term for heavy cream)
10. **Cinnamon** (6 recipes) - Should be pantry spice? Consider moving
11. **Lime** (6 recipes) - Fresh citrus
12. **Basmati Rice** (6 recipes) - Core grain
13. **Chicken** (6 recipes) - Core protein
14. **Tomato Puree** (6 recipes) - Core ingredient
15. **Breadcrumbs** (6 recipes) - Coating/binding
16. **Yeast** (6 recipes) - Baking essential
17. **Cherry Tomatoes** (6 recipes) - Fresh produce
18. **Vanilla Extract** (5 recipes) - Baking flavor
19. **Baking Powder** (5 recipes) - Baking leavener
20. **Chicken Breast** (5 recipes) - Core protein
21. **Ginger** (5 recipes) - Fresh spice
22. **Lemon** (5 recipes) - Fresh citrus
23. **Mushrooms** (5 recipes) - Core vegetable
24. **Self-Raising Flour** (5 recipes) - Specialty flour

---

## 🟢 BASIC PANTRY STAPLES (Always Optional)

These are items that virtually everyone has in their kitchen. If a recipe needs these, we assume they're available.

### Current Pantry List:

**Seasonings:**
- Salt
- Pepper / Black Pepper
- Garlic / Garlic Powder
- Onion / Onion Powder

**Oils & Fats:**
- Oil / Cooking Oil
- Olive Oil
- Vegetable Oil
- Canola Oil
- Butter (Salted/Unsalted)

**Sweeteners:**
- Sugar / White Sugar
- Granulated Sugar

**Flour (ONLY basic):**
- Flour (plain)
- All-Purpose Flour
- AP Flour
- Plain Flour

**Liquids:**
- Water

**Condiments:**
- Soy Sauce
- Vinegar
- White Vinegar
- Balsamic Vinegar

---

## ⚠️ ITEMS THAT NEED REVIEW

### Should These Be Pantry Staples?

**Bay Leaf** (20 recipes)
- **Current:** Main ingredient
- **Consideration:** Very common in recipes, long shelf life
- **Recommendation:** ❓ Consider adding to pantry staples

**Cinnamon** (6 recipes)
- **Current:** Main ingredient
- **Consideration:** Common spice, long shelf life
- **Recommendation:** ❓ Consider adding to pantry staples

**Vanilla Extract** (5 recipes)
- **Current:** Main ingredient
- **Consideration:** Common baking ingredient
- **Recommendation:** ❓ Consider adding to pantry staples

**Baking Powder** (5 recipes)
- **Current:** Main ingredient
- **Consideration:** Essential baking ingredient
- **Recommendation:** ✅ Should probably be pantry staple

### Should These Be Specialty?

**Cornstarch** (7 recipes)
- **Current:** Main ingredient
- **Consideration:** Thickening agent, not always on hand
- **Recommendation:** ✅ Keep as main ingredient

**Breadcrumbs** (6 recipes)
- **Current:** Main ingredient
- **Consideration:** Coating ingredient, easy to make from bread
- **Recommendation:** ✅ Keep as main ingredient

---

## 📊 CLASSIFICATION BREAKDOWN

```
Total Ingredients:    2,248
├─ Specialty:           537 (23.9%) - Recipe-defining ingredients
├─ Basic Pantry:        ~200 (8.9%) - Universal kitchen staples  
└─ Main Ingredients:  1,511 (67.2%) - Core recipe items
```

---

## 🔧 CHANGES MADE TO CODE

### Updated Specialty Keywords List:

**Added categories:**
1. **Specialty Flours** - chickpea, almond, coconut, rice flour, etc.
2. **Specialty Dairy** - parmesan, greek yogurt, heavy cream, etc.
3. **Specialty Proteins** - prosciutto, bacon, chorizo, lamb, salmon, etc.
4. **Specialty Produce** - avocado, eggplant, asparagus, etc.
5. **Specialty Condiments** - tahini, miso, fish sauce, pesto, etc.
6. **Specialty Herbs/Spices** - saffron, cardamom, cumin, paprika, etc.
7. **Specialty Nuts/Seeds** - pine nuts, cashews, walnuts, etc.
8. **Specialty Sweeteners** - honey, maple syrup, molasses, etc.
9. **Specialty Grains** - quinoa, couscous, chickpeas, etc.
10. **Specialty Liquids** - coconut milk, wine, stock, tomato paste, etc.

### Total Specialty Keywords: ~150+

---

## ✅ EXAMPLES OF CORRECT CLASSIFICATION

### ✅ Faina (Now CORRECT)
**Ingredients:**
- Chickpea Flour → **MAIN** (specialty flour)
- Water → Pantry
- Olive Oil → Pantry
- Salt → Pantry

**Result:** Main 0/1 → RED (missing chickpea flour) ✅

### ✅ Pancakes (Still CORRECT)
**Ingredients:**
- All-Purpose Flour → Pantry
- Eggs → **MAIN**
- Milk → **MAIN**
- Sugar → Pantry
- Butter → Pantry

**Result:** Main 2/2 (with eggs & milk) → GREEN ✅

### ✅ Chicken Alfredo (CORRECT)
**Ingredients:**
- Chicken → **MAIN**
- Heavy Cream → **MAIN** (specialty dairy)
- Parmesan → **MAIN** (specialty cheese)
- Pasta → **MAIN**
- Butter → Pantry
- Garlic → Pantry

**Result:** Main X/4 → Depends on what user has

---

## 💡 RECOMMENDATIONS

### For Better Accuracy:

1. **Add common spices to pantry:**
   - Bay leaf
   - Cinnamon
   - Vanilla extract
   - Baking powder

2. **Keep specialty detection strict:**
   - All cheese types (except "cheese" alone) = specialty
   - All flours except all-purpose = specialty
   - All herbs/spices = specialty (or add common ones to pantry)

3. **Consider user preferences:**
   - Some users may have extensive spice collections
   - Allow users to mark items as "I always have this"
   - Custom pantry settings per user

---

## 📝 FILES UPDATED

1. **`frontend/src/pages/Chef.jsx`**
   - Enhanced `isPantryStaple()` function
   - Added 150+ specialty keywords
   - Strict flour detection (chickpea flour ≠ flour)

2. **`backend/scraper/audit_ingredients.py`**
   - Created comprehensive auditing tool
   - Analyzes all 225 recipes
   - Exports specialty and pantry lists

3. **`backend/scraper/audit_results/`**
   - SPECIALTY_INGREDIENTS.txt (reference list)
   - BASIC_PANTRY.txt (reference list)

---

## 🎯 IMPACT

**Before Fix:**
- Faina showed GREEN without chickpea flour
- Almond cake showed GREEN without almond flour
- Users confused: "Why show recipes I can't make?"

**After Fix:**
- Faina shows RED without chickpea flour ✅
- Almond cake shows RED without almond flour ✅
- Users see accurate recipe availability ✅

**User Trust:**
- Lightning mode: Only truly makeable recipes
- Explore mode: Accurate green/red indicators
- Recipe identity preserved

---

**Report Generated By:** Ingredient Auditor v1.0  
**Next Audit Recommended:** When adding new recipe sources

