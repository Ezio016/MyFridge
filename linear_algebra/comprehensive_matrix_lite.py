"""
Comprehensive Recipe Matrix System (Lite Version)

Exports recipe features to JSON/CSV without requiring NumPy.
Load the exported files in your own Python/NumPy environment.

Features captured:
1. Cooking Methods (15): bake, fry, grill, boil, simmer, etc.
2. Kitchen Equipment (20): oven, pan, pot, knife, etc.
3. Cooking Techniques (25): chop, dice, season, brown, etc.
4. Meal Categories (8): breakfast, lunch, dinner, etc.
5. Time: prep_time, cook_time, total_time
6. Difficulty: easy=1, medium=2, hard=3
7. Steps: number of instruction steps
"""

import json
import csv
from pathlib import Path
from collections import Counter

# ============================================================
# FEATURE DEFINITIONS
# ============================================================

COOKING_METHODS = [
    "bake", "roast", "broil", "grill", "fry", "sauté", "stir_fry",
    "boil", "simmer", "steam", "poach", "braise", "slow_cook", "microwave", "raw"
]

EQUIPMENT = [
    "oven", "stovetop", "pan", "pot", "wok", "baking_sheet", "baking_dish",
    "grill", "blender", "mixer", "knife", "cutting_board", "bowl", "whisk",
    "spatula", "tongs", "colander", "microwave", "slow_cooker", "pizza_stone"
]

TECHNIQUES = [
    "chop", "dice", "mince", "slice", "julienne", "grate", "mash", "blend",
    "whisk", "beat", "fold", "knead", "roll", "marinate", "season", "coat",
    "brown", "caramelize", "deglaze", "reduce", "drain", "rest", "garnish", "plate", "serve"
]

CATEGORIES = ["breakfast", "lunch", "dinner", "appetizer", "main", "side", "dessert", "snack"]

DIFFICULTY_MAP = {"easy": 1, "medium": 2, "hard": 3, "challenging": 4}

# Keyword mappings for extraction
METHOD_KEYWORDS = {
    'bake': ['bake', 'baking', 'baked'],
    'roast': ['roast', 'roasting', 'roasted'],
    'broil': ['broil', 'broiling'],
    'grill': ['grill', 'grilling', 'grilled'],
    'fry': ['fry', 'frying', 'fried', 'deep fry'],
    'sauté': ['saute', 'sauté', 'sauteing'],
    'stir_fry': ['stir fry', 'stir-fry', 'wok'],
    'boil': ['boil', 'boiling', 'boiled'],
    'simmer': ['simmer', 'simmering'],
    'steam': ['steam', 'steaming', 'steamed'],
    'poach': ['poach', 'poaching'],
    'braise': ['braise', 'braising'],
    'slow_cook': ['slow cook', 'slow cooker', 'crock pot'],
    'microwave': ['microwave'],
    'raw': ['no cook', 'raw', 'uncooked'],
}

EQUIP_KEYWORDS = {
    'oven': ['oven', 'preheat'],
    'stovetop': ['stove', 'burner', 'heat over'],
    'pan': ['pan', 'skillet'],
    'pot': ['pot', 'saucepan'],
    'wok': ['wok'],
    'baking_sheet': ['baking sheet', 'sheet pan', 'baking tray'],
    'baking_dish': ['baking dish', 'casserole'],
    'grill': ['grill', 'bbq'],
    'blender': ['blender', 'food processor'],
    'mixer': ['mixer'],
    'knife': ['cut ', 'chop', 'dice', 'mince', 'slice'],
    'cutting_board': ['cutting board'],
    'bowl': ['bowl'],
    'whisk': ['whisk'],
    'spatula': ['spatula'],
    'tongs': ['tongs'],
    'colander': ['colander', 'drain'],
    'microwave': ['microwave'],
    'slow_cooker': ['slow cooker', 'crock pot'],
    'pizza_stone': ['pizza stone'],
}

TECH_KEYWORDS = {
    'chop': ['chop'],
    'dice': ['dice', 'diced'],
    'mince': ['mince', 'minced'],
    'slice': ['slice', 'sliced'],
    'julienne': ['julienne'],
    'grate': ['grate', 'grated'],
    'mash': ['mash', 'mashed'],
    'blend': ['blend'],
    'whisk': ['whisk'],
    'beat': ['beat', 'beaten'],
    'fold': ['fold '],
    'knead': ['knead'],
    'roll': ['roll out', 'rolling'],
    'marinate': ['marinate'],
    'season': ['season'],
    'coat': ['coat'],
    'brown': ['brown'],
    'caramelize': ['caramelize'],
    'deglaze': ['deglaze'],
    'reduce': ['reduce'],
    'drain': ['drain'],
    'rest': ['let rest', 'rest for'],
    'garnish': ['garnish'],
    'plate': ['plate'],
    'serve': ['serve'],
}


def extract_features(text, keyword_map):
    """Extract features from text using keyword matching."""
    text = text.lower()
    found = []
    for feature, keywords in keyword_map.items():
        for kw in keywords:
            if kw in text:
                found.append(feature)
                break
    return found


def parse_time(time_val):
    """Parse time to minutes."""
    if not time_val:
        return 0
    if isinstance(time_val, (int, float)):
        return int(time_val)
    return 0


def process_recipes(recipes):
    """Process all recipes and extract features."""
    results = []
    
    for recipe in recipes:
        name = recipe.get('name', 'Unknown')
        
        # Get instructions text
        instructions = recipe.get('instructions', [])
        if isinstance(instructions, list):
            text = ' '.join(instructions)
            num_steps = len(instructions)
        else:
            text = str(instructions)
            num_steps = 1
        
        # Extract features
        methods = extract_features(text, METHOD_KEYWORDS)
        equipment = extract_features(text, EQUIP_KEYWORDS)
        techniques = extract_features(text, TECH_KEYWORDS)
        
        # Category
        category = recipe.get('category', '').lower()
        
        # Times
        prep_time = parse_time(recipe.get('prep_time'))
        cook_time = parse_time(recipe.get('cook_time'))
        total_time = parse_time(recipe.get('total_time'))
        
        # Difficulty
        diff = recipe.get('difficulty', '').lower()
        difficulty = DIFFICULTY_MAP.get(diff, 0)
        
        results.append({
            'name': name,
            'methods': methods,
            'equipment': equipment,
            'techniques': techniques,
            'category': category,
            'prep_time': prep_time,
            'cook_time': cook_time,
            'total_time': total_time,
            'difficulty': difficulty,
            'num_steps': num_steps,
        })
    
    return results


def to_binary_row(features, all_features):
    """Convert feature list to binary row."""
    return [1 if f in features else 0 for f in all_features]


def export_matrices(results, output_dir):
    """Export to CSV and JSON."""
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    
    # Build column headers
    all_features = (
        [f"method_{m}" for m in COOKING_METHODS] +
        [f"equip_{e}" for e in EQUIPMENT] +
        [f"tech_{t}" for t in TECHNIQUES] +
        [f"cat_{c}" for c in CATEGORIES] +
        ["prep_time", "cook_time", "total_time", "difficulty", "num_steps"]
    )
    
    # Export comprehensive CSV
    with open(output_dir / "comprehensive_matrix.csv", 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['recipe'] + all_features)
        
        for r in results:
            row = [r['name']]
            # Methods
            row.extend(to_binary_row(r['methods'], COOKING_METHODS))
            # Equipment
            row.extend(to_binary_row(r['equipment'], EQUIPMENT))
            # Techniques
            row.extend(to_binary_row(r['techniques'], TECHNIQUES))
            # Categories
            row.extend(to_binary_row([r['category']], CATEGORIES))
            # Numeric features
            row.extend([r['prep_time'], r['cook_time'], r['total_time'], r['difficulty'], r['num_steps']])
            writer.writerow(row)
    
    print(f"  ✓ comprehensive_matrix.csv ({len(results)} × {len(all_features)+1})")
    
    # Export individual matrices
    for name, features, keywords in [
        ("method_matrix.csv", COOKING_METHODS, 'methods'),
        ("equip_matrix.csv", EQUIPMENT, 'equipment'),
        ("tech_matrix.csv", TECHNIQUES, 'techniques'),
        ("category_matrix.csv", CATEGORIES, 'category'),
    ]:
        with open(output_dir / name, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['recipe'] + features)
            for r in results:
                feat_val = r[keywords] if keywords != 'category' else [r[keywords]]
                row = [r['name']] + to_binary_row(feat_val, features)
                writer.writerow(row)
        print(f"  ✓ {name}")
    
    # Export time/difficulty vectors
    with open(output_dir / "numeric_features.csv", 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['recipe', 'prep_time', 'cook_time', 'total_time', 'difficulty', 'num_steps'])
        for r in results:
            writer.writerow([r['name'], r['prep_time'], r['cook_time'], r['total_time'], r['difficulty'], r['num_steps']])
    print(f"  ✓ numeric_features.csv")
    
    # Export metadata JSON
    method_counts = Counter()
    equip_counts = Counter()
    tech_counts = Counter()
    cat_counts = Counter()
    
    for r in results:
        method_counts.update(r['methods'])
        equip_counts.update(r['equipment'])
        tech_counts.update(r['techniques'])
        if r['category']:
            cat_counts[r['category']] += 1
    
    metadata = {
        "description": "Comprehensive Recipe Feature Matrix",
        "total_recipes": len(results),
        "feature_counts": {
            "methods": len(COOKING_METHODS),
            "equipment": len(EQUIPMENT),
            "techniques": len(TECHNIQUES),
            "categories": len(CATEGORIES),
            "numeric": 5,
            "total": len(all_features),
        },
        "feature_lists": {
            "methods": COOKING_METHODS,
            "equipment": EQUIPMENT,
            "techniques": TECHNIQUES,
            "categories": CATEGORIES,
        },
        "statistics": {
            "method_frequencies": dict(method_counts.most_common()),
            "equipment_frequencies": dict(equip_counts.most_common()),
            "technique_frequencies": dict(tech_counts.most_common(10)),
            "category_distribution": dict(cat_counts),
            "avg_prep_time": sum(r['prep_time'] for r in results) / len(results),
            "avg_cook_time": sum(r['cook_time'] for r in results) / len(results),
            "avg_total_time": sum(r['total_time'] for r in results) / len(results),
            "avg_steps": sum(r['num_steps'] for r in results) / len(results),
        }
    }
    
    with open(output_dir / "comprehensive_metadata.json", 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"  ✓ comprehensive_metadata.json")
    
    # Export JSON version of results
    with open(output_dir / "recipe_features.json", 'w') as f:
        json.dump(results, f, indent=2)
    print(f"  ✓ recipe_features.json")
    
    return metadata


def print_summary(metadata):
    """Print summary statistics."""
    print("\n" + "=" * 70)
    print("COMPREHENSIVE RECIPE MATRIX SUMMARY")
    print("=" * 70)
    print(f"\nTotal Recipes: {metadata['total_recipes']}")
    print(f"Total Features: {metadata['feature_counts']['total']}")
    
    print("\nFeature Breakdown:")
    for key, count in metadata['feature_counts'].items():
        if key != 'total':
            print(f"  {key.capitalize():12}: {count}")
    
    print("\nTop Cooking Methods:")
    for method, count in list(metadata['statistics']['method_frequencies'].items())[:5]:
        print(f"  {method:15}: {count} recipes")
    
    print("\nTop Equipment:")
    for equip, count in list(metadata['statistics']['equipment_frequencies'].items())[:5]:
        print(f"  {equip:15}: {count} recipes")
    
    print("\nTop Techniques:")
    for tech, count in list(metadata['statistics']['technique_frequencies'].items())[:5]:
        print(f"  {tech:15}: {count} recipes")
    
    print(f"\nAverage Times:")
    print(f"  Prep:  {metadata['statistics']['avg_prep_time']:.1f} min")
    print(f"  Cook:  {metadata['statistics']['avg_cook_time']:.1f} min")
    print(f"  Total: {metadata['statistics']['avg_total_time']:.1f} min")
    print(f"  Steps: {metadata['statistics']['avg_steps']:.1f}")


def main():
    # Load recipes
    recipes_path = Path(__file__).parent.parent / "backend" / "data" / "recipes.json"
    
    print(f"Loading recipes from: {recipes_path}")
    with open(recipes_path, 'r') as f:
        recipes = json.load(f)
    print(f"Loaded {len(recipes)} recipes")
    
    # Process
    print("\nExtracting features...")
    results = process_recipes(recipes)
    
    # Export
    output_dir = Path(__file__).parent / "exports"
    print(f"\nExporting to: {output_dir}")
    metadata = export_matrices(results, output_dir)
    
    # Summary
    print_summary(metadata)
    
    print("\n" + "=" * 70)
    print("USAGE: Load the CSV files in Python/NumPy:")
    print("=" * 70)
    print("""
import numpy as np
import pandas as pd

# Load comprehensive matrix
df = pd.read_csv('exports/comprehensive_matrix.csv', index_col=0)
R = df.values  # NumPy array

# Or load individual matrices
methods = pd.read_csv('exports/method_matrix.csv', index_col=0)
equipment = pd.read_csv('exports/equip_matrix.csv', index_col=0)
techniques = pd.read_csv('exports/tech_matrix.csv', index_col=0)
""")


if __name__ == "__main__":
    main()
