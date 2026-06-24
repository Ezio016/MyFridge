"""
Template Matrix for Recipe-Ingredient Representation

This module creates a standardized matrix with a fixed set of 30 basic ingredients.
Perfect for linear algebra demonstrations in classroom settings.

The matrix R has dimensions (n_recipes × 30) where:
- Each row represents a recipe
- Each column represents one of 30 standard ingredients
- R[i,j] = 1 if recipe i uses ingredient j, else 0
"""

import json
import re
import numpy as np
from pathlib import Path

# ============================================================
# STANDARD INGREDIENT LIST (30 Basic Ingredients)
# ============================================================
# These are the most common cooking ingredients, normalized

BASIC_INGREDIENTS = [
    # Proteins (6)
    "chicken",
    "beef",
    "pork",
    "fish",
    "eggs",
    "tofu",
    
    # Dairy (4)
    "milk",
    "butter",
    "cheese",
    "cream",
    
    # Vegetables (8)
    "onion",
    "garlic",
    "tomato",
    "potato",
    "carrot",
    "pepper",
    "mushroom",
    "spinach",
    
    # Grains & Carbs (4)
    "rice",
    "pasta",
    "bread",
    "flour",
    
    # Oils & Fats (2)
    "olive_oil",
    "vegetable_oil",
    
    # Seasonings (6)
    "salt",
    "sugar",
    "soy_sauce",
    "vinegar",
    "lemon",
    "ginger",
]

# Number of standard ingredients
N_INGREDIENTS = len(BASIC_INGREDIENTS)

# Create lookup for fast indexing
INGREDIENT_INDEX = {ing: i for i, ing in enumerate(BASIC_INGREDIENTS)}


def normalize_ingredient(raw_ingredient: str) -> list[str]:
    """
    Map a raw ingredient string to matching basic ingredients.
    Returns list of matched basic ingredient names (can match multiple).
    
    Examples:
        "2 chicken breasts" -> ["chicken"]
        "olive oil" -> ["olive_oil"]
        "eggs" -> ["eggs"]
        "parmesan cheese" -> ["cheese"]
    """
    raw = raw_ingredient.lower()
    matches = []
    
    # Mapping rules: (pattern, basic_ingredient)
    mappings = [
        # Proteins
        (r'\bchicken\b', 'chicken'),
        (r'\b(beef|steak|ground beef)\b', 'beef'),
        (r'\b(pork|bacon|ham|sausage|chorizo)\b', 'pork'),
        (r'\b(fish|salmon|tuna|cod|tilapia|shrimp|prawn)\b', 'fish'),
        (r'\beggs?\b', 'eggs'),
        (r'\btofu\b', 'tofu'),
        
        # Dairy
        (r'\bmilk\b', 'milk'),
        (r'\bbutter\b', 'butter'),
        (r'\bcheese\b', 'cheese'),
        (r'\b(cream|sour cream|heavy cream)\b', 'cream'),
        
        # Vegetables
        (r'\bonions?\b', 'onion'),
        (r'\bgarlic\b', 'garlic'),
        (r'\b(tomato|tomatoes)\b', 'tomato'),
        (r'\b(potato|potatoes)\b', 'potato'),
        (r'\b(carrot|carrots)\b', 'carrot'),
        (r'\b(pepper|bell pepper|peppers)\b', 'pepper'),
        (r'\bmushrooms?\b', 'mushroom'),
        (r'\bspinach\b', 'spinach'),
        
        # Grains
        (r'\brice\b', 'rice'),
        (r'\b(pasta|spaghetti|noodles|penne|fettuccine)\b', 'pasta'),
        (r'\bbread\b', 'bread'),
        (r'\bflour\b', 'flour'),
        
        # Oils
        (r'\bolive oil\b', 'olive_oil'),
        (r'\b(vegetable oil|canola oil|cooking oil)\b', 'vegetable_oil'),
        
        # Seasonings
        (r'\bsalt\b', 'salt'),
        (r'\bsugar\b', 'sugar'),
        (r'\bsoy sauce\b', 'soy_sauce'),
        (r'\bvinegar\b', 'vinegar'),
        (r'\blemon\b', 'lemon'),
        (r'\bginger\b', 'ginger'),
    ]
    
    for pattern, basic_ing in mappings:
        if re.search(pattern, raw):
            if basic_ing not in matches:
                matches.append(basic_ing)
    
    return matches


def build_template_matrix(recipes: list[dict]) -> tuple[np.ndarray, list[str]]:
    """
    Build a binary recipe-ingredient matrix using only the 30 basic ingredients.
    
    Args:
        recipes: List of recipe dictionaries with 'ingredients' field
        
    Returns:
        matrix: (n_recipes, 30) binary matrix
        recipe_names: List of recipe names corresponding to rows
    """
    n_recipes = len(recipes)
    matrix = np.zeros((n_recipes, N_INGREDIENTS), dtype=np.int8)
    recipe_names = []
    
    for i, recipe in enumerate(recipes):
        recipe_names.append(recipe.get('name', f'Recipe_{i}'))
        
        # Process all ingredients
        all_ings = recipe.get('ingredients', [])
        
        for ing_str in all_ings:
            matched = normalize_ingredient(ing_str)
            for basic_ing in matched:
                col = INGREDIENT_INDEX[basic_ing]
                matrix[i, col] = 1
    
    return matrix, recipe_names


def build_inventory_vector(inventory_items: list[str]) -> np.ndarray:
    """
    Build an inventory vector matching the 30 basic ingredients.
    
    Args:
        inventory_items: List of ingredient names in inventory
        
    Returns:
        vector: (30,) binary vector - 1 if you have it, 0 if not
    """
    vector = np.zeros(N_INGREDIENTS, dtype=np.int8)
    
    for item in inventory_items:
        matched = normalize_ingredient(item)
        for basic_ing in matched:
            col = INGREDIENT_INDEX[basic_ing]
            vector[col] = 1
    
    return vector


def compute_match_scores(R: np.ndarray, v: np.ndarray) -> np.ndarray:
    """
    Matrix-vector multiplication: scores = R @ v
    
    Each recipe gets a score = number of required ingredients you have.
    """
    return R @ v


def compute_match_percentages(R: np.ndarray, v: np.ndarray) -> np.ndarray:
    """
    Compute what % of each recipe's ingredients you have.
    """
    scores = R @ v
    totals = R.sum(axis=1)
    # Avoid division by zero
    totals = np.where(totals == 0, 1, totals)
    return (scores / totals) * 100


def print_matrix_preview(matrix: np.ndarray, recipe_names: list[str], n_recipes: int = 10):
    """Print a nice preview of the matrix."""
    print("\n" + "=" * 80)
    print("RECIPE-INGREDIENT TEMPLATE MATRIX")
    print("=" * 80)
    print(f"\nMatrix dimensions: {matrix.shape[0]} recipes × {matrix.shape[1]} ingredients")
    print(f"\nColumns (30 Basic Ingredients):")
    
    # Print ingredients in groups
    groups = [
        ("Proteins", BASIC_INGREDIENTS[0:6]),
        ("Dairy", BASIC_INGREDIENTS[6:10]),
        ("Vegetables", BASIC_INGREDIENTS[10:18]),
        ("Grains", BASIC_INGREDIENTS[18:22]),
        ("Oils", BASIC_INGREDIENTS[22:24]),
        ("Seasonings", BASIC_INGREDIENTS[24:30]),
    ]
    
    for group_name, ingredients in groups:
        print(f"  {group_name}: {', '.join(ingredients)}")
    
    print(f"\nFirst {n_recipes} recipes (rows):")
    print("-" * 80)
    
    # Header - abbreviated ingredient names
    header = "Recipe".ljust(30) + " | "
    abbrev = [ing[:3].upper() for ing in BASIC_INGREDIENTS]
    header += " ".join(abbrev)
    print(header)
    print("-" * 80)
    
    for i in range(min(n_recipes, len(recipe_names))):
        name = recipe_names[i][:28].ljust(30)
        row = " ".join(["1" if x else "." for x in matrix[i]])
        print(f"{name} | {row}")
    
    # Statistics
    print("\n" + "=" * 80)
    print("STATISTICS")
    print("=" * 80)
    print(f"Total recipes: {matrix.shape[0]}")
    print(f"Total ingredients tracked: {N_INGREDIENTS}")
    print(f"Non-zero entries: {matrix.sum()} / {matrix.size} ({100*matrix.sum()/matrix.size:.1f}%)")
    print(f"Average ingredients per recipe: {matrix.sum(axis=1).mean():.1f}")
    
    # Most common ingredients
    ing_counts = matrix.sum(axis=0)
    sorted_idx = np.argsort(ing_counts)[::-1]
    print(f"\nMost common basic ingredients:")
    for idx in sorted_idx[:10]:
        print(f"  {BASIC_INGREDIENTS[idx]}: {ing_counts[idx]} recipes ({100*ing_counts[idx]/len(recipe_names):.1f}%)")


def export_latex_matrix(matrix: np.ndarray, recipe_names: list[str], 
                        n_recipes: int = 8, filepath: str = None) -> str:
    """Export a small portion as LaTeX for class handouts."""
    latex = []
    latex.append("% Recipe-Ingredient Template Matrix")
    latex.append("% Columns: " + ", ".join(BASIC_INGREDIENTS[:15]))  # First 15 for space
    latex.append("")
    latex.append("\\begin{equation}")
    latex.append("R = \\begin{bmatrix}")
    
    for i in range(min(n_recipes, len(recipe_names))):
        row_vals = [str(int(x)) for x in matrix[i, :15]]  # First 15 columns
        latex.append("  " + " & ".join(row_vals) + " \\\\")
    
    latex.append("\\end{bmatrix}")
    latex.append("\\end{equation}")
    
    result = "\n".join(latex)
    
    if filepath:
        with open(filepath, 'w') as f:
            f.write(result)
        print(f"LaTeX saved to: {filepath}")
    
    return result


def demo_classroom():
    """Run a classroom demonstration."""
    print("\n" + "=" * 80)
    print("LINEAR ALGEBRA CLASSROOM DEMO: TEMPLATE MATRIX")
    print("=" * 80)
    
    # Load recipes
    recipes_path = Path(__file__).parent.parent / "backend" / "data" / "recipes.json"
    with open(recipes_path, 'r') as f:
        recipes = json.load(f)
    
    print(f"\nLoaded {len(recipes)} recipes from database")
    
    # Build template matrix
    R, names = build_template_matrix(recipes)
    
    # Show preview
    print_matrix_preview(R, names, n_recipes=15)
    
    # Demo: Inventory matching
    print("\n" + "=" * 80)
    print("DEMO: INVENTORY MATCHING (Matrix-Vector Multiplication)")
    print("=" * 80)
    
    # Sample inventory
    sample_inventory = [
        "chicken breast",
        "eggs",
        "onion",
        "garlic",
        "olive oil",
        "salt",
        "pepper",
        "rice",
        "butter",
    ]
    
    print(f"\nYour inventory: {sample_inventory}")
    
    v = build_inventory_vector(sample_inventory)
    print(f"\nInventory vector v (30 elements):")
    print(f"  {v}")
    print(f"  (Non-zero positions: {[BASIC_INGREDIENTS[i] for i in np.where(v)[0]]})")
    
    # Compute scores
    scores = compute_match_scores(R, v)
    percentages = compute_match_percentages(R, v)
    
    # Top matches
    top_idx = np.argsort(percentages)[::-1][:10]
    
    print(f"\nTop 10 Recipe Matches:")
    print("-" * 60)
    print(f"{'Recipe':<40} Score  Match%")
    print("-" * 60)
    for idx in top_idx:
        print(f"{names[idx][:38]:<40} {int(scores[idx]):>3}    {percentages[idx]:>5.1f}%")
    
    return R, names


def export_all(output_dir: str = None):
    """Export all matrix formats for classroom use."""
    if output_dir is None:
        output_dir = Path(__file__).parent / "exports"
    else:
        output_dir = Path(output_dir)
    
    output_dir.mkdir(exist_ok=True)
    
    # Load and build
    recipes_path = Path(__file__).parent.parent / "backend" / "data" / "recipes.json"
    with open(recipes_path, 'r') as f:
        recipes = json.load(f)
    
    R, names = build_template_matrix(recipes)
    
    # Export files
    print("\nExporting template matrix files...")
    
    # 1. NumPy format
    np.save(output_dir / "template_matrix.npy", R)
    np.save(output_dir / "recipe_names.npy", np.array(names))
    np.save(output_dir / "ingredient_names.npy", np.array(BASIC_INGREDIENTS))
    print(f"  ✓ NumPy arrays: template_matrix.npy, recipe_names.npy, ingredient_names.npy")
    
    # 2. CSV format
    import csv
    with open(output_dir / "template_matrix.csv", 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['recipe'] + BASIC_INGREDIENTS)
        for i, name in enumerate(names):
            writer.writerow([name] + list(map(int, R[i])))
    print(f"  ✓ CSV: template_matrix.csv")
    
    # 3. LaTeX (small sample)
    export_latex_matrix(R, names, n_recipes=10, 
                       filepath=str(output_dir / "template_matrix_sample.tex"))
    
    # 4. JSON metadata
    metadata = {
        "description": "Recipe-Ingredient Template Matrix",
        "dimensions": {
            "rows": len(names),
            "columns": N_INGREDIENTS,
        },
        "ingredients": BASIC_INGREDIENTS,
        "ingredient_groups": {
            "proteins": BASIC_INGREDIENTS[0:6],
            "dairy": BASIC_INGREDIENTS[6:10],
            "vegetables": BASIC_INGREDIENTS[10:18],
            "grains": BASIC_INGREDIENTS[18:22],
            "oils": BASIC_INGREDIENTS[22:24],
            "seasonings": BASIC_INGREDIENTS[24:30],
        },
        "statistics": {
            "total_recipes": len(names),
            "non_zero_entries": int(R.sum()),
            "sparsity_percent": round(100 * (1 - R.sum() / R.size), 2),
            "avg_ingredients_per_recipe": round(R.sum(axis=1).mean(), 2),
        }
    }
    with open(output_dir / "template_metadata.json", 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"  ✓ Metadata: template_metadata.json")
    
    print(f"\nAll files exported to: {output_dir}")
    
    return R, names


if __name__ == "__main__":
    # Run classroom demo
    demo_classroom()
    
    # Export all formats
    print("\n" + "=" * 80)
    export_all()
