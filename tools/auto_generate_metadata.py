#!/usr/bin/env python3
"""
Auto-Generate Recipe Metadata
Analyzes existing recipes and adds AI-friendly metadata automatically
"""

import json
import sys
from datetime import datetime
from collections import Counter

# Comprehensive keyword lists for detection
MEAT_KEYWORDS = [
    'chicken', 'beef', 'pork', 'lamb', 'turkey', 'duck', 'bacon', 'ham', 
    'sausage', 'chorizo', 'fish', 'salmon', 'tuna', 'shrimp', 'prawn', 
    'crab', 'lobster', 'anchovy', 'sardine', 'snapper', 'meat', 'steak'
]

DAIRY_KEYWORDS = [
    'milk', 'cheese', 'butter', 'cream', 'yogurt', 'yoghurt', 'ghee', 
    'parmesan', 'mozzarella', 'cheddar', 'feta', 'ricotta', 'mascarpone'
]

EGG_KEYWORDS = ['egg', 'eggs', 'yolk', 'white']

GLUTEN_KEYWORDS = [
    'flour', 'bread', 'pasta', 'noodle', 'wheat', 'barley', 'rye', 
    'couscous', 'semolina', 'breadcrumb', 'crouton'
]

SPICY_KEYWORDS = [
    'chili', 'chile', 'pepper', 'jalapeño', 'habanero', 'cayenne', 
    'paprika', 'hot sauce', 'sriracha', 'curry paste', 'red pepper flakes',
    'tabasco', 'chipotle', 'serrano', 'thai chili', 'bird\'s eye'
]

ALLERGEN_MAP = {
    'dairy': DAIRY_KEYWORDS,
    'eggs': EGG_KEYWORDS,
    'fish': ['fish', 'salmon', 'tuna', 'cod', 'anchovy', 'sardine'],
    'shellfish': ['shrimp', 'prawn', 'crab', 'lobster', 'clam', 'mussel', 'oyster'],
    'tree_nuts': ['almond', 'walnut', 'pecan', 'cashew', 'pistachio', 'hazelnut'],
    'peanuts': ['peanut', 'peanuts', 'peanut butter'],
    'soy': ['soy sauce', 'tofu', 'tempeh', 'edamame', 'miso'],
    'wheat': ['flour', 'bread', 'pasta', 'wheat']
}

CUISINE_KEYWORDS = {
    'italian': ['pasta', 'pizza', 'parmesan', 'mozzarella', 'basil', 'oregano', 'marinara'],
    'mexican': ['taco', 'burrito', 'salsa', 'guacamole', 'tortilla', 'jalapeño', 'cilantro', 'lime'],
    'chinese': ['soy sauce', 'ginger', 'sesame oil', 'rice wine', 'wok', 'stir fry', 'bok choy'],
    'indian': ['curry', 'garam masala', 'turmeric', 'cumin', 'coriander', 'naan', 'basmati'],
    'thai': ['thai', 'lemongrass', 'fish sauce', 'galangal', 'kaffir lime', 'basil', 'coconut milk'],
    'japanese': ['sushi', 'sake', 'miso', 'dashi', 'nori', 'wasabi', 'soy sauce', 'teriyaki'],
    'greek': ['feta', 'olive oil', 'lemon', 'oregano', 'tzatziki', 'pita'],
    'french': ['baguette', 'brie', 'croissant', 'burgundy', 'provençal'],
    'american': ['burger', 'bbq', 'fried chicken', 'mac and cheese', 'cornbread']
}


def get_ingredient_text(recipe):
    """Get all ingredients as lowercase text."""
    return ' '.join(recipe.get('ingredients', [])).lower()


def detect_dietary_flags(recipe):
    """Auto-detect dietary flags from ingredients."""
    ing_text = get_ingredient_text(recipe)
    
    has_meat = any(meat in ing_text for meat in MEAT_KEYWORDS)
    has_dairy = any(dairy in ing_text for dairy in DAIRY_KEYWORDS)
    has_eggs = any(egg in ing_text for egg in EGG_KEYWORDS)
    has_gluten = any(gluten in ing_text for gluten in GLUTEN_KEYWORDS)
    
    return {
        'is_vegetarian': not has_meat,
        'is_vegan': not has_meat and not has_dairy and not has_eggs,
        'is_gluten_free': not has_gluten
    }


def detect_allergens(recipe):
    """Detect common allergens in recipe."""
    ing_text = get_ingredient_text(recipe)
    allergens = []
    
    for allergen, keywords in ALLERGEN_MAP.items():
        if any(keyword in ing_text for keyword in keywords):
            allergens.append(allergen)
    
    return allergens


def detect_spice_level(recipe):
    """Detect spice level from ingredients."""
    ing_text = get_ingredient_text(recipe)
    recipe_name = recipe.get('name', '').lower()
    
    # Count spicy ingredients
    spicy_count = sum(1 for keyword in SPICY_KEYWORDS if keyword in ing_text or keyword in recipe_name)
    
    if spicy_count == 0:
        return None
    elif spicy_count <= 1:
        return 'mild'
    elif spicy_count <= 2:
        return 'medium'
    else:
        return 'hot'


def detect_primary_flavors(recipe):
    """Detect primary flavor profile."""
    ing_text = get_ingredient_text(recipe)
    recipe_name = recipe.get('name', '').lower()
    combined = ing_text + ' ' + recipe_name
    
    flavors = []
    
    # Spicy
    if any(keyword in combined for keyword in SPICY_KEYWORDS):
        flavors.append('spicy')
    
    # Sweet
    sweet_keywords = ['sugar', 'honey', 'maple', 'chocolate', 'vanilla', 'caramel', 'fruit', 'berry']
    if any(keyword in combined for keyword in sweet_keywords):
        flavors.append('sweet')
    
    # Savory
    savory_keywords = ['meat', 'broth', 'stock', 'roast', 'grilled', 'fried']
    if any(keyword in combined for keyword in savory_keywords):
        flavors.append('savory')
    
    # Tangy
    tangy_keywords = ['lemon', 'lime', 'vinegar', 'citrus', 'orange', 'tomato']
    if any(keyword in combined for keyword in tangy_keywords):
        flavors.append('tangy')
    
    # Umami
    umami_keywords = ['soy sauce', 'mushroom', 'parmesan', 'miso', 'anchovy', 'tomato paste']
    if any(keyword in combined for keyword in umami_keywords):
        flavors.append('umami')
    
    # Default to savory if nothing detected
    if not flavors:
        if recipe.get('category') == 'dessert':
            flavors.append('sweet')
        else:
            flavors.append('savory')
    
    return flavors[:3]  # Max 3 primary flavors


def detect_intensity(recipe, primary_flavors):
    """Detect flavor intensity."""
    if 'spicy' in primary_flavors:
        spice_level = detect_spice_level(recipe)
        if spice_level in ['medium', 'hot']:
            return 'bold'
    
    # Check for strong flavors
    ing_text = get_ingredient_text(recipe)
    bold_keywords = ['curry', 'garlic', 'ginger', 'onion', 'hot', 'strong']
    
    if any(keyword in ing_text for keyword in bold_keywords):
        return 'moderate'
    
    return 'mild'


def detect_cuisine(recipe):
    """Detect cuisine type from ingredients and name."""
    ing_text = get_ingredient_text(recipe)
    recipe_name = recipe.get('name', '').lower()
    combined = ing_text + ' ' + recipe_name
    
    # Check explicit cuisine field first
    if recipe.get('cuisine'):
        return recipe['cuisine'].lower()
    
    # Detect from keywords
    cuisine_scores = {}
    for cuisine, keywords in CUISINE_KEYWORDS.items():
        score = sum(1 for keyword in keywords if keyword in combined)
        if score > 0:
            cuisine_scores[cuisine] = score
    
    if cuisine_scores:
        # Return cuisine with highest score
        return max(cuisine_scores, key=cuisine_scores.get).capitalize()
    
    return None


def generate_tags(recipe, dietary_flags, spice_level, detected_cuisine):
    """Generate relevant tags for recipe."""
    tags = set(recipe.get('tags', []))  # Keep existing tags
    
    # Dietary tags
    if dietary_flags['is_vegan']:
        tags.add('vegan')
    if dietary_flags['is_vegetarian']:
        tags.add('vegetarian')
    if dietary_flags['is_gluten_free']:
        tags.add('gluten-free')
    
    # Time-based tags
    total_time = recipe.get('total_time', 0)
    if total_time <= 15:
        tags.add('quick')
        tags.add('15-minutes')
    elif total_time <= 30:
        tags.add('quick')
        tags.add('30-minutes')
    
    # Difficulty tags
    difficulty = recipe.get('difficulty', 'medium')
    if difficulty == 'easy':
        tags.add('easy')
        tags.add('beginner-friendly')
    
    # Spice tags
    if spice_level:
        tags.add('spicy')
    
    # Category tags
    category = recipe.get('category', '')
    if category:
        tags.add(category)
    
    # Cuisine tags
    if detected_cuisine:
        tags.add(detected_cuisine.lower())
    
    # Meal type (from recipe name)
    recipe_name = recipe.get('name', '').lower()
    if any(word in recipe_name for word in ['breakfast', 'pancake', 'waffle', 'toast', 'omelette']):
        tags.add('breakfast')
    elif any(word in recipe_name for word in ['dinner', 'supper']):
        tags.add('dinner')
    elif any(word in recipe_name for word in ['lunch', 'sandwich']):
        tags.add('lunch')
    elif any(word in recipe_name for word in ['dessert', 'cake', 'cookie', 'pie']):
        tags.add('dessert')
    
    return sorted(list(tags))


def enhance_recipe(recipe):
    """Add metadata to a single recipe."""
    # Detect all metadata
    dietary_flags = detect_dietary_flags(recipe)
    allergens = detect_allergens(recipe)
    spice_level = detect_spice_level(recipe)
    primary_flavors = detect_primary_flavors(recipe)
    intensity = detect_intensity(recipe, primary_flavors)
    detected_cuisine = detect_cuisine(recipe)
    tags = generate_tags(recipe, dietary_flags, spice_level, detected_cuisine)
    
    # Add to recipe (don't overwrite if exists)
    if 'dietary_flags' not in recipe:
        recipe['dietary_flags'] = dietary_flags
    
    if 'allergens' not in recipe:
        recipe['allergens'] = allergens
    
    if spice_level and 'spiceLevel' not in recipe:
        recipe['spiceLevel'] = spice_level
    
    if 'flavor_profile' not in recipe:
        recipe['flavor_profile'] = {
            'primary_flavors': primary_flavors,
            'intensity': intensity
        }
    
    # Update cuisine if detected and not set
    if detected_cuisine and not recipe.get('cuisine'):
        recipe['cuisine'] = detected_cuisine
    
    # Merge tags (keep existing + add new)
    recipe['tags'] = tags
    
    return recipe


def main():
    # Load recipes
    recipes_path = 'backend/data/recipes.json'
    
    print("=" * 60)
    print("AUTO-GENERATING RECIPE METADATA")
    print("=" * 60)
    
    try:
        with open(recipes_path, 'r', encoding='utf-8') as f:
            recipes = json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: {recipes_path} not found!")
        sys.exit(1)
    
    print(f"\n📚 Loaded {len(recipes)} recipes")
    
    # Create backup
    backup_path = f'backend/data/recipes.backup.{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(backup_path, 'w', encoding='utf-8') as f:
        json.dump(recipes, f, indent=2, ensure_ascii=False)
    print(f"💾 Backup created: {backup_path}")
    
    # Statistics
    stats = {
        'total': len(recipes),
        'vegan': 0,
        'vegetarian': 0,
        'gluten_free': 0,
        'spicy': 0,
        'cuisines': Counter(),
        'allergens': Counter()
    }
    
    # Process each recipe
    print(f"\n🔄 Processing recipes...")
    for i, recipe in enumerate(recipes, 1):
        if i % 50 == 0:
            print(f"   Processed {i}/{len(recipes)} recipes...")
        
        enhance_recipe(recipe)
        
        # Update stats
        if recipe.get('dietary_flags', {}).get('is_vegan'):
            stats['vegan'] += 1
        if recipe.get('dietary_flags', {}).get('is_vegetarian'):
            stats['vegetarian'] += 1
        if recipe.get('dietary_flags', {}).get('is_gluten_free'):
            stats['gluten_free'] += 1
        if recipe.get('spiceLevel'):
            stats['spicy'] += 1
        if recipe.get('cuisine'):
            stats['cuisines'][recipe['cuisine']] += 1
        for allergen in recipe.get('allergens', []):
            stats['allergens'][allergen] += 1
    
    print(f"✅ All {len(recipes)} recipes processed!")
    
    # Save enhanced recipes
    with open(recipes_path, 'w', encoding='utf-8') as f:
        json.dump(recipes, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Enhanced recipes saved to {recipes_path}")
    
    # Print statistics
    print("\n" + "=" * 60)
    print("METADATA GENERATION REPORT")
    print("=" * 60)
    
    print(f"\n📊 Dietary Distribution:")
    print(f"   Vegan: {stats['vegan']} ({stats['vegan']/stats['total']*100:.1f}%)")
    print(f"   Vegetarian: {stats['vegetarian']} ({stats['vegetarian']/stats['total']*100:.1f}%)")
    print(f"   Gluten-Free: {stats['gluten_free']} ({stats['gluten_free']/stats['total']*100:.1f}%)")
    print(f"   Spicy: {stats['spicy']} ({stats['spicy']/stats['total']*100:.1f}%)")
    
    print(f"\n🌍 Top Cuisines:")
    for cuisine, count in stats['cuisines'].most_common(10):
        print(f"   {cuisine}: {count} recipes")
    
    print(f"\n⚠️  Common Allergens:")
    for allergen, count in stats['allergens'].most_common():
        print(f"   {allergen}: {count} recipes")
    
    print("\n" + "=" * 60)
    print("✅ METADATA GENERATION COMPLETE!")
    print("=" * 60)
    print(f"\n🎯 Next Steps:")
    print(f"   1. Review the changes in {recipes_path}")
    print(f"   2. Test filtering with 'vegan', 'spicy', 'quick', etc.")
    print(f"   3. Manually refine metadata for top recipes")
    print(f"   4. Backup saved at: {backup_path}")
    print()


if __name__ == '__main__':
    main()
