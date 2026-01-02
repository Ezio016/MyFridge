"""
Food.com Dataset Batch Importer
================================

Imports recipes from Food.com Kaggle dataset with:
- Smart duplicate detection
- AI rewriting for legal compliance
- Progress tracking
- Incremental saves
- Rate limit handling

Instructions:
1. Download Food.com dataset from Kaggle:
   https://www.kaggle.com/datasets/shuyangli94/food-com-recipes-and-user-interactions
2. Place RAW_recipes.csv in backend/data/raw/
3. Run: python scraper/batch_import_foodcom.py --limit 1000
"""

import csv
import json
import os
import time
import argparse
from typing import List, Dict, Set
from pathlib import Path
import re

# Import our legal recipe importer
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from legal_recipe_importer import LegalRecipeImporter

class FoodComImporter:
    """Imports recipes from Food.com CSV with duplicate detection."""
    
    def __init__(self, groq_api_key: str = None):
        """Initialize importer."""
        self.legal_importer = LegalRecipeImporter(groq_api_key)
        self.existing_recipes = []
        self.existing_names = set()
        self.existing_ids = set()
        self.stats = {
            'processed': 0,
            'imported': 0,
            'duplicates': 0,
            'errors': 0
        }
    
    def load_existing_recipes(self, db_path: str):
        """Load existing recipes to check for duplicates."""
        try:
            with open(db_path, 'r', encoding='utf-8') as f:
                self.existing_recipes = json.load(f)
            
            # Build lookup sets for fast duplicate checking
            for recipe in self.existing_recipes:
                self.existing_names.add(self._normalize_name(recipe.get('name', '')))
                self.existing_ids.add(recipe.get('id', ''))
            
            print(f"📊 Loaded {len(self.existing_recipes)} existing recipes")
            
        except FileNotFoundError:
            print("📊 Starting with empty database")
            self.existing_recipes = []
    
    def _normalize_name(self, name: str) -> str:
        """Normalize recipe name for duplicate detection."""
        # Remove special characters, lowercase, remove extra spaces
        normalized = re.sub(r'[^\w\s]', '', name.lower())
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        return normalized
    
    def is_duplicate(self, recipe_name: str, recipe_id: str) -> bool:
        """Check if recipe is a duplicate."""
        # Check by ID first
        if recipe_id in self.existing_ids:
            return True
        
        # Check by normalized name
        normalized_name = self._normalize_name(recipe_name)
        if normalized_name in self.existing_names:
            return True
        
        return False
    
    def parse_foodcom_row(self, row: Dict) -> Dict:
        """
        Parse a Food.com CSV row into our format.
        
        Food.com columns:
        - name: recipe name
        - id: recipe id
        - minutes: cooking time
        - contributor_id: uploader
        - submitted: date
        - tags: JSON list
        - nutrition: JSON list [calories, fat, sugar, sodium, protein, saturated fat, carbs]
        - n_steps: number of steps
        - steps: JSON list
        - description: text
        - ingredients: JSON list
        - n_ingredients: count
        """
        try:
            # Parse JSON fields
            tags = json.loads(row.get('tags', '[]'))
            steps = json.loads(row.get('steps', '[]'))
            ingredients = json.loads(row.get('ingredients', '[]'))
            
            # Clean up tags (remove generic ones)
            cleaned_tags = [t for t in tags if len(t) > 2 and t not in ['preparation', 'time-to-make']]
            
            # Estimate times
            total_minutes = int(row.get('minutes', 30))
            prep_time = min(total_minutes // 3, 30)  # Estimate 1/3 is prep
            cook_time = total_minutes - prep_time
            
            # Determine cuisine from tags
            cuisine_keywords = {
                'italian': 'Italian',
                'mexican': 'Mexican',
                'asian': 'Asian',
                'chinese': 'Chinese',
                'japanese': 'Japanese',
                'thai': 'Thai',
                'indian': 'Indian',
                'french': 'French',
                'greek': 'Greek',
                'mediterranean': 'Mediterranean',
                'american': 'American'
            }
            
            cuisine = 'International'
            for keyword, cuisine_name in cuisine_keywords.items():
                if any(keyword in tag.lower() for tag in cleaned_tags):
                    cuisine = cuisine_name
                    break
            
            # Determine category from tags
            category = 'main'
            if any(tag in ['dessert', 'cookies-and-brownies', 'pie', 'cakes'] for tag in cleaned_tags):
                category = 'dessert'
            elif any(tag in ['breakfast', 'brunch'] for tag in cleaned_tags):
                category = 'breakfast'
            elif any(tag in ['soups-stews', 'chowders'] for tag in cleaned_tags):
                category = 'soup'
            elif any(tag in ['salads', 'vegetable'] for tag in cleaned_tags):
                category = 'salad'
            elif any(tag in ['appetizers', 'snacks'] for tag in cleaned_tags):
                category = 'appetizer'
            
            # Build raw recipe
            raw_recipe = {
                'id': f"foodcom_{row.get('id', '')}",
                'source': 'Food.com Dataset',
                'name': row.get('name', '').strip(),
                'ingredients': ingredients,
                'steps': steps,
                'cook_time': cook_time,
                'prep_time': prep_time,
                'servings': 4,  # Default, not in dataset
                'cuisine': cuisine,
                'category': category,
                'tags': cleaned_tags[:10]  # Keep top 10 tags
            }
            
            return raw_recipe
            
        except Exception as e:
            print(f"⚠️ Error parsing row: {e}")
            return None
    
    def import_batch(self, csv_path: str, limit: int = 1000, use_ai: bool = False):
        """
        Import recipes from Food.com CSV.
        
        Args:
            csv_path: Path to RAW_recipes.csv
            limit: Maximum number of recipes to import
            use_ai: Whether to use AI for rewriting (slower but better)
        """
        if not os.path.exists(csv_path):
            print(f"❌ CSV file not found: {csv_path}")
            print(f"\n📥 Download instructions:")
            print(f"   1. Go to: https://www.kaggle.com/datasets/shuyangli94/food-com-recipes-and-user-interactions")
            print(f"   2. Download RAW_recipes.csv")
            print(f"   3. Place it at: {csv_path}")
            return
        
        print(f"\n🍳 Food.com Batch Importer")
        print(f"=" * 60)
        print(f"📁 Reading: {csv_path}")
        print(f"🎯 Target: {limit} new recipes")
        print(f"🤖 AI rewriting: {'Enabled' if use_ai else 'Simple mode (faster)'}")
        
        new_recipes = []
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for i, row in enumerate(reader):
                    # Stop if we've reached limit
                    if len(new_recipes) >= limit:
                        break
                    
                    # Progress update every 100 rows
                    if i % 100 == 0 and i > 0:
                        print(f"📊 Processed {i} rows, imported {len(new_recipes)} recipes, found {self.stats['duplicates']} duplicates")
                    
                    # Parse row
                    raw_recipe = self.parse_foodcom_row(row)
                    if not raw_recipe:
                        self.stats['errors'] += 1
                        continue
                    
                    self.stats['processed'] += 1
                    
                    # Check for duplicates
                    if self.is_duplicate(raw_recipe['name'], raw_recipe['id']):
                        self.stats['duplicates'] += 1
                        continue
                    
                    # Create legal recipe
                    try:
                        legal_recipe = self.legal_importer.create_legal_recipe(raw_recipe, use_ai=use_ai)
                        new_recipes.append(legal_recipe)
                        self.stats['imported'] += 1
                        
                        # Add to duplicate check sets
                        self.existing_names.add(self._normalize_name(legal_recipe['name']))
                        self.existing_ids.add(legal_recipe['id'])
                        
                        # Show progress for first few and every 50th
                        if len(new_recipes) <= 5 or len(new_recipes) % 50 == 0:
                            print(f"  ✅ [{len(new_recipes)}] {legal_recipe['name']} ({legal_recipe['total_time']} min)")
                        
                        # Rate limiting for AI (if using)
                        if use_ai:
                            time.sleep(2)  # 30 requests/min = 2 sec delay
                        
                    except Exception as e:
                        print(f"  ⚠️ Error creating recipe: {e}")
                        self.stats['errors'] += 1
                        continue
        
        except Exception as e:
            print(f"❌ Error reading CSV: {e}")
            return []
        
        return new_recipes
    
    def save_recipes(self, new_recipes: List[Dict], db_path: str):
        """Save recipes to database."""
        all_recipes = self.existing_recipes + new_recipes
        
        # Create backup
        if os.path.exists(db_path):
            backup_path = db_path.replace('.json', '.backup.json')
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(self.existing_recipes, f, indent=2, ensure_ascii=False)
            print(f"💾 Backup saved to: {backup_path}")
        
        # Save updated database
        with open(db_path, 'w', encoding='utf-8') as f:
            json.dump(all_recipes, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Saved {len(all_recipes)} total recipes to: {db_path}")
    
    def print_stats(self):
        """Print import statistics."""
        print(f"\n📊 Import Statistics")
        print(f"=" * 60)
        print(f"  Rows processed:    {self.stats['processed']}")
        print(f"  ✅ Imported:       {self.stats['imported']}")
        print(f"  🔄 Duplicates:     {self.stats['duplicates']}")
        print(f"  ⚠️ Errors:         {self.stats['errors']}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Import recipes from Food.com dataset')
    parser.add_argument('--limit', type=int, default=1000, help='Number of recipes to import (default: 1000)')
    parser.add_argument('--csv', type=str, default=None, help='Path to RAW_recipes.csv')
    parser.add_argument('--use-ai', action='store_true', help='Use AI for rewriting (slower but better quality)')
    args = parser.parse_args()
    
    # Setup paths
    script_dir = Path(__file__).parent
    default_csv = script_dir / '..' / 'data' / 'raw' / 'RAW_recipes.csv'
    csv_path = args.csv if args.csv else str(default_csv)
    db_path = script_dir / '..' / 'data' / 'recipes.json'
    
    # Get Groq API key from environment
    groq_api_key = os.getenv('GROQ_API_KEY')
    if args.use_ai and not groq_api_key:
        print("⚠️ GROQ_API_KEY not found in environment. AI rewriting disabled.")
        print("   Set it with: export GROQ_API_KEY='your-key-here'")
        args.use_ai = False
    
    # Create importer
    importer = FoodComImporter(groq_api_key=groq_api_key if args.use_ai else None)
    
    # Load existing recipes
    importer.load_existing_recipes(str(db_path))
    
    # Import batch
    new_recipes = importer.import_batch(csv_path, limit=args.limit, use_ai=args.use_ai)
    
    if new_recipes:
        # Save to database
        importer.save_recipes(new_recipes, str(db_path))
        
        # Print stats
        importer.print_stats()
        
        print(f"\n🎉 Successfully imported {len(new_recipes)} new recipes!")
        print(f"📊 Total database size: {len(importer.existing_recipes) + len(new_recipes)} recipes")
    else:
        print("\n⚠️ No new recipes imported.")
    
    print(f"\n💡 To import more: python scraper/batch_import_foodcom.py --limit 5000")


if __name__ == '__main__':
    main()

