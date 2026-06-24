# Ingredient Groups & Recipe Variants

## Problem Statement

Some recipes call for ingredients that can be either:
1. **Purchased ready-made** (e.g., bottled teriyaki sauce)
2. **Made from scratch** using common ingredients (e.g., soy sauce + honey + vinegar + oil + garlic + ginger)

This creates challenges for recipe readiness calculation:
- If we mark all sauce components as "main ingredients", users with bottled sauce won't see the recipe as "ready"
- If we mark them as "optional", users without ANY of them might think they can make it (which they can't)

## Solution: Ingredient Groups

The app now recognizes **ingredient groups** where a single primary ingredient (like "teriyaki sauce") can be replaced by a set of component ingredients.

### How It Works

1. **Recipe Recognition**: When a recipe calls for "teriyaki sauce" (or any of its components), the system checks:
   - ✅ Do you have bottled teriyaki sauce? → **Recipe ready!**
   - ✅ Do you have ALL components (soy sauce, honey, vinegar, oil, garlic, ginger)? → **Recipe ready! (Make from scratch)**
   - ❌ Do you have only some components? → **Missing ingredients** (shows what's needed)

2. **Smart Shopping**: 
   - If you have all components → Don't recommend the bottled version
   - If you have the bottle → Don't recommend the components
   - If you have neither → Recommend the shortcut (bottled) for students

3. **UI Display**:
   - Shows which method you're using (bottled or from scratch)
   - For missing groups, suggests BOTH options:
     - Buy the ready-made version
     - Get the missing components to make it yourself

## Supported Ingredient Groups

Currently defined groups (see `frontend/src/utils/ingredientGroups.js`):

### 1. Teriyaki Sauce
- **Primary**: teriyaki sauce
- **Components**: soy sauce, honey, rice vinegar, sesame oil, garlic, ginger
- **Use Case**: Asian stir-fries, marinades

### 2. Curry Paste
- **Primary**: curry paste
- **Components**: curry powder, garlic, ginger, onion, oil
- **Use Case**: Curries, stews

### 3. Pesto Sauce
- **Primary**: pesto
- **Components**: basil, garlic, pine nuts, parmesan, olive oil
- **Use Case**: Pasta, sandwiches

### 4. Marinara Sauce
- **Primary**: marinara sauce
- **Components**: tomato, garlic, onion, olive oil, basil, oregano
- **Use Case**: Pasta, pizza

### 5. Alfredo Sauce
- **Primary**: alfredo sauce
- **Components**: butter, cream, parmesan, garlic
- **Use Case**: Pasta, chicken dishes

## Adding New Ingredient Groups

To add a new ingredient group, edit `frontend/src/utils/ingredientGroups.js`:

```javascript
export const INGREDIENT_GROUPS = {
  // ... existing groups ...
  
  yourNewGroup: {
    primary: 'ready-made ingredient name',
    components: ['ingredient1', 'ingredient2', 'ingredient3'],
    description: 'Human-readable description for UI',
    category: 'sauce', // or 'spice-blend', 'base', etc.
  },
}
```

## Example: Teriyaki Chicken Recipe

### Original Recipe (Ambiguous)
```
Ingredients:
- Chicken thighs
- Soy sauce
- Honey
- Rice vinegar
- Sesame oil
- Garlic
- Ginger
- Cornstarch
```

**Problem**: Are soy sauce, honey, etc. "main" or "optional"? Users might not realize they're making teriyaki sauce.

### With Ingredient Groups (Clear)

**Scenario 1**: User has bottled teriyaki sauce
```
✓ Chicken thighs
✓ Teriyaki sauce
  🛒 Using bottled teriyaki sauce
✓ Cornstarch

Recipe Status: Ready to cook! ✨
```

**Scenario 2**: User has components but no bottle
```
✓ Chicken thighs
✓ Teriyaki sauce
  👨‍🍳 Making from scratch
✓ Cornstarch

Recipe Status: Ready to cook! ✨
```

**Scenario 3**: User missing some components
```
✓ Chicken thighs
✗ Teriyaki sauce
  💡 Teriyaki sauce (or make your own: soy sauce, honey, rice vinegar, sesame oil, garlic, ginger)
  💭 Or get: teriyaki sauce
  Missing: honey, rice vinegar
✓ Cornstarch

Recipe Status: Missing 2 ingredients
```

## Technical Implementation

### 1. Detection (`checkIngredientGroup`)
```javascript
const result = checkIngredientGroup('teriyaki sauce', userInventory)
// Returns: { satisfied: true/false, method: 'primary'|'components', description, missing }
```

### 2. Smart Shopping (`shouldRecommendIngredient`)
```javascript
const result = shouldRecommendIngredient('teriyaki sauce', userInventory)
// Returns: { shouldRecommend: true/false, reason: '...' }
```

### 3. UI Explanation (`getIngredientGroupExplanation`)
```javascript
const explanation = getIngredientGroupExplanation('soy sauce', userInventory)
// Returns: "✓ Making from scratch" or null
```

## Future Enhancements

### Recipe Variants
In the future, we could automatically generate recipe variants:
- "Teriyaki Chicken (Quick Version)" → Uses bottled sauce
- "Teriyaki Chicken (From Scratch)" → Uses components

### Context-Aware Substitution
Some substitutions only work in certain contexts:
- Teriyaki sauce in marinades ✅ Can be made from components
- Teriyaki sauce for glazing ✅ Can be made from components
- Teriyaki sauce for dipping ⚠️ May need thicker consistency

### User Preferences
- "I prefer making from scratch" → Prioritize recipes with components
- "I like shortcuts" → Recommend bottled versions

## Benefits for Students

1. **Flexibility**: Work with what you have OR what's convenient
2. **Learning**: Understand what's in store-bought products
3. **Budget**: Make from scratch if you already have basics
4. **Convenience**: Buy ready-made for quick meals
5. **Transparency**: See both options, make informed choices

---

*This feature ensures students can cook efficiently whether they're budget-conscious (DIY) or time-pressed (ready-made).*

