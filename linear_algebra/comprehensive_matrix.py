"""
Comprehensive Recipe Matrix System

This module creates multiple matrices capturing different aspects of recipes:
1. Ingredient Matrix (R_ing)     - What ingredients are used
2. Method Matrix (R_method)      - Cooking methods (bake, fry, grill, etc.)
3. Equipment Matrix (R_equip)    - Kitchen equipment needed
4. Technique Matrix (R_tech)     - Cooking techniques (chop, dice, sauté, etc.)
5. Time Vectors                  - Prep time, cook time, total time
6. Difficulty Vector             - Encoded difficulty levels
7. Category Matrix               - Meal type (breakfast, lunch, dinner, etc.)

Perfect for demonstrating:
- Multi-view learning
- Matrix concatenation
- Feature engineering
- Dimensionality analysis
"""

import json
import re
import numpy as np
from pathlib import Path
from collections import Counter

# ============================================================
# COOKING METHODS (15)
# ============================================================
COOKING_METHODS = [
    "bake",         # oven baking
    "roast",        # oven roasting
    "broil",        # broiler/grill from above
    "grill",        # grilling
    "fry",          # pan frying, deep frying
    "sauté",        # sautéing (quick fry)
    "stir_fry",     # wok cooking
    "boil",         # boiling in water
    "simmer",       # gentle boiling
    "steam",        # steaming
    "poach",        # poaching in liquid
    "braise",       # slow cooking in liquid
    "slow_cook",    # slow cooker/crockpot
    "microwave",    # microwave cooking
    "raw",          # no cooking (salads, etc.)
]

# ============================================================
# KITCHEN EQUIPMENT (20)
# ============================================================
EQUIPMENT = [
    "oven",         # standard oven
    "stovetop",     # burner/hob
    "pan",          # frying pan/skillet
    "pot",          # cooking pot
    "wok",          # wok
    "baking_sheet", # sheet pan, baking tray
    "baking_dish",  # casserole dish
    "grill",        # outdoor grill, grill pan
    "blender",      # blender, food processor
    "mixer",        # stand mixer, hand mixer
    "knife",        # cutting/chopping
    "cutting_board",# prep surface
    "bowl",         # mixing bowls
    "whisk",        # whisking
    "spatula",      # flipping, stirring
    "tongs",        # gripping, turning
    "colander",     # draining
    "microwave",    # microwave oven
    "slow_cooker",  # crockpot
    "pizza_stone",  # pizza making
]

# ============================================================
# COOKING TECHNIQUES (25)
# ============================================================
TECHNIQUES = [
    "chop",         # rough cutting
    "dice",         # small cubes
    "mince",        # very fine cutting
    "slice",        # thin cuts
    "julienne",     # matchstick cuts
    "grate",        # grating/shredding
    "mash",         # mashing
    "blend",        # blending/pureeing
    "whisk",        # whisking
    "beat",         # beating eggs, etc.
    "fold",         # gentle folding
    "knead",        # bread dough
    "roll",         # rolling dough
    "marinate",     # marinating
    "season",       # adding spices
    "coat",         # coating with flour, etc.
    "brown",        # browning meat
    "caramelize",   # caramelizing
    "deglaze",      # deglazing pan
    "reduce",       # reducing sauce
    "drain",        # draining liquid
    "rest",         # resting meat
    "garnish",      # final garnishing
    "plate",        # plating/presentation
    "serve",        # serving
]

# ============================================================
# MEAL CATEGORIES (8)
# ============================================================
CATEGORIES = [
    "breakfast",
    "lunch", 
    "dinner",
    "appetizer",
    "main",
    "side",
    "dessert",
    "snack",
]

# ============================================================
# DIFFICULTY LEVELS
# ============================================================
DIFFICULTY_MAP = {
    "easy": 1,
    "medium": 2,
    "hard": 3,
    "challenging": 4,
}

# Create indices
METHOD_INDEX = {m: i for i, m in enumerate(COOKING_METHODS)}
EQUIP_INDEX = {e: i for i, e in enumerate(EQUIPMENT)}
TECH_INDEX = {t: i for i, t in enumerate(TECHNIQUES)}
CAT_INDEX = {c: i for i, c in enumerate(CATEGORIES)}


def extract_methods(instructions: list[str]) -> list[str]:
    """Extract cooking methods from instructions."""
    text = " ".join(instructions).lower()
    found = []
    
    # Simple keyword matching for speed
    keywords = {
        'bake': ['bake', 'baking', 'baked'],
        'roast': ['roast', 'roasting', 'roasted'],
        'broil': ['broil', 'broiling'],
        'grill': ['grill', 'grilling', 'grilled'],
        'fry': ['fry', 'frying', 'fried', 'deep fry'],
        'sauté': ['saute', 'sauté', 'sauteing', 'sautéing'],
        'stir_fry': ['stir fry', 'stir-fry', 'wok'],
        'boil': ['boil', 'boiling', 'boiled'],
        'simmer': ['simmer', 'simmering', 'simmered'],
        'steam': ['steam', 'steaming', 'steamed'],
        'poach': ['poach', 'poaching', 'poached'],
        'braise': ['braise', 'braising', 'braised'],
        'slow_cook': ['slow cook', 'slow cooker', 'crock pot'],
        'microwave': ['microwave'],
        'raw': ['no cook', 'raw', 'uncooked'],
    }
    
    for method, kws in keywords.items():
        for kw in kws:
            if kw in text:
                if method not in found:
                    found.append(method)
                break
    
    return found


def extract_equipment(instructions: list[str]) -> list[str]:
    """Extract kitchen equipment from instructions."""
    text = " ".join(instructions).lower()
    found = []
    
    keywords = {
        'oven': ['oven', 'preheat'],
        'stovetop': ['stove', 'burner', 'hob', 'heat'],
        'pan': ['pan', 'skillet'],
        'pot': ['pot', 'saucepan'],
        'wok': ['wok'],
        'baking_sheet': ['baking sheet', 'sheet pan', 'baking tray', 'cookie sheet'],
        'baking_dish': ['baking dish', 'casserole', 'roasting pan'],
        'grill': ['grill', 'bbq', 'barbecue'],
        'blender': ['blender', 'food processor', 'puree'],
        'mixer': ['mixer'],
        'knife': ['knife', 'cut', 'chop', 'dice', 'mince', 'slice'],
        'cutting_board': ['cutting board'],
        'bowl': ['bowl'],
        'whisk': ['whisk'],
        'spatula': ['spatula'],
        'tongs': ['tongs'],
        'colander': ['colander', 'drain', 'strainer'],
        'microwave': ['microwave'],
        'slow_cooker': ['slow cooker', 'crock pot'],
        'pizza_stone': ['pizza stone'],
    }
    
    for equip, kws in keywords.items():
        for kw in kws:
            if kw in text:
                if equip not in found:
                    found.append(equip)
                break
    
    return found


def extract_techniques(instructions: list[str]) -> list[str]:
    """Extract cooking techniques from instructions."""
    text = " ".join(instructions).lower()
    found = []
    
    keywords = {
        'chop': ['chop', 'chopped', 'chopping'],
        'dice': ['dice', 'diced', 'dicing'],
        'mince': ['mince', 'minced', 'mincing'],
        'slice': ['slice', 'sliced', 'slicing'],
        'julienne': ['julienne'],
        'grate': ['grate', 'grated', 'grating'],
        'mash': ['mash', 'mashed', 'mashing'],
        'blend': ['blend', 'blended', 'blending'],
        'whisk': ['whisk', 'whisked', 'whisking'],
        'beat': ['beat', 'beaten', 'beating'],
        'fold': ['fold', 'folded', 'folding'],
        'knead': ['knead', 'kneaded', 'kneading'],
        'roll': ['roll', 'rolled', 'rolling'],
        'marinate': ['marinate', 'marinated', 'marinating'],
        'season': ['season', 'seasoned', 'seasoning'],
        'coat': ['coat', 'coated', 'coating'],
        'brown': ['brown', 'browned', 'browning'],
        'caramelize': ['caramelize', 'caramelized'],
        'deglaze': ['deglaze', 'deglazed'],
        'reduce': ['reduce', 'reduced', 'reducing'],
        'drain': ['drain', 'drained', 'draining'],
        'rest': ['rest', 'rested', 'resting'],
        'garnish': ['garnish', 'garnished'],
        'plate': ['plate', 'plated', 'plating'],
        'serve': ['serve', 'served', 'serving'],
    }
    
    for tech, kws in keywords.items():
        for kw in kws:
            if kw in text:
                if tech not in found:
                    found.append(tech)
                break
    
    return found


def parse_time(time_str) -> int:
    """Parse time string to minutes."""
    if not time_str:
        return 0
    if isinstance(time_str, (int, float)):
        return int(time_str)
    
    time_str = str(time_str).lower()
    total = 0
    
    # Hours
    hours = re.search(r'(\d+)\s*h', time_str)
    if hours:
        total += int(hours.group(1)) * 60
    
    # Minutes
    mins = re.search(r'(\d+)\s*m', time_str)
    if mins:
        total += int(mins.group(1))
    
    # Just a number (assume minutes)
    if total == 0:
        just_num = re.search(r'(\d+)', time_str)
        if just_num:
            total = int(just_num.group(1))
    
    return total


def build_comprehensive_matrices(recipes: list[dict]):
    """Build all matrices from recipe data."""
    n = len(recipes)
    
    # Initialize matrices
    R_method = np.zeros((n, len(COOKING_METHODS)), dtype=np.int8)
    R_equip = np.zeros((n, len(EQUIPMENT)), dtype=np.int8)
    R_tech = np.zeros((n, len(TECHNIQUES)), dtype=np.int8)
    R_cat = np.zeros((n, len(CATEGORIES)), dtype=np.int8)
    
    # Initialize vectors
    v_prep = np.zeros(n, dtype=np.float32)
    v_cook = np.zeros(n, dtype=np.float32)
    v_total = np.zeros(n, dtype=np.float32)
    v_difficulty = np.zeros(n, dtype=np.int8)
    v_steps = np.zeros(n, dtype=np.int8)
    
    recipe_names = []
    
    for i, recipe in enumerate(recipes):
        recipe_names.append(recipe.get('name', f'Recipe_{i}'))
        
        # Get instructions
        instructions = recipe.get('instructions', [])
        if isinstance(instructions, str):
            instructions = [instructions]
        
        # Extract methods
        methods = extract_methods(instructions)
        for m in methods:
            if m in METHOD_INDEX:
                R_method[i, METHOD_INDEX[m]] = 1
        
        # Extract equipment
        equipment = extract_equipment(instructions)
        for e in equipment:
            if e in EQUIP_INDEX:
                R_equip[i, EQUIP_INDEX[e]] = 1
        
        # Extract techniques
        techniques = extract_techniques(instructions)
        for t in techniques:
            if t in TECH_INDEX:
                R_tech[i, TECH_INDEX[t]] = 1
        
        # Category
        cat = recipe.get('category', '').lower()
        if cat in CAT_INDEX:
            R_cat[i, CAT_INDEX[cat]] = 1
        
        # Times
        v_prep[i] = parse_time(recipe.get('prep_time'))
        v_cook[i] = parse_time(recipe.get('cook_time'))
        v_total[i] = parse_time(recipe.get('total_time'))
        
        # Difficulty
        diff = recipe.get('difficulty', '').lower()
        v_difficulty[i] = DIFFICULTY_MAP.get(diff, 0)
        
        # Number of steps
        v_steps[i] = len(instructions)
    
    return {
        'recipe_names': recipe_names,
        'R_method': R_method,
        'R_equip': R_equip,
        'R_tech': R_tech,
        'R_cat': R_cat,
        'v_prep': v_prep,
        'v_cook': v_cook,
        'v_total': v_total,
        'v_difficulty': v_difficulty,
        'v_steps': v_steps,
        'method_names': COOKING_METHODS,
        'equip_names': EQUIPMENT,
        'tech_names': TECHNIQUES,
        'cat_names': CATEGORIES,
    }


def print_comprehensive_info(data: dict):
    """Print information about all matrices."""
    n = len(data['recipe_names'])
    
    print("\n" + "=" * 80)
    print("COMPREHENSIVE RECIPE MATRIX SYSTEM")
    print("=" * 80)
    print(f"\nTotal Recipes: {n}")
    
    # Method matrix
    print("\n" + "-" * 80)
    print("1. COOKING METHODS MATRIX (R_method)")
    print("-" * 80)
    print(f"   Dimensions: {data['R_method'].shape}")
    print(f"   Methods: {', '.join(COOKING_METHODS)}")
    counts = data['R_method'].sum(axis=0)
    top_methods = sorted(zip(COOKING_METHODS, counts), key=lambda x: -x[1])[:5]
    print(f"   Most common: {', '.join([f'{m}({c})' for m,c in top_methods])}")
    
    # Equipment matrix
    print("\n" + "-" * 80)
    print("2. EQUIPMENT MATRIX (R_equip)")
    print("-" * 80)
    print(f"   Dimensions: {data['R_equip'].shape}")
    print(f"   Equipment: {', '.join(EQUIPMENT[:10])}...")
    counts = data['R_equip'].sum(axis=0)
    top_equip = sorted(zip(EQUIPMENT, counts), key=lambda x: -x[1])[:5]
    print(f"   Most common: {', '.join([f'{e}({c})' for e,c in top_equip])}")
    
    # Technique matrix
    print("\n" + "-" * 80)
    print("3. TECHNIQUE MATRIX (R_tech)")
    print("-" * 80)
    print(f"   Dimensions: {data['R_tech'].shape}")
    print(f"   Techniques: {', '.join(TECHNIQUES[:10])}...")
    counts = data['R_tech'].sum(axis=0)
    top_tech = sorted(zip(TECHNIQUES, counts), key=lambda x: -x[1])[:5]
    print(f"   Most common: {', '.join([f'{t}({c})' for t,c in top_tech])}")
    
    # Category matrix
    print("\n" + "-" * 80)
    print("4. CATEGORY MATRIX (R_cat)")
    print("-" * 80)
    print(f"   Dimensions: {data['R_cat'].shape}")
    counts = data['R_cat'].sum(axis=0)
    print(f"   Distribution: {', '.join([f'{c}:{int(n)}' for c,n in zip(CATEGORIES, counts)])}")
    
    # Time vectors
    print("\n" + "-" * 80)
    print("5. TIME VECTORS")
    print("-" * 80)
    print(f"   Prep Time:  min={data['v_prep'].min():.0f}, max={data['v_prep'].max():.0f}, avg={data['v_prep'].mean():.1f} min")
    print(f"   Cook Time:  min={data['v_cook'].min():.0f}, max={data['v_cook'].max():.0f}, avg={data['v_cook'].mean():.1f} min")
    print(f"   Total Time: min={data['v_total'].min():.0f}, max={data['v_total'].max():.0f}, avg={data['v_total'].mean():.1f} min")
    
    # Other vectors
    print("\n" + "-" * 80)
    print("6. OTHER VECTORS")
    print("-" * 80)
    diff_counts = Counter(data['v_difficulty'])
    print(f"   Difficulty: {dict(diff_counts)}")
    print(f"   Steps: min={data['v_steps'].min()}, max={data['v_steps'].max()}, avg={data['v_steps'].mean():.1f}")
    
    # Combined dimensions
    print("\n" + "=" * 80)
    print("COMBINED MATRIX DIMENSIONS")
    print("=" * 80)
    
    total_cols = (len(COOKING_METHODS) + len(EQUIPMENT) + len(TECHNIQUES) + 
                  len(CATEGORIES) + 5)  # 5 vectors
    print(f"""
    Individual Matrices:
    ├── R_method:     {n} × {len(COOKING_METHODS):3d}  (cooking methods)
    ├── R_equip:      {n} × {len(EQUIPMENT):3d}  (equipment)
    ├── R_tech:       {n} × {len(TECHNIQUES):3d}  (techniques)
    ├── R_cat:        {n} × {len(CATEGORIES):3d}  (categories)
    ├── v_prep:       {n} × 1    (prep time)
    ├── v_cook:       {n} × 1    (cook time)
    ├── v_total:      {n} × 1    (total time)
    ├── v_difficulty: {n} × 1    (difficulty)
    └── v_steps:      {n} × 1    (num steps)
    
    Combined Matrix: {n} × {total_cols} (concatenate all features)
    """)


def build_combined_matrix(data: dict) -> np.ndarray:
    """Concatenate all matrices into one combined feature matrix."""
    matrices = [
        data['R_method'].astype(np.float32),
        data['R_equip'].astype(np.float32),
        data['R_tech'].astype(np.float32),
        data['R_cat'].astype(np.float32),
        data['v_prep'].reshape(-1, 1),
        data['v_cook'].reshape(-1, 1),
        data['v_total'].reshape(-1, 1),
        data['v_difficulty'].reshape(-1, 1).astype(np.float32),
        data['v_steps'].reshape(-1, 1).astype(np.float32),
    ]
    
    return np.hstack(matrices)


def export_comprehensive(data: dict, output_dir: str = None):
    """Export all matrices."""
    if output_dir is None:
        output_dir = Path(__file__).parent / "exports"
    else:
        output_dir = Path(output_dir)
    
    output_dir.mkdir(exist_ok=True)
    
    print("\n" + "=" * 80)
    print("EXPORTING COMPREHENSIVE MATRICES")
    print("=" * 80)
    
    # Save individual matrices
    np.save(output_dir / "method_matrix.npy", data['R_method'])
    np.save(output_dir / "equip_matrix.npy", data['R_equip'])
    np.save(output_dir / "tech_matrix.npy", data['R_tech'])
    np.save(output_dir / "category_matrix.npy", data['R_cat'])
    print("  ✓ Individual matrices: method, equip, tech, category")
    
    # Save vectors
    np.save(output_dir / "time_vectors.npy", np.column_stack([
        data['v_prep'], data['v_cook'], data['v_total']
    ]))
    np.save(output_dir / "difficulty_vector.npy", data['v_difficulty'])
    np.save(output_dir / "steps_vector.npy", data['v_steps'])
    print("  ✓ Vectors: time, difficulty, steps")
    
    # Combined matrix
    combined = build_combined_matrix(data)
    np.save(output_dir / "combined_features.npy", combined)
    print(f"  ✓ Combined matrix: {combined.shape}")
    
    # Feature names
    feature_names = (
        [f"method_{m}" for m in COOKING_METHODS] +
        [f"equip_{e}" for e in EQUIPMENT] +
        [f"tech_{t}" for t in TECHNIQUES] +
        [f"cat_{c}" for c in CATEGORIES] +
        ["prep_time", "cook_time", "total_time", "difficulty", "num_steps"]
    )
    np.save(output_dir / "feature_names.npy", np.array(feature_names))
    print(f"  ✓ Feature names: {len(feature_names)} features")
    
    # CSV export
    import csv
    with open(output_dir / "comprehensive_matrix.csv", 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['recipe'] + feature_names)
        for i, name in enumerate(data['recipe_names']):
            writer.writerow([name] + list(combined[i]))
    print("  ✓ CSV: comprehensive_matrix.csv")
    
    # Metadata JSON
    metadata = {
        "description": "Comprehensive Recipe Feature Matrix",
        "dimensions": {
            "recipes": len(data['recipe_names']),
            "total_features": len(feature_names),
        },
        "feature_groups": {
            "methods": {"count": len(COOKING_METHODS), "names": COOKING_METHODS},
            "equipment": {"count": len(EQUIPMENT), "names": EQUIPMENT},
            "techniques": {"count": len(TECHNIQUES), "names": TECHNIQUES},
            "categories": {"count": len(CATEGORIES), "names": CATEGORIES},
            "time": ["prep_time", "cook_time", "total_time"],
            "other": ["difficulty", "num_steps"],
        },
        "statistics": {
            "avg_methods_per_recipe": float(data['R_method'].sum(axis=1).mean()),
            "avg_equipment_per_recipe": float(data['R_equip'].sum(axis=1).mean()),
            "avg_techniques_per_recipe": float(data['R_tech'].sum(axis=1).mean()),
            "avg_total_time": float(data['v_total'].mean()),
            "avg_steps": float(data['v_steps'].mean()),
        }
    }
    with open(output_dir / "comprehensive_metadata.json", 'w') as f:
        json.dump(metadata, f, indent=2)
    print("  ✓ Metadata: comprehensive_metadata.json")
    
    print(f"\nAll files exported to: {output_dir}")


def demo():
    """Run demonstration."""
    # Load recipes
    recipes_path = Path(__file__).parent.parent / "backend" / "data" / "recipes.json"
    with open(recipes_path, 'r') as f:
        recipes = json.load(f)
    
    print(f"Loaded {len(recipes)} recipes")
    
    # Build all matrices
    data = build_comprehensive_matrices(recipes)
    
    # Print info
    print_comprehensive_info(data)
    
    # Show sample recipe breakdown
    print("\n" + "=" * 80)
    print("SAMPLE RECIPE BREAKDOWN")
    print("=" * 80)
    
    for i in [0, 3, 10]:
        if i < len(recipes):
            name = data['recipe_names'][i]
            print(f"\n{name}:")
            
            methods = [COOKING_METHODS[j] for j in np.where(data['R_method'][i])[0]]
            equip = [EQUIPMENT[j] for j in np.where(data['R_equip'][i])[0]]
            tech = [TECHNIQUES[j] for j in np.where(data['R_tech'][i])[0]]
            cat = [CATEGORIES[j] for j in np.where(data['R_cat'][i])[0]]
            
            print(f"  Methods: {methods or ['none detected']}")
            print(f"  Equipment: {equip or ['none detected']}")
            print(f"  Techniques: {tech[:8]}{'...' if len(tech) > 8 else ''}")
            print(f"  Category: {cat or ['unknown']}")
            print(f"  Time: prep={data['v_prep'][i]:.0f}m, cook={data['v_cook'][i]:.0f}m, total={data['v_total'][i]:.0f}m")
            print(f"  Difficulty: {data['v_difficulty'][i]}, Steps: {data['v_steps'][i]}")
    
    return data


if __name__ == "__main__":
    data = demo()
    export_comprehensive(data)
