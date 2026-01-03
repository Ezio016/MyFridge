#!/usr/bin/env python3
"""
Add popularity scores to all recipes in the database.

Popularity is calculated based on:
1. Recipe source (TheMealDB, BBC Food, etc. have different base scores)
2. Recipe completeness (has description, tags, image, etc.)
3. Cooking time (quicker recipes get a slight boost)
4. Ingredient count (not too simple, not too complex)
"""

import json
import os
from pathlib import Path

def calculate_popularity_score(recipe):
    """Calculate a popularity score (0-100) for a recipe."""
    score = 0.0
    
    # 1. Base score by source (40 points max)
    source = recipe.get('source', '').lower()
    source_scores = {
        'themealdb': 35,      # Popular, well-tested recipes
        'bbc food': 32,       # High quality, trusted source
        'epicurious': 30,     # Professional recipes
        'food.com': 25,       # Community recipes
        'myfridge': 20,       # Our curated recipes
        'recipe puppy': 15,   # Aggregated recipes
    }
    
    for source_key, source_score in source_scores.items():
        if source_key in source:
            score += source_score
            break
    else:
        score += 10  # Unknown source gets base score
    
    # 2. Recipe completeness (30 points max)
    completeness = 0
    
    # Has description
    if recipe.get('description') and len(recipe.get('description', '')) > 20:
        completeness += 5
    
    # Has tags
    if recipe.get('tags') and len(recipe.get('tags', [])) > 0:
        completeness += 5
    
    # Has image
    if recipe.get('image'):
        completeness += 5
    
    # Has detailed instructions
    instructions = recipe.get('instructions', [])
    if instructions and len(instructions) >= 3:
        completeness += 5
    
    # Has reasonable number of ingredients (not too few, not too many)
    ingredients = recipe.get('ingredients', [])
    if 3 <= len(ingredients) <= 15:
        completeness += 5
    elif len(ingredients) > 15:
        completeness += 2  # Complex recipes get partial credit
    
    # Has timing info
    if recipe.get('total_time') or (recipe.get('prep_time') and recipe.get('cook_time')):
        completeness += 5
    
    score += completeness
    
    # 3. Cooking time bonus (15 points max)
    total_time = recipe.get('total_time', 0)
    if not total_time:
        total_time = (recipe.get('prep_time', 0) or 0) + (recipe.get('cook_time', 0) or 0)
    
    if total_time > 0:
        if total_time <= 15:
            score += 15  # Super quick
        elif total_time <= 30:
            score += 12  # Quick
        elif total_time <= 45:
            score += 8   # Medium
        elif total_time <= 60:
            score += 5   # Takes a while
        else:
            score += 2   # Long recipes
    else:
        score += 5  # No time info, give average score
    
    # 4. Ingredient count sweet spot (15 points max)
    ingredient_count = len(ingredients)
    if 5 <= ingredient_count <= 10:
        score += 15  # Perfect range
    elif 3 <= ingredient_count <= 12:
        score += 12  # Good range
    elif ingredient_count <= 15:
        score += 8   # Acceptable
    elif ingredient_count <= 20:
        score += 5   # Getting complex
    else:
        score += 2   # Very complex
    
    # Normalize to 0-100
    return min(100, max(0, round(score, 1)))


def add_popularity_to_recipes():
    """Add popularity scores to all recipes."""
    # Get the path to recipes.json
    script_dir = Path(__file__).parent
    data_dir = script_dir.parent / 'data'
    recipes_file = data_dir / 'recipes.json'
    
    if not recipes_file.exists():
        print(f"❌ Error: {recipes_file} not found!")
        return
    
    # Load recipes
    print(f"📖 Loading recipes from {recipes_file}...")
    with open(recipes_file, 'r', encoding='utf-8') as f:
        recipes = json.load(f)
    
    print(f"Found {len(recipes)} recipes")
    
    # Add popularity scores
    updated_count = 0
    for recipe in recipes:
        old_score = recipe.get('popularity_score')
        new_score = calculate_popularity_score(recipe)
        recipe['popularity_score'] = new_score
        
        if old_score != new_score:
            updated_count += 1
    
    # Sort by popularity (highest first)
    recipes.sort(key=lambda r: r.get('popularity_score', 0), reverse=True)
    
    # Save back
    print(f"💾 Saving {len(recipes)} recipes with popularity scores...")
    with open(recipes_file, 'w', encoding='utf-8') as f:
        json.dump(recipes, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Done! Updated {updated_count} recipes")
    
    # Show top 10 most popular
    print("\n🏆 Top 10 Most Popular Recipes:")
    for i, recipe in enumerate(recipes[:10], 1):
        score = recipe.get('popularity_score', 0)
        name = recipe.get('name', 'Unknown')
        source = recipe.get('source', 'Unknown')
        time = recipe.get('total_time', 0)
        print(f"  {i}. {name} ({source}) - Score: {score}, Time: {time}min")
    
    # Show score distribution
    print("\n📊 Score Distribution:")
    ranges = {
        '90-100': 0,
        '80-89': 0,
        '70-79': 0,
        '60-69': 0,
        '50-59': 0,
        '40-49': 0,
        '30-39': 0,
        '0-29': 0
    }
    
    for recipe in recipes:
        score = recipe.get('popularity_score', 0)
        if score >= 90:
            ranges['90-100'] += 1
        elif score >= 80:
            ranges['80-89'] += 1
        elif score >= 70:
            ranges['70-79'] += 1
        elif score >= 60:
            ranges['60-69'] += 1
        elif score >= 50:
            ranges['50-59'] += 1
        elif score >= 40:
            ranges['40-49'] += 1
        elif score >= 30:
            ranges['30-39'] += 1
        else:
            ranges['0-29'] += 1
    
    for range_name, count in ranges.items():
        print(f"  {range_name}: {count} recipes")


if __name__ == '__main__':
    add_popularity_to_recipes()

