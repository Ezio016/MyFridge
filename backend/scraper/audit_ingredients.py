"""
Recipe Ingredient Audit Tool
=============================

Analyzes all recipes to find ingredients that might be wrongly classified
as pantry staples or optional items.

Helps ensure recipe identity is preserved (e.g., chickpea flour for Faina)
"""

import json
import os
from pathlib import Path
from collections import defaultdict
import re

class IngredientAuditor:
    """Audit recipe ingredients for proper classification."""
    
    # Specialty ingredients that should NEVER be pantry staples
    SPECIALTY_KEYWORDS = [
        # Specialty flours
        'chickpea', 'almond', 'coconut', 'rice flour', 'cornmeal',
        'semolina', 'buckwheat', 'rye', 'spelt', 'quinoa flour',
        'oat flour', 'whole wheat', 'bread flour', 'cake flour',
        
        # Specialty dairy
        'parmesan', 'parmigiano', 'cheddar', 'mozzarella', 'feta',
        'goat cheese', 'blue cheese', 'brie', 'camembert',
        'cream cheese', 'sour cream', 'heavy cream', 'whipping cream',
        'greek yogurt', 'buttermilk', 'ricotta', 'mascarpone',
        
        # Specialty proteins
        'prosciutto', 'pancetta', 'bacon', 'sausage', 'chorizo',
        'lamb', 'veal', 'duck', 'venison', 'salmon', 'tuna',
        'shrimp', 'prawns', 'lobster', 'crab', 'scallops',
        'anchovies', 'sardines',
        
        # Specialty produce
        'avocado', 'eggplant', 'zucchini', 'asparagus', 'artichoke',
        'fennel', 'leek', 'shallot', 'kale', 'arugula', 'spinach',
        'bok choy', 'broccoli', 'cauliflower', 'brussels sprouts',
        
        # Specialty condiments/sauces
        'tahini', 'miso', 'curry paste', 'fish sauce', 'oyster sauce',
        'hoisin', 'sriracha', 'harissa', 'pesto', 'capers',
        'olives', 'sun-dried tomato', 'roasted red pepper',
        
        # Specialty herbs/spices (beyond basic)
        'saffron', 'cardamom', 'turmeric', 'cumin', 'coriander',
        'paprika', 'cayenne', 'chili powder', 'curry powder',
        'garam masala', 'five spice', 'oregano', 'thyme',
        'rosemary', 'basil', 'cilantro', 'parsley', 'dill',
        'mint', 'sage', 'tarragon',
        
        # Specialty nuts/seeds
        'pine nuts', 'cashews', 'pistachios', 'hazelnuts',
        'macadamia', 'pecans', 'walnuts', 'sesame seeds',
        'sunflower seeds', 'pumpkin seeds', 'chia seeds',
        'flax seeds',
        
        # Specialty sweeteners
        'honey', 'maple syrup', 'agave', 'molasses', 'brown sugar',
        'powdered sugar', 'confectioners',
        
        # Specialty grains/legumes
        'quinoa', 'couscous', 'bulgur', 'farro', 'barley',
        'lentils', 'chickpeas', 'black beans', 'kidney beans',
        
        # Specialty liquids
        'coconut milk', 'almond milk', 'wine', 'beer', 'stock',
        'broth', 'tomato sauce', 'tomato paste',
    ]
    
    # Only these are TRUE pantry staples (universally available)
    BASIC_PANTRY = [
        'salt', 'pepper', 'black pepper', 'water',
        'oil', 'olive oil', 'vegetable oil', 'cooking oil', 'canola oil',
        'butter', 'unsalted butter', 'salted butter',
        'sugar', 'white sugar', 'granulated sugar',
        'flour', 'all-purpose flour', 'plain flour', 'ap flour',
        'garlic', 'garlic clove', 'garlic powder',
        'onion', 'onion powder',
        'soy sauce', 'vinegar', 'white vinegar', 'balsamic vinegar',
    ]
    
    def __init__(self):
        self.recipes = []
        self.issues = []
        self.stats = {
            'total_recipes': 0,
            'total_ingredients': 0,
            'specialty_found': 0,
            'potential_issues': 0
        }
    
    def load_recipes(self, db_path: str):
        """Load recipes from database."""
        with open(db_path, 'r', encoding='utf-8') as f:
            self.recipes = json.load(f)
        self.stats['total_recipes'] = len(self.recipes)
        print(f"📊 Loaded {len(self.recipes)} recipes")
    
    def normalize_ingredient(self, ing: str) -> str:
        """Normalize ingredient for comparison."""
        # Remove measurements
        ing = re.sub(r'^\d+(\.\d+)?\s*(cup|cups|tablespoon|tablespoons|teaspoon|teaspoons|tbsp|tsp|oz|g|kg|lb|ml|l)s?\s+', '', ing, flags=re.IGNORECASE)
        ing = re.sub(r'^\d+(\.\d+)?\s+', '', ing)  # Remove leading numbers
        # Remove parenthetical notes
        ing = re.sub(r'\([^)]*\)', '', ing)
        # Lowercase and trim
        ing = ing.lower().strip()
        # Remove "to taste", "optional", etc.
        ing = re.sub(r',?\s*(to taste|optional|if needed|or more)$', '', ing, flags=re.IGNORECASE)
        return ing.strip()
    
    def is_specialty_ingredient(self, ing: str) -> tuple:
        """Check if ingredient is specialty (returns (bool, matched_keyword))."""
        ing_norm = self.normalize_ingredient(ing)
        
        for keyword in self.SPECIALTY_KEYWORDS:
            if keyword in ing_norm:
                return (True, keyword)
        
        return (False, None)
    
    def is_basic_pantry(self, ing: str) -> tuple:
        """Check if ingredient is basic pantry (returns (bool, matched_item))."""
        ing_norm = self.normalize_ingredient(ing)
        
        # Check for exact or close match
        for pantry_item in self.BASIC_PANTRY:
            # Exact match
            if ing_norm == pantry_item:
                return (True, pantry_item)
            # Contains match (but not if it's a specialty variation)
            if pantry_item in ing_norm:
                # For flour, be strict
                if 'flour' in pantry_item:
                    if ing_norm in ['flour', 'all-purpose flour', 'plain flour', 'ap flour']:
                        return (True, pantry_item)
                else:
                    return (True, pantry_item)
        
        return (False, None)
    
    def audit_recipes(self):
        """Audit all recipes for ingredient classification."""
        print(f"\n🔍 Auditing {len(self.recipes)} recipes...\n")
        
        # Track all ingredients
        all_ingredients = defaultdict(list)  # ingredient -> [recipe names]
        specialty_ingredients = defaultdict(list)
        ambiguous_ingredients = []  # Neither specialty nor basic pantry
        
        for recipe in self.recipes:
            recipe_name = recipe.get('name', 'Unknown')
            ingredients = recipe.get('ingredients', [])
            
            for ing in ingredients:
                self.stats['total_ingredients'] += 1
                
                # Normalize
                ing_norm = self.normalize_ingredient(ing)
                if not ing_norm or len(ing_norm) < 2:
                    continue
                
                # Track
                all_ingredients[ing_norm].append(recipe_name)
                
                # Check classification
                is_specialty, specialty_match = self.is_specialty_ingredient(ing)
                is_pantry, pantry_match = self.is_basic_pantry(ing)
                
                if is_specialty:
                    self.stats['specialty_found'] += 1
                    specialty_ingredients[ing_norm].append({
                        'recipe': recipe_name,
                        'matched': specialty_match,
                        'original': ing
                    })
                elif not is_pantry:
                    # Not specialty, not basic pantry = ambiguous
                    # These are the main ingredients!
                    ambiguous_ingredients.append({
                        'ingredient': ing_norm,
                        'recipe': recipe_name,
                        'original': ing
                    })
        
        # Generate reports
        self.generate_specialty_report(specialty_ingredients)
        self.generate_ambiguous_report(ambiguous_ingredients)
        self.print_stats()
    
    def generate_specialty_report(self, specialty_ingredients):
        """Generate report of specialty ingredients."""
        print("=" * 80)
        print("SPECIALTY INGREDIENTS FOUND (Should be MAIN, not optional)")
        print("=" * 80)
        
        # Sort by frequency
        sorted_specialty = sorted(specialty_ingredients.items(), key=lambda x: len(x[1]), reverse=True)
        
        for ing, occurrences in sorted_specialty[:50]:  # Top 50
            print(f"\n🔴 {ing}")
            print(f"   Used in {len(occurrences)} recipe(s)")
            print(f"   Matched keyword: '{occurrences[0]['matched']}'")
            # Show first 3 recipes
            for i, occ in enumerate(occurrences[:3]):
                print(f"   - {occ['recipe']}")
            if len(occurrences) > 3:
                print(f"   ... and {len(occurrences) - 3} more")
    
    def generate_ambiguous_report(self, ambiguous_ingredients):
        """Generate report of ambiguous ingredients (main ingredients)."""
        print("\n" + "=" * 80)
        print("MAIN INGREDIENTS (Not pantry, not specialty - the actual recipe items)")
        print("=" * 80)
        
        # Group by ingredient
        grouped = defaultdict(list)
        for item in ambiguous_ingredients:
            grouped[item['ingredient']].append(item['recipe'])
        
        # Sort by frequency
        sorted_main = sorted(grouped.items(), key=lambda x: len(x[1]), reverse=True)
        
        print(f"\nFound {len(sorted_main)} unique main ingredients")
        print("\nTop 30 most common main ingredients:")
        for ing, recipes in sorted_main[:30]:
            print(f"  ✅ {ing} (used in {len(recipes)} recipes)")
    
    def print_stats(self):
        """Print audit statistics."""
        print("\n" + "=" * 80)
        print("AUDIT STATISTICS")
        print("=" * 80)
        print(f"  Total recipes:        {self.stats['total_recipes']}")
        print(f"  Total ingredients:    {self.stats['total_ingredients']}")
        print(f"  Specialty found:      {self.stats['specialty_found']}")
        print(f"  Avg per recipe:       {self.stats['total_ingredients'] / self.stats['total_recipes']:.1f}")
    
    def export_lists(self, output_dir: str):
        """Export specialty and pantry lists for code."""
        os.makedirs(output_dir, exist_ok=True)
        
        # Export specialty list
        specialty_path = os.path.join(output_dir, 'SPECIALTY_INGREDIENTS.txt')
        with open(specialty_path, 'w') as f:
            f.write("# Specialty Ingredients - Should NEVER be pantry staples\n\n")
            for keyword in sorted(self.SPECIALTY_KEYWORDS):
                f.write(f"{keyword}\n")
        
        # Export basic pantry list
        pantry_path = os.path.join(output_dir, 'BASIC_PANTRY.txt')
        with open(pantry_path, 'w') as f:
            f.write("# Basic Pantry Items - Can be assumed available\n\n")
            for item in sorted(self.BASIC_PANTRY):
                f.write(f"{item}\n")
        
        print(f"\n📄 Exported lists to {output_dir}")


def main():
    """Main entry point."""
    script_dir = Path(__file__).parent
    db_path = script_dir / '..' / 'data' / 'recipes.json'
    output_dir = script_dir / 'audit_results'
    
    print("🔍 Recipe Ingredient Auditor")
    print("=" * 80)
    
    # Create auditor
    auditor = IngredientAuditor()
    
    # Load recipes
    auditor.load_recipes(str(db_path))
    
    # Audit
    auditor.audit_recipes()
    
    # Export
    auditor.export_lists(str(output_dir))
    
    print("\n✅ Audit complete!")


if __name__ == '__main__':
    main()

