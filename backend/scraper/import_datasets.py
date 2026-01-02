"""
Import recipes from open-source datasets to quickly build a large database.

Sources:
1. TheMealDB API - Free, no key required, ~300 recipes
2. Recipe1M dataset - Academic dataset with 1M+ recipes
3. Food.com Kaggle dataset - 230k+ recipes
"""
import json
import requests
import time
from typing import List, Dict
import os

class DatasetImporter:
    def __init__(self):
        self.recipes = []
    
    def import_themealdb(self) -> List[Dict]:
        """
        Import recipes from TheMealDB API (free, no key required).
        API Docs: https://www.themealdb.com/api.php
        """
        print("\n🌐 Importing from TheMealDB API...")
        recipes = []
        
        # Get all categories
        categories_url = "https://www.themealdb.com/api/json/v1/1/categories.php"
        try:
            response = requests.get(categories_url, timeout=10)
            categories = response.json().get('categories', [])
            
            print(f"Found {len(categories)} categories")
            
            # For each category, get all meals
            for cat in categories[:5]:  # Start with first 5 categories
                cat_name = cat['strCategory']
                print(f"  📁 Fetching {cat_name} recipes...")
                
                meals_url = f"https://www.themealdb.com/api/json/v1/1/filter.php?c={cat_name}"
                meals_response = requests.get(meals_url, timeout=10)
                meals = meals_response.json().get('meals', [])
                
                # Get detailed info for each meal
                for meal in meals[:10]:  # Limit to 10 per category for now
                    meal_id = meal['idMeal']
                    detail_url = f"https://www.themealdb.com/api/json/v1/1/lookup.php?i={meal_id}"
                    
                    try:
                        detail_response = requests.get(detail_url, timeout=10)
                        meal_detail = detail_response.json().get('meals', [{}])[0]
                        
                        if not meal_detail:
                            continue
                        
                        # Extract ingredients
                        ingredients = []
                        for i in range(1, 21):
                            ing = meal_detail.get(f'strIngredient{i}', '').strip()
                            measure = meal_detail.get(f'strMeasure{i}', '').strip()
                            if ing:
                                ingredients.append(f"{measure} {ing}".strip())
                        
                        # Parse instructions into steps
                        instructions_text = meal_detail.get('strInstructions', '')
                        steps = [s.strip() for s in instructions_text.split('\r\n') if s.strip()]
                        if not steps:
                            steps = [s.strip() for s in instructions_text.split('.') if s.strip()]
                        
                        # Determine category
                        category = 'main'
                        if 'dessert' in cat_name.lower():
                            category = 'dessert'
                        elif 'breakfast' in cat_name.lower():
                            category = 'breakfast'
                        elif 'side' in cat_name.lower():
                            category = 'side'
                        
                        # Build recipe object
                        recipe = {
                            'id': f"themealdb_{meal_id}",
                            'source': 'TheMealDB',
                            'name': meal_detail.get('strMeal', 'Unknown'),
                            'description': f"{meal_detail.get('strMeal', '')} from {meal_detail.get('strArea', 'Unknown')} cuisine",
                            'prep_time': 10,  # Default estimates
                            'cook_time': 30,
                            'total_time': 40,
                            'servings': 4,
                            'difficulty': 'medium',
                            'ingredients': ingredients,
                            'instructions': steps[:15],  # Limit steps
                            'tags': [cat_name.lower(), meal_detail.get('strArea', '').lower()],
                            'cuisine': meal_detail.get('strArea', 'International'),
                            'category': category,
                            'image_url': meal_detail.get('strMealThumb', '')
                        }
                        
                        recipes.append(recipe)
                        print(f"    ✅ {recipe['name']}")
                        time.sleep(0.5)  # Be nice to the API
                        
                    except Exception as e:
                        print(f"    ⚠️ Error fetching meal {meal_id}: {e}")
                        continue
                
                time.sleep(1)  # Pause between categories
            
            print(f"\n✅ Imported {len(recipes)} recipes from TheMealDB")
            return recipes
            
        except Exception as e:
            print(f"❌ Error importing from TheMealDB: {e}")
            return []
    
    def save_recipes(self, output_file: str):
        """Save all recipes to JSON file."""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.recipes, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Saved {len(self.recipes)} recipes to {output_file}")


def main():
    """Main import function."""
    print("🍳 MyFridge Recipe Dataset Importer")
    print("=" * 60)
    
    importer = DatasetImporter()
    
    # Load existing recipes
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(script_dir, '..', 'data', 'recipes.json')
    
    try:
        with open(data_path, 'r', encoding='utf-8') as f:
            existing_recipes = json.load(f)
        print(f"📊 Current database: {len(existing_recipes)} recipes")
    except FileNotFoundError:
        existing_recipes = []
        print("📊 Starting with empty database")
    
    # Import from TheMealDB
    new_recipes = importer.import_themealdb()
    
    # Merge with existing (avoid duplicates)
    existing_ids = {r['id'] for r in existing_recipes}
    unique_new = [r for r in new_recipes if r['id'] not in existing_ids]
    
    all_recipes = existing_recipes + unique_new
    
    print(f"\n📈 Added {len(unique_new)} new recipes")
    print(f"📊 Total recipes: {len(all_recipes)}")
    
    # Save
    with open(data_path, 'w', encoding='utf-8') as f:
        json.dump(all_recipes, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Database updated successfully!")
    
    # Summary
    categories = {}
    cuisines = {}
    sources = {}
    
    for recipe in all_recipes:
        cat = recipe.get('category', 'unknown')
        categories[cat] = categories.get(cat, 0) + 1
        cui = recipe.get('cuisine', 'unknown')
        cuisines[cui] = cuisines.get(cui, 0) + 1
        src = recipe.get('source', 'unknown')
        sources[src] = sources.get(src, 0) + 1
    
    print("\n📂 By category:")
    for cat, count in sorted(categories.items(), key=lambda x: -x[1])[:10]:
        print(f"  - {cat}: {count}")
    
    print("\n🌍 By cuisine:")
    for cui, count in sorted(cuisines.items(), key=lambda x: -x[1])[:10]:
        print(f"  - {cui}: {count}")
    
    print("\n📚 By source:")
    for src, count in sorted(sources.items(), key=lambda x: -x[1]):
        print(f"  - {src}: {count}")
    
    print("\n💡 Next steps to reach 1000s of recipes:")
    print("  1. Run this script multiple times to get more categories")
    print("  2. Download Food.com dataset from Kaggle (230k+ recipes)")
    print("  3. Use Spoonacular API (5000+ recipes, free tier)")
    print("  4. Build aggressive web scrapers for major recipe sites")
    print("\n🚀 Want me to implement any of these? Just ask!")


if __name__ == '__main__':
    main()

