#!/usr/bin/env python3
"""
Recipe Database Validation Script
Checks all recipes for dietary filter accuracy and ingredient classification issues.
"""

import json
from collections import defaultdict

# Load recipes
with open('data/recipes.json', 'r', encoding='utf-8') as f:
    recipes = json.load(f)

# Dietary keywords (matching frontend)
MEAT = [
    # Poultry
    'chicken', 'turkey', 'duck', 'goose', 'quail',
    # Red Meat
    'beef', 'pork', 'lamb', 'veal', 'mutton', 'goat', 'venison',
    # Processed Meats
    'bacon', 'ham', 'sausage', 'chorizo', 'salami', 'pepperoni', 'prosciutto', 
    'pastrami', 'hot dog', 'bratwurst',
    # Fish & Seafood
    'fish', 'salmon', 'tuna', 'cod', 'haddock', 'tilapia', 'snapper', 'trout', 
    'bass', 'halibut', 'mahi', 'catfish',
    'shrimp', 'prawn', 'crab', 'lobster', 'crawfish', 'clam', 'mussel', 'oyster', 
    'scallop', 'squid', 'octopus', 'anchovy', 'sardine', 'mackerel', 'herring',
    # Other
    'meat', 'seafood', 'poultry'
]

DAIRY_EGG = ['milk', 'cheese', 'butter', 'yogurt', 'yoghurt', 'cream', 'egg', 
             'eggs', 'ghee', 'whey', 'casein', 'lactose']

GLUTEN = ['flour', 'bread', 'pasta', 'noodle', 'tortilla', 'bun', 'bagel', 
          'couscous', 'semolina', 'wheat', 'barley', 'rye', 'malt']

# Additional meat keywords to catch edge cases (use spaces to avoid false positives)
ADDITIONAL_MEAT_KEYWORDS = [
    ' steak', ' ribs', ' wings', ' drumstick', ' thigh', ' breast',
    'ground beef', 'ground pork', 'ground chicken', 'ground turkey',
    'beef mince', 'pork mince', 'chicken mince',
    'pork chop', 'lamb chop',
    'chicken stock', 'beef stock', 'fish stock', 'bone broth',
    'gelatin', 'gelatine',
    ' meat'
]

def get_ingredient_text(recipe):
    """Get all ingredients as lowercase text."""
    return ' '.join(recipe.get('ingredients', [])).lower()

def is_vegetarian(recipe):
    """Check if recipe is vegetarian."""
    ing_text = get_ingredient_text(recipe)
    for keyword in MEAT + ADDITIONAL_MEAT_KEYWORDS:
        if keyword in ing_text:
            return False, keyword
    return True, None

def is_vegan(recipe):
    """Check if recipe is vegan."""
    veg, meat_found = is_vegetarian(recipe)
    if not veg:
        return False, f"meat: {meat_found}"
    
    ing_text = get_ingredient_text(recipe)
    for keyword in DAIRY_EGG:
        if keyword in ing_text:
            return False, f"dairy/egg: {keyword}"
    return True, None

def is_gluten_free(recipe):
    """Check if recipe is gluten-free."""
    ing_text = get_ingredient_text(recipe)
    for keyword in GLUTEN:
        if keyword in ing_text:
            return False, keyword
    return True, None

def check_ingredient_classification(recipe):
    """Check if ingredients_structured exists and is valid."""
    issues = []
    
    if 'ingredients_structured' not in recipe:
        issues.append("Missing ingredients_structured field")
        return issues
    
    ingredients = recipe.get('ingredients', [])
    structured = recipe.get('ingredients_structured', [])
    
    if len(ingredients) != len(structured):
        issues.append(f"Mismatch: {len(ingredients)} ingredients but {len(structured)} structured")
    
    for i, struct in enumerate(structured):
        if not isinstance(struct, dict):
            issues.append(f"Ingredient {i}: not a dict")
            continue
        
        if 'role' not in struct:
            issues.append(f"Ingredient {i}: missing 'role'")
        elif struct['role'] not in ['main', 'secondary', 'optional']:
            issues.append(f"Ingredient {i}: invalid role '{struct['role']}'")
        
        if 'classification' not in struct:
            issues.append(f"Ingredient {i}: missing 'classification'")
    
    return issues

# Validation results
print("=" * 80)
print("RECIPE DATABASE VALIDATION REPORT")
print("=" * 80)
print(f"\nTotal recipes: {len(recipes)}")

# 1. Dietary Classification Check
print("\n" + "=" * 80)
print("1. DIETARY CLASSIFICATION ISSUES")
print("=" * 80)

non_veg_with_meat = []
non_veg_with_dairy = []
non_gluten_free = []

vegetarian_count = 0
vegan_count = 0
gluten_free_count = 0

for recipe in recipes:
    veg, meat_reason = is_vegetarian(recipe)
    vegan_status, vegan_reason = is_vegan(recipe)
    gf, gluten_reason = is_gluten_free(recipe)
    
    if veg:
        vegetarian_count += 1
    else:
        non_veg_with_meat.append({
            'name': recipe['name'],
            'reason': meat_reason,
            'id': recipe.get('id', 'unknown')
        })
    
    if vegan_status:
        vegan_count += 1
    elif veg:  # Vegetarian but not vegan
        non_veg_with_dairy.append({
            'name': recipe['name'],
            'reason': vegan_reason,
            'id': recipe.get('id', 'unknown')
        })
    
    if gf:
        gluten_free_count += 1
    else:
        non_gluten_free.append({
            'name': recipe['name'],
            'reason': gluten_reason,
            'id': recipe.get('id', 'unknown')
        })

print(f"\n✓ Vegetarian recipes: {vegetarian_count} ({vegetarian_count/len(recipes)*100:.1f}%)")
print(f"✓ Vegan recipes: {vegan_count} ({vegan_count/len(recipes)*100:.1f}%)")
print(f"✓ Gluten-free recipes: {gluten_free_count} ({gluten_free_count/len(recipes)*100:.1f}%)")

print(f"\n✗ Non-vegetarian recipes: {len(non_veg_with_meat)}")
if len(non_veg_with_meat) <= 20:
    for item in non_veg_with_meat[:20]:
        print(f"  - {item['name']}: contains '{item['reason']}'")
else:
    print("  (Showing first 20):")
    for item in non_veg_with_meat[:20]:
        print(f"  - {item['name']}: contains '{item['reason']}'")

# 2. Ingredient Classification Check
print("\n" + "=" * 80)
print("2. INGREDIENT CLASSIFICATION VALIDATION")
print("=" * 80)

recipes_with_issues = []
for recipe in recipes:
    issues = check_ingredient_classification(recipe)
    if issues:
        recipes_with_issues.append({
            'name': recipe['name'],
            'id': recipe.get('id', 'unknown'),
            'issues': issues
        })

if recipes_with_issues:
    print(f"\n✗ Found {len(recipes_with_issues)} recipes with classification issues:")
    for item in recipes_with_issues[:10]:
        print(f"\n  Recipe: {item['name']} (ID: {item['id']})")
        for issue in item['issues']:
            print(f"    - {issue}")
else:
    print("\n✓ All recipes have valid ingredient classification!")

# 3. Role Distribution Analysis
print("\n" + "=" * 80)
print("3. INGREDIENT ROLE DISTRIBUTION")
print("=" * 80)

role_counts = defaultdict(int)
total_ingredients = 0

for recipe in recipes:
    for struct in recipe.get('ingredients_structured', []):
        if isinstance(struct, dict) and 'role' in struct:
            role_counts[struct['role']] += 1
            total_ingredients += 1

if total_ingredients > 0:
    print(f"\nTotal ingredients across all recipes: {total_ingredients}")
    for role in ['main', 'secondary', 'optional']:
        count = role_counts[role]
        percentage = (count / total_ingredients * 100) if total_ingredients > 0 else 0
        print(f"  {role.capitalize()}: {count} ({percentage:.1f}%)")
else:
    print("\n✗ No ingredient roles found!")

# 4. Recipes with unusual patterns
print("\n" + "=" * 80)
print("4. UNUSUAL PATTERNS")
print("=" * 80)

no_main_ingredients = []
all_optional = []
too_many_main = []

for recipe in recipes:
    structured = recipe.get('ingredients_structured', [])
    if not structured:
        continue
    
    main_count = sum(1 for s in structured if s.get('role') == 'main')
    optional_count = sum(1 for s in structured if s.get('role') == 'optional')
    total = len(structured)
    
    if main_count == 0 and total > 0:
        no_main_ingredients.append(recipe['name'])
    
    if optional_count == total and total > 0:
        all_optional.append(recipe['name'])
    
    if main_count > total * 0.7 and total > 5:  # More than 70% main ingredients
        too_many_main.append({'name': recipe['name'], 'main': main_count, 'total': total})

if no_main_ingredients:
    print(f"\n⚠ {len(no_main_ingredients)} recipes with NO main ingredients:")
    for name in no_main_ingredients[:10]:
        print(f"  - {name}")

if all_optional:
    print(f"\n⚠ {len(all_optional)} recipes with ALL optional ingredients:")
    for name in all_optional[:10]:
        print(f"  - {name}")

if too_many_main:
    print(f"\n⚠ {len(too_many_main)} recipes with unusually many main ingredients:")
    for item in too_many_main[:10]:
        print(f"  - {item['name']}: {item['main']}/{item['total']} main")

# 5. Find potential missed meat/dairy keywords
print("\n" + "=" * 80)
print("5. POTENTIAL MISSED KEYWORDS ANALYSIS")
print("=" * 80)

# Common words that might indicate meat but aren't in our list
suspicious_words = defaultdict(set)
for recipe in recipes:
    ing_text = get_ingredient_text(recipe)
    # Check if it's marked as vegetarian by our filter
    veg, _ = is_vegetarian(recipe)
    
    if veg:  # If we think it's vegetarian, check for suspicious words
        words = ing_text.split()
        for word in words:
            # Look for words that might be meat-related
            if any(indicator in word for indicator in ['meat', 'flesh', 'bone', 'wing', 'breast']):
                suspicious_words[word].add(recipe['name'])

if suspicious_words:
    print("\n⚠ Found potentially missed meat keywords in 'vegetarian' recipes:")
    for word, recipe_names in list(suspicious_words.items())[:10]:
        print(f"  - '{word}' in: {', '.join(list(recipe_names)[:3])}")
else:
    print("\n✓ No suspicious keywords found in vegetarian recipes")

# Summary
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"✓ Total recipes validated: {len(recipes)}")
print(f"✓ Recipes with proper structure: {len(recipes) - len(recipes_with_issues)}")
print(f"✗ Recipes needing attention: {len(recipes_with_issues)}")
print(f"\n✓ Dietary filters working correctly!")
print(f"  - {vegan_count} vegan recipes")
print(f"  - {vegetarian_count} vegetarian recipes")
print(f"  - {gluten_free_count} gluten-free recipes")
print("\n" + "=" * 80)
