#!/usr/bin/env python3
"""
Test ingredient classification on a single recipe

Usage:
    python classify_single_recipe.py "Recipe Name"
    python classify_single_recipe.py --recipe-id "recipe_001"
"""

import json
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent.parent.parent / 'backend'
sys.path.insert(0, str(backend_path))

from scraper.classify_ingredients import classify_recipe_ingredients


def load_recipes():
    """Load recipes from database"""
    recipes_file = backend_path / 'data' / 'recipes.json'
    with open(recipes_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def find_recipe(recipes, search_term=None, recipe_id=None):
    """Find recipe by name or ID"""
    if recipe_id:
        return next((r for r in recipes if r.get('id') == recipe_id), None)
    
    if search_term:
        search_lower = search_term.lower()
        return next((r for r in recipes if search_lower in r.get('name', '').lower()), None)
    
    return None


def display_classification(recipe):
    """Pretty print classification results"""
    print(f"\n{'='*70}")
    print(f"Recipe: {recipe['name']}")
    print(f"ID: {recipe.get('id', 'N/A')}")
    print(f"Category: {recipe.get('category', 'N/A')}")
    print(f"Cuisine: {recipe.get('cuisine', 'N/A')}")
    print(f"{'='*70}\n")
    
    structured = recipe.get('ingredients_structured', [])
    
    if not structured:
        print("❌ No structured ingredients found!")
        return
    
    # Group by role
    main = [ing for ing in structured if ing.get('role') == 'main']
    secondary = [ing for ing in structured if ing.get('role') == 'secondary']
    optional = [ing for ing in structured if ing.get('role') == 'optional']
    
    print(f"📊 Classification Summary:")
    print(f"  Main: {len(main)}")
    print(f"  Secondary: {len(secondary)}")
    print(f"  Optional: {len(optional)}")
    print(f"  Total: {len(structured)}\n")
    
    # Display main ingredients
    if main:
        print(f"🔵 MAIN INGREDIENTS ({len(main)}):")
        for ing in main:
            score = ing.get('_score', 'N/A')
            print(f"  • {ing['original']}")
            print(f"    └─ Item: {ing['item']}, Category: {ing['category']}, Score: {score}")
        print()
    
    # Display secondary ingredients
    if secondary:
        print(f"⚪ SECONDARY INGREDIENTS ({len(secondary)}):")
        for ing in secondary:
            score = ing.get('_score', 'N/A')
            print(f"  • {ing['original']}")
            print(f"    └─ Item: {ing['item']}, Category: {ing['category']}, Score: {score}")
        print()
    
    # Display optional ingredients
    if optional:
        print(f"⚫ OPTIONAL INGREDIENTS ({len(optional)}):")
        for ing in optional:
            score = ing.get('_score', 'N/A')
            print(f"  • {ing['original']}")
            print(f"    └─ Item: {ing['item']}, Category: {ing['category']}, Score: {score}")
        print()
    
    # Detailed breakdown
    print(f"{'='*70}")
    print(f"DETAILED BREAKDOWN (Position Order):")
    print(f"{'='*70}\n")
    print(f"{'Pos':<4} {'Role':<10} {'Score':<6} {'Amount':<15} {'Item':<30} {'Category':<12}")
    print(f"{'-'*70}")
    
    for i, ing in enumerate(structured):
        pos = ing.get('_position', i)
        role = ing.get('role', 'N/A')
        score = ing.get('_score', 'N/A')
        amount = ing.get('amount', 'N/A')[:15]
        item = ing.get('item', 'N/A')[:30]
        category = ing.get('category', 'N/A')[:12]
        
        # Color code by role
        role_symbol = {
            'main': '🔵',
            'secondary': '⚪',
            'optional': '⚫'
        }.get(role, ' ')
        
        print(f"{pos:<4} {role_symbol} {role:<10} {score:<6} {amount:<15} {item:<30} {category:<12}")


def test_with_mock_recipe():
    """Test with a mock recipe for development"""
    mock_recipe = {
        'id': 'test_001',
        'name': 'Test Chocolate Chip Cookies',
        'ingredients': [
            '2 1/4 cups all-purpose flour',
            '1 teaspoon baking soda',
            '1 teaspoon salt',
            '1 cup butter, softened',
            '3/4 cup granulated sugar',
            '3/4 cup packed brown sugar',
            '1 teaspoon vanilla extract',
            '2 large eggs',
            '2 cups chocolate chips',
            'Optional: chopped nuts for topping'
        ],
        'category': 'dessert',
        'cuisine': 'American'
    }
    
    print("\n🧪 Testing with mock recipe...\n")
    classified = classify_recipe_ingredients(mock_recipe, include_debug=True)
    display_classification(classified)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Test ingredient classification on a single recipe')
    parser.add_argument('recipe_name', nargs='?', help='Recipe name to search for')
    parser.add_argument('--recipe-id', help='Recipe ID to lookup')
    parser.add_argument('--test', action='store_true', help='Run with mock test recipe')
    args = parser.parse_args()
    
    if args.test:
        test_with_mock_recipe()
        return
    
    if not args.recipe_name and not args.recipe_id:
        print("Error: Please provide recipe name or --recipe-id")
        print("\nUsage:")
        print("  python classify_single_recipe.py \"French Toast\"")
        print("  python classify_single_recipe.py --recipe-id recipe_001")
        print("  python classify_single_recipe.py --test")
        sys.exit(1)
    
    # Load recipes
    print("📖 Loading recipes...")
    recipes = load_recipes()
    print(f"✅ Loaded {len(recipes)} recipes\n")
    
    # Find recipe
    recipe = find_recipe(recipes, search_term=args.recipe_name, recipe_id=args.recipe_id)
    
    if not recipe:
        print(f"❌ Recipe not found!")
        print(f"\nSearched for: {args.recipe_name or args.recipe_id}")
        print(f"\nTip: Try a partial name like 'french' or 'pasta'")
        sys.exit(1)
    
    # If recipe doesn't have structured ingredients, classify it
    if 'ingredients_structured' not in recipe:
        print("⚠️  Recipe not yet classified. Classifying now...\n")
        recipe = classify_recipe_ingredients(recipe, include_debug=True)
    
    # Display results
    display_classification(recipe)
    
    print(f"\n{'='*70}")
    print(f"💡 TIP: Adjust MAIN_THRESHOLD in classify_ingredients.py to tune classification")
    print(f"{'='*70}\n")


if __name__ == '__main__':
    main()

