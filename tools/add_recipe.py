#!/usr/bin/env python3
"""
Recipe Management Tool
Add and validate recipes for MyFridge database
"""

import json
import sys
import os
from datetime import datetime

# Add parent directory to path to import classify_ingredients
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend', 'scraper'))
from classify_ingredients import classify_recipe_ingredients

# Recipe schema definition
REQUIRED_FIELDS = [
    'id', 'source', 'name', 'description',
    'prep_time', 'cook_time', 'total_time', 'servings',
    'difficulty', 'ingredients', 'instructions', 'category'
]

VALID_DIFFICULTIES = ['easy', 'medium', 'hard']
VALID_CATEGORIES = ['main', 'side', 'appetizer', 'dessert', 'breakfast', 'snack', 'beverage']
VALID_ROLES = ['main', 'secondary', 'optional']
VALID_CLASSIFICATIONS = ['essential', 'common', 'optional']
VALID_ING_CATEGORIES = ['protein', 'produce', 'dairy', 'carb', 'spice', 'condiment', 'other']

def validate_recipe(recipe):
    """Validate a recipe against the schema."""
    errors = []
    warnings = []
    
    # Check required fields
    for field in REQUIRED_FIELDS:
        if field not in recipe:
            errors.append(f"Missing required field: '{field}'")
    
    if errors:
        return errors, warnings
    
    # Validate field types and values
    if not isinstance(recipe['id'], str) or not recipe['id']:
        errors.append("'id' must be a non-empty string")
    
    if not isinstance(recipe['name'], str) or len(recipe['name']) < 3:
        errors.append("'name' must be a string with at least 3 characters")
    
    if not isinstance(recipe['description'], str) or len(recipe['description']) < 20:
        warnings.append("'description' should be at least 20 characters for good SEO")
    
    # Validate timing
    if not isinstance(recipe['prep_time'], (int, float)) or recipe['prep_time'] < 0:
        errors.append("'prep_time' must be a positive number")
    
    if not isinstance(recipe['cook_time'], (int, float)) or recipe['cook_time'] < 0:
        errors.append("'cook_time' must be a positive number")
    
    if not isinstance(recipe['total_time'], (int, float)) or recipe['total_time'] < 0:
        errors.append("'total_time' must be a positive number")
    
    if recipe['total_time'] < (recipe['prep_time'] + recipe['cook_time']):
        warnings.append(f"total_time ({recipe['total_time']}) should equal prep_time ({recipe['prep_time']}) + cook_time ({recipe['cook_time']})")
    
    # Validate servings
    if not isinstance(recipe['servings'], int) or recipe['servings'] < 1:
        errors.append("'servings' must be a positive integer")
    
    # Validate difficulty
    if recipe['difficulty'] not in VALID_DIFFICULTIES:
        errors.append(f"'difficulty' must be one of: {', '.join(VALID_DIFFICULTIES)}")
    
    # Validate category
    if recipe['category'] not in VALID_CATEGORIES:
        errors.append(f"'category' must be one of: {', '.join(VALID_CATEGORIES)}")
    
    # Validate ingredients array
    if not isinstance(recipe['ingredients'], list) or len(recipe['ingredients']) == 0:
        errors.append("'ingredients' must be a non-empty array")
    
    # Validate instructions array
    if not isinstance(recipe['instructions'], list) or len(recipe['instructions']) == 0:
        errors.append("'instructions' must be a non-empty array")
    
    # Validate ingredients_structured if present
    if 'ingredients_structured' in recipe:
        if not isinstance(recipe['ingredients_structured'], list):
            errors.append("'ingredients_structured' must be an array")
        elif len(recipe['ingredients_structured']) != len(recipe['ingredients']):
            errors.append(f"'ingredients_structured' length ({len(recipe['ingredients_structured'])}) must match 'ingredients' length ({len(recipe['ingredients'])})")
        else:
            # Validate each structured ingredient
            for i, struct in enumerate(recipe['ingredients_structured']):
                if not isinstance(struct, dict):
                    errors.append(f"ingredients_structured[{i}]: must be an object")
                    continue
                
                # Check required fields
                for field in ['item', 'amount', 'original', 'role', 'classification', 'category']:
                    if field not in struct:
                        errors.append(f"ingredients_structured[{i}]: missing '{field}'")
                
                # Validate role
                if 'role' in struct and struct['role'] not in VALID_ROLES:
                    errors.append(f"ingredients_structured[{i}]: role must be one of {', '.join(VALID_ROLES)}")
                
                # Validate classification
                if 'classification' in struct and struct['classification'] not in VALID_CLASSIFICATIONS:
                    errors.append(f"ingredients_structured[{i}]: classification must be one of {', '.join(VALID_CLASSIFICATIONS)}")
                
                # Validate category
                if 'category' in struct and struct['category'] not in VALID_ING_CATEGORIES:
                    errors.append(f"ingredients_structured[{i}]: category must be one of {', '.join(VALID_ING_CATEGORIES)}")
    else:
        warnings.append("'ingredients_structured' is missing - will be auto-generated")
    
    # Check for at least a few tags
    if 'tags' not in recipe or not isinstance(recipe['tags'], list) or len(recipe['tags']) < 2:
        warnings.append("Add at least 2-3 tags for better searchability")
    
    return errors, warnings


def check_duplicate_id(recipe_id, database_path='backend/data/recipes.json'):
    """Check if recipe ID already exists in database."""
    try:
        with open(database_path, 'r', encoding='utf-8') as f:
            existing_recipes = json.load(f)
        
        for recipe in existing_recipes:
            if recipe.get('id') == recipe_id:
                return True
        return False
    except FileNotFoundError:
        return False


def add_recipe_to_database(recipe, database_path='backend/data/recipes.json'):
    """Add a recipe to the database."""
    try:
        # Load existing recipes
        with open(database_path, 'r', encoding='utf-8') as f:
            recipes = json.load(f)
        
        # Add new recipe
        recipes.append(recipe)
        
        # Save back to file
        with open(database_path, 'w', encoding='utf-8') as f:
            json.dump(recipes, f, indent=2, ensure_ascii=False)
        
        return True, f"Recipe '{recipe['name']}' added successfully!"
    except Exception as e:
        return False, f"Failed to add recipe: {str(e)}"


def auto_classify_ingredients(recipe):
    """Automatically classify ingredients using the classification algorithm."""
    if 'ingredients_structured' in recipe and len(recipe['ingredients_structured']) > 0:
        print("⚠️  Recipe already has ingredients_structured. Skipping auto-classification.")
        return recipe
    
    print("🤖 Auto-classifying ingredients...")
    
    # Prepare recipe for classification
    recipe_for_classification = {
        'name': recipe['name'],
        'ingredients': recipe['ingredients']
    }
    
    # Classify
    classified = classify_recipe_ingredients(recipe_for_classification, include_debug=False)
    
    # Add to recipe
    recipe['ingredients_structured'] = classified
    
    print(f"✅ Classified {len(classified)} ingredients")
    
    # Show summary
    main_count = sum(1 for ing in classified if ing.get('role') == 'main')
    secondary_count = sum(1 for ing in classified if ing.get('role') == 'secondary')
    optional_count = sum(1 for ing in classified if ing.get('role') == 'optional')
    
    print(f"   Main: {main_count}, Secondary: {secondary_count}, Optional: {optional_count}")
    
    return recipe


def main():
    if len(sys.argv) < 2:
        print("Usage: python add_recipe.py <recipe_file.json> [--validate-only] [--no-auto-classify]")
        print("\nOptions:")
        print("  --validate-only      Validate the recipe without adding to database")
        print("  --no-auto-classify   Don't auto-classify ingredients (must be pre-classified)")
        sys.exit(1)
    
    recipe_file = sys.argv[1]
    validate_only = '--validate-only' in sys.argv
    auto_classify = '--no-auto-classify' not in sys.argv
    
    # Load recipe
    try:
        with open(recipe_file, 'r', encoding='utf-8') as f:
            recipe = json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: File not found: {recipe_file}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON in {recipe_file}")
        print(f"   {str(e)}")
        sys.exit(1)
    
    print(f"\n{'='*60}")
    print(f"VALIDATING RECIPE: {recipe.get('name', 'Unknown')}")
    print(f"{'='*60}\n")
    
    # Validate
    errors, warnings = validate_recipe(recipe)
    
    # Show results
    if errors:
        print(f"❌ VALIDATION FAILED - {len(errors)} error(s):\n")
        for error in errors:
            print(f"  ❌ {error}")
        print()
        sys.exit(1)
    
    print("✅ VALIDATION PASSED!\n")
    
    if warnings:
        print(f"⚠️  {len(warnings)} warning(s):\n")
        for warning in warnings:
            print(f"  ⚠️  {warning}")
        print()
    
    # Auto-classify if needed
    if auto_classify and 'ingredients_structured' not in recipe:
        recipe = auto_classify_ingredients(recipe)
        print()
    
    # Show recipe summary
    print(f"📊 RECIPE SUMMARY:")
    print(f"   ID: {recipe['id']}")
    print(f"   Name: {recipe['name']}")
    print(f"   Category: {recipe['category']}")
    print(f"   Difficulty: {recipe['difficulty']}")
    print(f"   Time: {recipe['prep_time']}min prep + {recipe['cook_time']}min cook = {recipe['total_time']}min total")
    print(f"   Servings: {recipe['servings']}")
    print(f"   Ingredients: {len(recipe['ingredients'])}")
    print(f"   Instructions: {len(recipe['instructions'])} steps")
    if 'tags' in recipe:
        print(f"   Tags: {', '.join(recipe['tags'])}")
    print()
    
    if validate_only:
        print("✅ Validation complete (not added to database)")
        sys.exit(0)
    
    # Check for duplicate ID
    if check_duplicate_id(recipe['id']):
        print(f"❌ Error: Recipe ID '{recipe['id']}' already exists in database!")
        print("   Choose a different ID or remove the existing recipe first.")
        sys.exit(1)
    
    # Add popularity score if missing
    if 'popularity_score' not in recipe:
        recipe['popularity_score'] = 50.0
    
    # Add timestamp if missing
    if 'popularity_last_updated' not in recipe:
        recipe['popularity_last_updated'] = datetime.now().isoformat()
    
    # Add to database
    print("📝 Adding recipe to database...")
    success, message = add_recipe_to_database(recipe)
    
    if success:
        print(f"✅ {message}")
        print(f"\n🎉 Recipe '{recipe['name']}' is now in the database!")
    else:
        print(f"❌ {message}")
        sys.exit(1)


if __name__ == '__main__':
    main()
