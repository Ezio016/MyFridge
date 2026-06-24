#!/usr/bin/env python3
"""
Migration script to move recipes from JSON to database.

This script:
1. Reads recipes.json
2. Extracts unique ingredients -> ingredients table
3. Inserts recipes -> recipes table
4. Links recipe-ingredient relationships -> recipe_ingredients
5. Computes and stores ingredient vectors -> recipe_vectors
6. Computes and stores flavor profiles -> recipe_flavor_profiles
7. Populates ingredient flavors from INGREDIENT_FLAVORS dict -> ingredient_flavors

Run from backend directory:
    python -m scripts.migrate_to_db
"""

import json
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.database import engine, Base, SessionLocal
from app.models import (
    Recipe, RecipeVector, RecipeFlavorProfile,
    Ingredient, IngredientFlavor, RecipeIngredient
)

# Import flavor data from existing service
from app.services.flavor_matrix import INGREDIENT_FLAVORS, FLAVOR_DIMENSIONS


# Standard ingredients for vector representation (same as recipe_lab.py)
STANDARD_INGREDIENTS = [
    "chicken", "beef", "pork", "fish", "eggs", "tofu",
    "milk", "butter", "cheese", "cream",
    "onion", "garlic", "tomato", "potato", "carrot",
    "pepper", "mushroom", "spinach", "broccoli", "zucchini",
    "rice", "pasta", "bread", "flour", "noodles",
    "olive oil", "vegetable oil", "sesame oil",
    "salt", "sugar", "soy sauce", "vinegar", "lemon",
    "basil", "parsley", "cilantro", "thyme", "oregano",
    "cumin", "paprika", "chili", "ginger", "garlic powder"
]

COOKING_METHODS = [
    "fry", "sauté", "stir-fry", "boil", "simmer", "steam",
    "bake", "roast", "grill", "broil", "poach", "braise"
]


def ingredient_to_vector(ingredients_list: list[str]) -> list[int]:
    """Convert ingredient list to binary vector."""
    vector = [0] * len(STANDARD_INGREDIENTS)
    for ing in ingredients_list:
        ing_lower = ing.lower()
        for i, std_ing in enumerate(STANDARD_INGREDIENTS):
            if std_ing in ing_lower:
                vector[i] = 1
                break
    return vector


def extract_cooking_methods(instructions: list[str]) -> list[int]:
    """Extract cooking methods from instructions as binary vector."""
    text = " ".join(instructions).lower() if instructions else ""
    vector = [0] * len(COOKING_METHODS)
    for i, method in enumerate(COOKING_METHODS):
        if method in text:
            vector[i] = 1
    return vector


def calculate_flavor_profile(ingredients: list[str]) -> dict:
    """Calculate flavor profile for a recipe."""
    total_vector = [0.0] * len(FLAVOR_DIMENSIONS)
    
    for ing in ingredients:
        ing_lower = ing.lower()
        # Find matching flavor
        for key, flavor_vec in INGREDIENT_FLAVORS.items():
            if key in ing_lower:
                for i in range(len(FLAVOR_DIMENSIONS)):
                    total_vector[i] += flavor_vec[i]
                break
    
    # Normalize to 0-1 range
    max_val = max(total_vector) if max(total_vector) > 0 else 1
    normalized = [round(v / max_val, 3) for v in total_vector]
    
    # Find dominant flavors
    flavor_scores = list(zip(FLAVOR_DIMENSIONS, normalized))
    flavor_scores.sort(key=lambda x: x[1], reverse=True)
    dominant = [f for f, s in flavor_scores[:3] if s > 0.3]
    
    # Generate description
    descriptions = []
    for flavor, score in flavor_scores:
        if score >= 0.7:
            descriptions.append(f"very {flavor}")
        elif score >= 0.4:
            descriptions.append(flavor)
    
    description = ", ".join(descriptions[:4]) if descriptions else "balanced, mild"
    
    return {
        "normalized": normalized,
        "dominant": dominant,
        "description": description,
    }


def parse_ingredient(ing_str: str) -> dict:
    """Parse an ingredient string into components."""
    parts = ing_str.strip().split()
    
    # Try to extract amount (first part that looks like a number)
    amount = None
    name_start = 0
    
    if parts and (parts[0].replace('.', '').replace('/', '').replace('-', '').isdigit() 
                  or parts[0] in ['a', 'an']):
        amount = parts[0]
        name_start = 1
        
        # Check for unit
        if len(parts) > 1 and parts[1].lower() in [
            'cup', 'cups', 'tbsp', 'tsp', 'oz', 'lb', 'lbs', 'pound', 'pounds',
            'teaspoon', 'tablespoon', 'ounce', 'ounces', 'gram', 'grams', 'g',
            'kg', 'ml', 'liter', 'liters', 'can', 'cans', 'clove', 'cloves',
            'piece', 'pieces', 'slice', 'slices', 'bunch', 'head', 'pinch'
        ]:
            amount = f"{amount} {parts[1]}"
            name_start = 2
    
    name = " ".join(parts[name_start:]) if name_start < len(parts) else ing_str
    
    return {
        "amount": amount,
        "name": name.lower(),
        "original": ing_str,
    }


def identify_ingredient_key(name: str) -> str | None:
    """Find the standard ingredient key that matches this name."""
    name_lower = name.lower()
    for key in INGREDIENT_FLAVORS.keys():
        if key in name_lower or name_lower in key:
            return key
    return None


def migrate_recipes(db: Session, recipes_path: str):
    """Migrate recipes from JSON to database."""
    print(f"Loading recipes from {recipes_path}...")
    
    with open(recipes_path, 'r') as f:
        recipes_data = json.load(f)
    
    print(f"Found {len(recipes_data)} recipes")
    
    # First pass: collect all unique ingredients
    print("\n1. Collecting unique ingredients...")
    ingredient_names = set()
    for recipe in recipes_data:
        for ing in recipe.get('ingredients', []):
            parsed = parse_ingredient(ing)
            key = identify_ingredient_key(parsed['name'])
            if key:
                ingredient_names.add(key)
            else:
                # Use first word as fallback
                first_word = parsed['name'].split()[0] if parsed['name'] else None
                if first_word and len(first_word) > 2:
                    ingredient_names.add(first_word)
    
    print(f"   Found {len(ingredient_names)} unique ingredient keys")
    
    # Create ingredients in database
    print("\n2. Creating ingredients table...")
    ingredient_map = {}  # name -> Ingredient object
    
    for name in ingredient_names:
        # Check if already exists
        existing = db.query(Ingredient).filter(Ingredient.name == name).first()
        if existing:
            ingredient_map[name] = existing
            continue
        
        ing = Ingredient(
            name=name,
            category=get_ingredient_category(name),
            is_common=name in ['salt', 'pepper', 'oil', 'butter', 'garlic', 'onion']
        )
        db.add(ing)
        ingredient_map[name] = ing
    
    db.commit()
    print(f"   Created {len(ingredient_map)} ingredients")
    
    # Create ingredient flavors
    print("\n3. Creating ingredient flavors...")
    for name, ing in ingredient_map.items():
        if name in INGREDIENT_FLAVORS:
            vec = INGREDIENT_FLAVORS[name]
            flavor = IngredientFlavor(
                ingredient_id=ing.id,
                sweet=vec[0], salty=vec[1], sour=vec[2], bitter=vec[3],
                umami=vec[4], spicy=vec[5], fatty=vec[6], aromatic=vec[7]
            )
            db.add(flavor)
    
    db.commit()
    print("   Done creating ingredient flavors")
    
    # Create recipes
    print("\n4. Migrating recipes...")
    recipes_created = 0
    
    for i, recipe_data in enumerate(recipes_data):
        if i % 100 == 0:
            print(f"   Processing recipe {i}/{len(recipes_data)}...")
        
        # Check if already exists
        external_id = recipe_data.get('id', f"recipe_{i}")
        existing = db.query(Recipe).filter(Recipe.external_id == external_id).first()
        if existing:
            continue
        
        # Create recipe
        recipe = Recipe(
            external_id=external_id,
            name=recipe_data.get('name', 'Untitled'),
            description=recipe_data.get('description'),
            prep_time=recipe_data.get('prep_time'),
            cook_time=recipe_data.get('cook_time'),
            total_time=recipe_data.get('total_time'),
            servings=recipe_data.get('servings', 4),
            difficulty=recipe_data.get('difficulty', 'medium'),
            cuisine=recipe_data.get('cuisine'),
            category=recipe_data.get('category'),
            instructions=recipe_data.get('instructions', []),
            tags=recipe_data.get('tags', []),
            image_url=recipe_data.get('image_url'),
            source=recipe_data.get('source'),
            popularity_score=recipe_data.get('popularity_score', 0),
        )
        db.add(recipe)
        db.flush()  # Get the ID
        
        # Create recipe ingredients
        ingredients_list = recipe_data.get('ingredients', [])
        main_ingredients = recipe_data.get('mainIngredients', [])
        optional_ingredients = recipe_data.get('optionalIngredients', [])
        
        for ing_str in ingredients_list:
            parsed = parse_ingredient(ing_str)
            key = identify_ingredient_key(parsed['name'])
            
            # Determine role
            role = "secondary"
            is_optional = False
            
            if ing_str in main_ingredients or any(m in ing_str for m in main_ingredients):
                role = "main"
            if ing_str in optional_ingredients or any(o in ing_str for o in optional_ingredients):
                is_optional = True
            
            # Check ingredients_structured if available
            structured = recipe_data.get('ingredients_structured', [])
            for s in structured:
                if s.get('original') == ing_str:
                    role = s.get('role', role)
                    is_optional = s.get('classification') == 'optional'
                    break
            
            recipe_ing = RecipeIngredient(
                recipe_id=recipe.id,
                ingredient_id=ingredient_map.get(key, ingredient_map.get(parsed['name'].split()[0])).id if key in ingredient_map or parsed['name'].split()[0] in ingredient_map else None,
                ingredient_name=parsed['name'],
                amount=parsed['amount'],
                original_text=ing_str,
                role=role,
                is_optional=is_optional,
            )
            db.add(recipe_ing)
        
        # Create recipe vector
        ing_vector = ingredient_to_vector(ingredients_list)
        method_vector = extract_cooking_methods(recipe_data.get('instructions', []))
        
        recipe_vec = RecipeVector(
            recipe_id=recipe.id,
            ingredient_vector=ing_vector,
            method_vector=method_vector,
        )
        db.add(recipe_vec)
        
        # Create recipe flavor profile
        flavor_data = calculate_flavor_profile(ingredients_list)
        normalized = flavor_data['normalized']
        
        recipe_flavor = RecipeFlavorProfile(
            recipe_id=recipe.id,
            sweet=normalized[0], salty=normalized[1], sour=normalized[2], bitter=normalized[3],
            umami=normalized[4], spicy=normalized[5], fatty=normalized[6], aromatic=normalized[7],
            dominant_flavors=flavor_data['dominant'],
            flavor_description=flavor_data['description'],
        )
        db.add(recipe_flavor)
        
        recipes_created += 1
        
        # Commit in batches
        if recipes_created % 100 == 0:
            db.commit()
    
    db.commit()
    print(f"\n   Created {recipes_created} recipes with vectors and flavor profiles")


def get_ingredient_category(name: str) -> str:
    """Determine category for an ingredient."""
    proteins = ['chicken', 'beef', 'pork', 'fish', 'shrimp', 'lamb', 'bacon', 'eggs', 'tofu']
    dairy = ['milk', 'butter', 'cheese', 'cream', 'yogurt', 'parmesan']
    vegetables = ['onion', 'garlic', 'tomato', 'potato', 'carrot', 'pepper', 'mushroom', 
                  'spinach', 'broccoli', 'celery', 'cabbage', 'eggplant', 'zucchini', 'avocado']
    grains = ['rice', 'pasta', 'bread', 'noodles', 'flour']
    herbs = ['basil', 'parsley', 'cilantro', 'thyme', 'oregano', 'rosemary', 'mint', 'dill']
    spices = ['cumin', 'paprika', 'chili', 'cinnamon', 'nutmeg', 'turmeric', 'curry', 'pepper']
    oils = ['olive oil', 'sesame oil', 'vegetable oil', 'coconut oil', 'butter']
    fruits = ['apple', 'banana', 'orange', 'mango', 'pineapple', 'berries', 'lemon', 'lime']
    
    if name in proteins:
        return 'protein'
    if name in dairy:
        return 'dairy'
    if name in vegetables:
        return 'vegetable'
    if name in grains:
        return 'grain'
    if name in herbs:
        return 'herb'
    if name in spices:
        return 'spice'
    if name in oils:
        return 'oil'
    if name in fruits:
        return 'fruit'
    return 'other'


def main():
    """Main migration function."""
    print("=" * 60)
    print("MyFridge Database Migration")
    print("=" * 60)
    
    # Get recipes path
    recipes_path = Path(__file__).parent.parent / "data" / "recipes.json"
    if not recipes_path.exists():
        print(f"Error: recipes.json not found at {recipes_path}")
        sys.exit(1)
    
    print(f"\nRecipes file: {recipes_path}")
    
    # Create tables
    print("\nCreating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created.")
    
    # Run migration
    db = SessionLocal()
    try:
        migrate_recipes(db, str(recipes_path))
        print("\n" + "=" * 60)
        print("Migration completed successfully!")
        print("=" * 60)
        
        # Print stats
        recipe_count = db.query(Recipe).count()
        ingredient_count = db.query(Ingredient).count()
        vector_count = db.query(RecipeVector).count()
        flavor_count = db.query(RecipeFlavorProfile).count()
        
        print(f"\nDatabase stats:")
        print(f"  - Recipes: {recipe_count}")
        print(f"  - Ingredients: {ingredient_count}")
        print(f"  - Recipe Vectors: {vector_count}")
        print(f"  - Flavor Profiles: {flavor_count}")
        
    except Exception as e:
        print(f"\nError during migration: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
