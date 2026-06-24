"""
Recipe Tensor Representation

Each recipe is a unique matrix where:
- ROWS = Processing methods (how you cook/prepare)
- COLUMNS = Ingredients (what you use)
- CELL VALUE = 1 if that method is applied to that ingredient

This creates a 3D tensor: (n_recipes × n_methods × n_ingredients)
Or viewed as n unique matrices, one per recipe.

Example for "Fried Rice":
                    rice  egg  onion  garlic  soy_sauce  oil
    stir_fry    [    1     0     1      1        0        1  ]
    scramble    [    0     1     0      0        0        0  ]
    chop        [    0     0     1      1        0        0  ]
    season      [    1     0     0      0        1        0  ]
    heat        [    0     0     0      0        0        1  ]

This matrix uniquely identifies the recipe!
"""

import json
from pathlib import Path

# ============================================================
# PROCESSING METHODS (ROWS) - 20 methods
# ============================================================
PROCESSING_METHODS = [
    # Heat methods
    "fry",          # pan frying
    "stir_fry",     # wok/high heat stirring
    "sauté",        # quick cook in fat
    "boil",         # cook in boiling water
    "simmer",       # gentle boiling
    "steam",        # steam cooking
    "bake",         # oven baking
    "roast",        # oven roasting
    "grill",        # direct heat grilling
    "broil",        # top-down heat
    
    # Prep methods
    "chop",         # cutting into pieces
    "slice",        # thin cuts
    "mince",        # very fine cutting
    "grate",        # grating/shredding
    "blend",        # blending/pureeing
    "mash",         # mashing
    "whisk",        # whisking/beating
    "marinate",     # soaking in marinade
    "season",       # adding spices/salt
    "raw",          # used raw/unprocessed
]

# ============================================================
# INGREDIENTS (COLUMNS) - 30 basic ingredients
# ============================================================
INGREDIENTS = [
    # Proteins
    "chicken", "beef", "pork", "fish", "eggs", "tofu",
    # Dairy
    "milk", "butter", "cheese", "cream",
    # Vegetables
    "onion", "garlic", "tomato", "potato", "carrot", 
    "pepper", "mushroom", "spinach",
    # Grains
    "rice", "pasta", "bread", "flour",
    # Oils & Liquids
    "olive_oil", "vegetable_oil", "stock", "wine",
    # Seasonings
    "salt", "sugar", "soy_sauce", "lemon",
]

N_METHODS = len(PROCESSING_METHODS)
N_INGREDIENTS = len(INGREDIENTS)

# Create index lookups
METHOD_IDX = {m: i for i, m in enumerate(PROCESSING_METHODS)}
ING_IDX = {ing: i for i, ing in enumerate(INGREDIENTS)}

# ============================================================
# KEYWORD MAPPINGS
# ============================================================

# Map raw ingredient strings to our standard ingredients
INGREDIENT_PATTERNS = {
    'chicken': ['chicken'],
    'beef': ['beef', 'steak', 'sirloin'],
    'pork': ['pork', 'bacon', 'ham', 'sausage'],
    'fish': ['fish', 'salmon', 'tuna', 'cod', 'tilapia'],
    'eggs': ['egg', 'eggs'],
    'tofu': ['tofu'],
    'milk': ['milk'],
    'butter': ['butter'],
    'cheese': ['cheese', 'parmesan', 'mozzarella', 'cheddar'],
    'cream': ['cream', 'sour cream'],
    'onion': ['onion', 'onions', 'shallot'],
    'garlic': ['garlic'],
    'tomato': ['tomato', 'tomatoes'],
    'potato': ['potato', 'potatoes'],
    'carrot': ['carrot', 'carrots'],
    'pepper': ['pepper', 'bell pepper', 'peppers'],
    'mushroom': ['mushroom', 'mushrooms'],
    'spinach': ['spinach'],
    'rice': ['rice'],
    'pasta': ['pasta', 'spaghetti', 'noodle', 'fettuccine'],
    'bread': ['bread', 'toast'],
    'flour': ['flour'],
    'olive_oil': ['olive oil'],
    'vegetable_oil': ['vegetable oil', 'oil', 'canola'],
    'stock': ['stock', 'broth'],
    'wine': ['wine'],
    'salt': ['salt'],
    'sugar': ['sugar'],
    'soy_sauce': ['soy sauce'],
    'lemon': ['lemon', 'lime', 'citrus'],
}

# Map instruction keywords to processing methods
METHOD_PATTERNS = {
    'fry': ['fry', 'frying', 'fried', 'pan-fry'],
    'stir_fry': ['stir fry', 'stir-fry', 'wok'],
    'sauté': ['sauté', 'saute', 'sautéing'],
    'boil': ['boil', 'boiling', 'boiled'],
    'simmer': ['simmer', 'simmering'],
    'steam': ['steam', 'steaming', 'steamed'],
    'bake': ['bake', 'baking', 'baked'],
    'roast': ['roast', 'roasting', 'roasted'],
    'grill': ['grill', 'grilling', 'grilled', 'bbq'],
    'broil': ['broil', 'broiling'],
    'chop': ['chop', 'chopped', 'chopping', 'cut', 'dice', 'diced'],
    'slice': ['slice', 'sliced', 'slicing'],
    'mince': ['mince', 'minced', 'mincing', 'finely chop'],
    'grate': ['grate', 'grated', 'shred', 'shredded'],
    'blend': ['blend', 'blended', 'puree', 'process'],
    'mash': ['mash', 'mashed', 'mashing'],
    'whisk': ['whisk', 'whisked', 'beat', 'beaten'],
    'marinate': ['marinate', 'marinated', 'marinade'],
    'season': ['season', 'seasoned', 'salt and pepper', 'add salt'],
    'raw': ['raw', 'fresh', 'uncooked', 'no cook'],
}


def identify_ingredient(ingredient_str):
    """Map an ingredient string to our standard ingredient."""
    ing_lower = ingredient_str.lower()
    for std_ing, patterns in INGREDIENT_PATTERNS.items():
        for pattern in patterns:
            if pattern in ing_lower:
                return std_ing
    return None


def extract_method_ingredient_pairs(instructions, ingredients_list):
    """
    Extract which methods are applied to which ingredients.
    Returns list of (method, ingredient) tuples.
    """
    pairs = []
    
    # Map raw ingredients to standard ones
    std_ingredients = set()
    for ing in ingredients_list:
        std = identify_ingredient(ing)
        if std:
            std_ingredients.add(std)
    
    # Analyze each instruction step
    if isinstance(instructions, list):
        steps = instructions
    else:
        steps = [instructions]
    
    for step in steps:
        step_lower = step.lower()
        
        # Find methods used in this step
        methods_in_step = []
        for method, patterns in METHOD_PATTERNS.items():
            for pattern in patterns:
                if pattern in step_lower:
                    methods_in_step.append(method)
                    break
        
        # Find ingredients mentioned in this step
        ings_in_step = []
        for std_ing in std_ingredients:
            # Check if this ingredient is mentioned in the step
            for pattern in INGREDIENT_PATTERNS.get(std_ing, [std_ing]):
                if pattern in step_lower:
                    ings_in_step.append(std_ing)
                    break
        
        # Create pairs: each method applies to each ingredient in this step
        for method in methods_in_step:
            for ing in ings_in_step:
                if (method, ing) not in pairs:
                    pairs.append((method, ing))
        
        # If we found methods but no specific ingredients, 
        # might be general instructions - skip
    
    return pairs


def build_recipe_matrix(recipe):
    """
    Build a unique matrix for a single recipe.
    Returns: (matrix as 2D list, method_names, ingredient_names)
    """
    # Initialize matrix (methods × ingredients)
    matrix = [[0 for _ in range(N_INGREDIENTS)] for _ in range(N_METHODS)]
    
    # Get recipe data
    instructions = recipe.get('instructions', [])
    ingredients_list = recipe.get('ingredients', [])
    
    # Extract method-ingredient pairs
    pairs = extract_method_ingredient_pairs(instructions, ingredients_list)
    
    # Fill the matrix
    for method, ingredient in pairs:
        if method in METHOD_IDX and ingredient in ING_IDX:
            row = METHOD_IDX[method]
            col = ING_IDX[ingredient]
            matrix[row][col] = 1
    
    # Also mark which ingredients are used (in 'raw' row if not processed)
    for ing_str in ingredients_list:
        std_ing = identify_ingredient(ing_str)
        if std_ing and std_ing in ING_IDX:
            col = ING_IDX[std_ing]
            # Check if this ingredient has any processing method
            has_method = any(matrix[r][col] == 1 for r in range(N_METHODS - 1))
            if not has_method:
                # Mark as 'raw' (last row)
                matrix[METHOD_IDX['raw']][col] = 1
    
    return matrix


def build_recipe_tensor(recipes):
    """
    Build a 3D tensor of all recipes.
    Shape: (n_recipes, n_methods, n_ingredients)
    """
    tensor = []
    recipe_names = []
    
    for recipe in recipes:
        matrix = build_recipe_matrix(recipe)
        tensor.append(matrix)
        recipe_names.append(recipe.get('name', 'Unknown'))
    
    return tensor, recipe_names


def print_recipe_matrix(recipe_name, matrix):
    """Pretty print a recipe matrix."""
    print(f"\n{'='*70}")
    print(f"RECIPE: {recipe_name}")
    print(f"{'='*70}")
    
    # Find which ingredients are used
    used_ings = []
    for col in range(N_INGREDIENTS):
        if any(matrix[row][col] == 1 for row in range(N_METHODS)):
            used_ings.append(col)
    
    if not used_ings:
        print("  (No method-ingredient relationships extracted)")
        return
    
    # Print header
    header = "Method".ljust(12) + " | "
    header += " ".join([INGREDIENTS[i][:6].center(6) for i in used_ings])
    print(header)
    print("-" * len(header))
    
    # Print rows (only methods that are used)
    for row in range(N_METHODS):
        if any(matrix[row][col] == 1 for col in used_ings):
            row_str = PROCESSING_METHODS[row].ljust(12) + " | "
            row_str += " ".join([
                "  1   " if matrix[row][col] == 1 else "  ·   " 
                for col in used_ings
            ])
            print(row_str)


def matrix_to_latex(recipe_name, matrix, used_ings):
    """Convert matrix to LaTeX format."""
    latex = []
    latex.append(f"% Recipe: {recipe_name}")
    latex.append("\\begin{equation}")
    latex.append(f"R_{{\\text{{{recipe_name[:15]}}}}} = \\begin{{bmatrix}}")
    
    for row in range(N_METHODS):
        if any(matrix[row][col] == 1 for col in used_ings):
            row_vals = [str(matrix[row][col]) for col in used_ings]
            latex.append("  " + " & ".join(row_vals) + " \\\\")
    
    latex.append("\\end{bmatrix}")
    latex.append("\\end{equation}")
    
    return "\n".join(latex)


def export_tensor(tensor, recipe_names, output_dir):
    """Export the tensor to various formats."""
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    
    print(f"\nExporting tensor ({len(tensor)} × {N_METHODS} × {N_INGREDIENTS})...")
    
    # Export as JSON (list of matrices)
    tensor_data = {
        "description": "Recipe Tensor - Each recipe is a unique matrix",
        "dimensions": {
            "recipes": len(tensor),
            "methods": N_METHODS,
            "ingredients": N_INGREDIENTS,
        },
        "method_labels": PROCESSING_METHODS,
        "ingredient_labels": INGREDIENTS,
        "recipe_names": recipe_names,
        "tensor": tensor,
    }
    
    with open(output_dir / "recipe_tensor.json", 'w') as f:
        json.dump(tensor_data, f, indent=2)
    print(f"  ✓ recipe_tensor.json")
    
    # Export individual matrices as separate JSON files (first 5)
    matrices_dir = output_dir / "individual_matrices"
    matrices_dir.mkdir(exist_ok=True)
    
    for i in range(min(10, len(tensor))):
        name_safe = recipe_names[i].replace(' ', '_').replace('/', '_')[:30]
        matrix_data = {
            "recipe": recipe_names[i],
            "methods": PROCESSING_METHODS,
            "ingredients": INGREDIENTS,
            "matrix": tensor[i],
        }
        with open(matrices_dir / f"{i:03d}_{name_safe}.json", 'w') as f:
            json.dump(matrix_data, f, indent=2)
    print(f"  ✓ individual_matrices/ (first 10 recipes)")
    
    # Export metadata
    # Count non-zero entries per recipe
    density_stats = []
    for i, matrix in enumerate(tensor):
        non_zero = sum(sum(row) for row in matrix)
        total = N_METHODS * N_INGREDIENTS
        density_stats.append({
            "recipe": recipe_names[i],
            "non_zero": non_zero,
            "density": non_zero / total if total > 0 else 0,
        })
    
    # Method usage across all recipes
    method_usage = [0] * N_METHODS
    for matrix in tensor:
        for row in range(N_METHODS):
            if any(matrix[row][col] == 1 for col in range(N_INGREDIENTS)):
                method_usage[row] += 1
    
    metadata = {
        "total_recipes": len(tensor),
        "matrix_dimensions": f"{N_METHODS} methods × {N_INGREDIENTS} ingredients",
        "tensor_shape": f"({len(tensor)}, {N_METHODS}, {N_INGREDIENTS})",
        "method_labels": PROCESSING_METHODS,
        "ingredient_labels": INGREDIENTS,
        "method_usage": {PROCESSING_METHODS[i]: method_usage[i] for i in range(N_METHODS)},
        "avg_density": sum(d["density"] for d in density_stats) / len(density_stats),
    }
    
    with open(output_dir / "tensor_metadata.json", 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"  ✓ tensor_metadata.json")
    
    print(f"\nFiles exported to: {output_dir}")


def demo():
    """Run demonstration."""
    # Load recipes
    recipes_path = Path(__file__).parent.parent / "backend" / "data" / "recipes.json"
    
    print("Loading recipes...")
    with open(recipes_path, 'r') as f:
        recipes = json.load(f)
    print(f"Loaded {len(recipes)} recipes")
    
    # Build tensor
    print("\nBuilding recipe tensor...")
    tensor, recipe_names = build_recipe_tensor(recipes)
    print(f"Tensor shape: ({len(tensor)}, {N_METHODS}, {N_INGREDIENTS})")
    
    # Show some examples
    print("\n" + "=" * 70)
    print("SAMPLE RECIPE MATRICES")
    print("Each recipe is a unique matrix: Methods × Ingredients")
    print("=" * 70)
    
    # Show first 3 recipes
    for i in [0, 2, 4]:
        if i < len(recipes):
            print_recipe_matrix(recipe_names[i], tensor[i])
    
    # Export
    export_tensor(tensor, recipe_names, Path(__file__).parent / "exports")
    
    # Summary
    print("\n" + "=" * 70)
    print("TENSOR REPRESENTATION SUMMARY")
    print("=" * 70)
    print(f"""
    Structure:
    - Each recipe = unique {N_METHODS} × {N_INGREDIENTS} matrix
    - Rows = Processing methods (how you cook)
    - Columns = Ingredients (what you use)
    - Cell = 1 if method applied to ingredient
    
    Total tensor: {len(tensor)} recipes × {N_METHODS} methods × {N_INGREDIENTS} ingredients
    
    Linear Algebra Applications:
    1. Matrix comparison: ||R_a - R_b||_F (Frobenius norm)
    2. Recipe similarity: trace(R_a^T @ R_b) / (||R_a|| ||R_b||)
    3. Tensor decomposition: Find latent cooking patterns
    4. Method-ingredient correlation: R^T @ R
    """)


if __name__ == "__main__":
    demo()
