"""
Recipe Deduplication Tool
=========================

Finds and removes duplicate recipes from the database.
Uses fuzzy matching to catch similar names like:
- "Perfect Scrambled Eggs" vs "Classic Scrambled Eggs"
- "Chicken Pasta" vs "Easy Chicken Pasta"

Keeps the best version based on:
1. Source priority (TheMealDB > Curated > Bootstrap)
2. More ingredients/steps
3. Has image URL
"""

import json
import os
from pathlib import Path
from collections import defaultdict
import re

class RecipeDeduplicator:
    """Remove duplicate recipes from database."""
    
    # Source priority (higher = better)
    SOURCE_PRIORITY = {
        'TheMealDB': 100,
        'Recipe Puppy': 80,
        'Curated': 60,
        'MyFridge': 40,
    }
    
    # Words to ignore when comparing names
    IGNORE_WORDS = [
        'the', 'a', 'an', 'perfect', 'classic', 'easy', 'simple', 
        'best', 'homemade', 'ultimate', 'authentic', 'traditional',
        'quick', 'delicious', 'amazing', 'favorite', 'moms', "mom's"
    ]
    
    def __init__(self):
        self.recipes = []
        self.groups = defaultdict(list)
        self.stats = {
            'original': 0,
            'duplicates': 0,
            'kept': 0,
            'removed': 0
        }
    
    def normalize_name(self, name: str) -> str:
        """Normalize recipe name for comparison."""
        # Lowercase
        normalized = name.lower().strip()
        
        # Remove ignore words
        words = normalized.split()
        words = [w for w in words if w not in self.IGNORE_WORDS]
        normalized = ' '.join(words)
        
        # Remove special chars
        normalized = re.sub(r'[^\w\s]', '', normalized)
        
        # Remove extra spaces
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        return normalized
    
    def get_source_score(self, recipe: dict) -> int:
        """Get source priority score."""
        source = recipe.get('source', '').split('(')[0].strip()
        return self.SOURCE_PRIORITY.get(source, 0)
    
    def get_quality_score(self, recipe: dict) -> int:
        """Calculate recipe quality score."""
        score = 0
        
        # Source priority
        score += self.get_source_score(recipe)
        
        # Has image
        if recipe.get('image_url'):
            score += 20
        
        # Number of ingredients (more is better, up to 20)
        score += min(len(recipe.get('ingredients', [])), 20)
        
        # Number of steps (more is better, up to 15)
        score += min(len(recipe.get('instructions', [])), 15)
        
        # Has description
        if recipe.get('description'):
            score += 10
        
        # Has tags
        score += min(len(recipe.get('tags', [])), 10)
        
        return score
    
    def load_recipes(self, db_path: str):
        """Load recipes from database."""
        with open(db_path, 'r', encoding='utf-8') as f:
            self.recipes = json.load(f)
        self.stats['original'] = len(self.recipes)
        print(f"📊 Loaded {len(self.recipes)} recipes")
    
    def find_duplicates(self):
        """Group recipes by normalized name."""
        for recipe in self.recipes:
            normalized = self.normalize_name(recipe['name'])
            self.groups[normalized].append(recipe)
        
        # Count duplicates
        for normalized, group in self.groups.items():
            if len(group) > 1:
                self.stats['duplicates'] += len(group) - 1
        
        print(f"🔍 Found {self.stats['duplicates']} duplicate recipes")
    
    def deduplicate(self) -> list:
        """Remove duplicates, keeping best version."""
        deduplicated = []
        
        for normalized, group in self.groups.items():
            if len(group) == 1:
                # No duplicates, keep it
                deduplicated.append(group[0])
                self.stats['kept'] += 1
            else:
                # Duplicates found, keep best one
                print(f"\n🔄 Deduplicating '{normalized}':")
                
                # Score each recipe
                scored = []
                for recipe in group:
                    score = self.get_quality_score(recipe)
                    scored.append((score, recipe))
                    print(f"   - {recipe['name']} ({recipe['id']})")
                    print(f"     Source: {recipe.get('source', 'Unknown')}, Score: {score}")
                
                # Sort by score (highest first)
                scored.sort(reverse=True, key=lambda x: x[0])
                
                # Keep the best
                best = scored[0][1]
                deduplicated.append(best)
                print(f"   ✅ Keeping: {best['name']} (score: {scored[0][0]})")
                print(f"   ❌ Removing: {len(scored) - 1} duplicates")
                
                self.stats['kept'] += 1
                self.stats['removed'] += len(scored) - 1
        
        return deduplicated
    
    def save_recipes(self, recipes: list, db_path: str):
        """Save deduplicated recipes."""
        # Backup original
        backup_path = db_path.replace('.json', '.before_dedup.json')
        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump(self.recipes, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Backup saved to: {backup_path}")
        
        # Save deduplicated
        with open(db_path, 'w', encoding='utf-8') as f:
            json.dump(recipes, f, indent=2, ensure_ascii=False)
        print(f"✅ Saved {len(recipes)} deduplicated recipes")
    
    def print_stats(self):
        """Print deduplication statistics."""
        print(f"\n📊 Deduplication Stats")
        print(f"=" * 60)
        print(f"  Original recipes:  {self.stats['original']}")
        print(f"  Duplicates found:  {self.stats['duplicates']}")
        print(f"  Recipes kept:      {self.stats['kept']}")
        print(f"  Recipes removed:   {self.stats['removed']}")
        print(f"  Final count:       {self.stats['kept']}")
        print(f"  Reduction:         {self.stats['duplicates']} recipes ({self.stats['duplicates'] / self.stats['original'] * 100:.1f}%)")


def main():
    """Main entry point."""
    script_dir = Path(__file__).parent
    db_path = script_dir / '..' / 'data' / 'recipes.json'
    
    print("🧹 Recipe Deduplication Tool")
    print("=" * 60)
    
    # Create deduplicator
    dedup = RecipeDeduplicator()
    
    # Load recipes
    dedup.load_recipes(str(db_path))
    
    # Find duplicates
    dedup.find_duplicates()
    
    if dedup.stats['duplicates'] == 0:
        print("\n✅ No duplicates found! Database is clean.")
        return
    
    # Confirm
    response = input(f"\n⚠️  Remove {dedup.stats['duplicates']} duplicates? (y/N): ")
    if response.lower() != 'y':
        print("❌ Cancelled.")
        return
    
    # Deduplicate
    deduplicated = dedup.deduplicate()
    
    # Save
    dedup.save_recipes(deduplicated, str(db_path))
    
    # Stats
    dedup.print_stats()
    
    print(f"\n🎉 Deduplication complete!")
    print(f"💡 Backup saved in case you need to restore")


if __name__ == '__main__':
    main()

