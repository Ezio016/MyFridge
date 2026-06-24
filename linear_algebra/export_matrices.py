#!/usr/bin/env python3
"""
Export Recipe Matrices for Linear Algebra Class
================================================

Exports matrices in various formats for use in class demonstrations.
"""

import json
import numpy as np
import csv
from pathlib import Path
from recipe_matrix import (
    load_recipes,
    build_recipe_ingredient_matrix,
    cosine_similarity,
    svd_decomposition
)


def export_to_csv(matrix: np.ndarray, row_labels: list, col_labels: list, filename: str):
    """Export matrix to CSV with row and column labels."""
    output_path = Path(__file__).parent / "exports" / filename
    output_path.parent.mkdir(exist_ok=True)
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        # Header row
        writer.writerow([''] + col_labels)
        # Data rows
        for i, row in enumerate(matrix):
            writer.writerow([row_labels[i]] + list(row))
    
    print(f"Exported: {output_path}")
    return output_path


def export_to_numpy(matrix: np.ndarray, filename: str):
    """Export matrix to .npy format."""
    output_path = Path(__file__).parent / "exports" / filename
    output_path.parent.mkdir(exist_ok=True)
    
    np.save(output_path, matrix)
    print(f"Exported: {output_path}")
    return output_path


def export_to_latex(matrix: np.ndarray, row_labels: list, col_labels: list, filename: str, max_size: int = 10):
    """Export small matrix to LaTeX format for slides."""
    output_path = Path(__file__).parent / "exports" / filename
    output_path.parent.mkdir(exist_ok=True)
    
    # Truncate if too large
    m = min(matrix.shape[0], max_size)
    n = min(matrix.shape[1], max_size)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("% Recipe-Ingredient Matrix (truncated)\n")
        f.write("% Rows: Recipes, Columns: Ingredients\n\n")
        
        f.write("\\begin{equation}\n")
        f.write("R = \\begin{pmatrix}\n")
        
        for i in range(m):
            row_str = " & ".join([f"{int(matrix[i,j])}" for j in range(n)])
            if i < m - 1:
                row_str += " \\\\"
            f.write(f"  {row_str}\n")
        
        f.write("\\end{pmatrix}\n")
        f.write("\\end{equation}\n\n")
        
        # Add labels as comments
        f.write(f"% Row labels: {row_labels[:m]}\n")
        f.write(f"% Column labels: {col_labels[:n]}\n")
    
    print(f"Exported: {output_path}")
    return output_path


def export_summary_stats(R: np.ndarray, recipe_names: list, ingredient_names: list, filename: str):
    """Export summary statistics for the matrix."""
    output_path = Path(__file__).parent / "exports" / filename
    output_path.parent.mkdir(exist_ok=True)
    
    stats = {
        "matrix_shape": {
            "rows (recipes)": R.shape[0],
            "columns (ingredients)": R.shape[1]
        },
        "sparsity": {
            "total_elements": int(R.size),
            "non_zero_elements": int((R > 0).sum()),
            "zero_elements": int((R == 0).sum()),
            "sparsity_percentage": float(f"{(R == 0).sum() / R.size * 100:.2f}")
        },
        "recipe_statistics": {
            "avg_ingredients_per_recipe": float(f"{R.sum(axis=1).mean():.2f}"),
            "min_ingredients": int(R.sum(axis=1).min()),
            "max_ingredients": int(R.sum(axis=1).max()),
            "std_ingredients": float(f"{R.sum(axis=1).std():.2f}")
        },
        "ingredient_statistics": {
            "avg_recipes_per_ingredient": float(f"{R.sum(axis=0).mean():.2f}"),
            "most_common_ingredient": ingredient_names[R.sum(axis=0).argmax()],
            "most_common_count": int(R.sum(axis=0).max()),
            "least_common_count": int(R.sum(axis=0).min())
        },
        "matrix_properties": {
            "rank": int(np.linalg.matrix_rank(R)),
            "frobenius_norm": float(f"{np.linalg.norm(R, 'fro'):.2f}"),
        }
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2)
    
    print(f"Exported: {output_path}")
    return stats


def export_small_example(n_recipes: int = 10, n_ingredients: int = 15):
    """
    Create and export a small example matrix for teaching.
    Manually curated for clarity.
    """
    # Small curated example
    recipe_names = [
        "French Toast",
        "Pancakes", 
        "Omelette",
        "Fried Rice",
        "Pasta",
        "Salad",
        "Smoothie",
        "Sandwich",
        "Soup",
        "Stir Fry"
    ]
    
    ingredient_names = [
        "eggs", "milk", "bread", "butter", "flour",
        "rice", "pasta", "chicken", "vegetables", "cheese",
        "tomato", "lettuce", "fruit", "oil", "salt"
    ]
    
    # Binary matrix: 1 if recipe uses ingredient
    R = np.array([
        # eggs milk bread butt flour rice pasta chkn vegg chee tom lett fruit oil salt
        [1,   1,   1,    1,   0,    0,   0,    0,   0,   0,   0,  0,   0,    0,  1],  # French Toast
        [1,   1,   0,    1,   1,    0,   0,    0,   0,   0,   0,  0,   0,    0,  1],  # Pancakes
        [1,   0,   0,    1,   0,    0,   0,    0,   1,   1,   0,  0,   0,    0,  1],  # Omelette
        [1,   0,   0,    0,   0,    1,   0,    1,   1,   0,   0,  0,   0,    1,  1],  # Fried Rice
        [0,   0,   0,    0,   0,    0,   1,    0,   0,   1,   1,  0,   0,    1,  1],  # Pasta
        [0,   0,   0,    0,   0,    0,   0,    1,   1,   0,   1,  1,   0,    1,  1],  # Salad
        [0,   1,   0,    0,   0,    0,   0,    0,   0,   0,   0,  0,   1,    0,  0],  # Smoothie
        [0,   0,   1,    1,   0,    0,   0,    1,   0,   1,   1,  1,   0,    0,  1],  # Sandwich
        [0,   0,   0,    0,   0,    0,   0,    1,   1,   0,   1,  0,   0,    0,  1],  # Soup
        [0,   0,   0,    0,   0,    1,   0,    1,   1,   0,   0,  0,   0,    1,  1],  # Stir Fry
    ], dtype=np.float32)
    
    output_dir = Path(__file__).parent / "exports"
    output_dir.mkdir(exist_ok=True)
    
    # Export small example
    export_to_csv(R, recipe_names, ingredient_names, "small_example.csv")
    export_to_numpy(R, "small_example.npy")
    export_to_latex(R, recipe_names, ingredient_names, "small_example.tex")
    
    # Also create an inventory vector example
    inventory = np.array([1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], dtype=np.float32)
    inventory_names = ["eggs", "milk", "bread", "butter", "salt"]
    
    with open(output_dir / "small_example_inventory.txt", 'w') as f:
        f.write("Inventory Vector v:\n")
        f.write(f"Items: {inventory_names}\n")
        f.write(f"Vector: {inventory.tolist()}\n\n")
        f.write("Matrix-Vector Product R @ v:\n")
        scores = R @ inventory
        for i, (recipe, score) in enumerate(zip(recipe_names, scores)):
            f.write(f"  {recipe}: {int(score)} matches\n")
    
    print(f"\nSmall example files created in {output_dir}/")
    return R, recipe_names, ingredient_names


def export_all():
    """Export all matrices and statistics."""
    print("=" * 60)
    print("EXPORTING RECIPE MATRICES")
    print("=" * 60)
    
    # Load full dataset
    recipes = load_recipes()
    R, recipe_names, ingredient_names = build_recipe_ingredient_matrix(recipes)
    
    print(f"\nFull Matrix: {R.shape[0]} recipes × {R.shape[1]} ingredients")
    
    # Export full matrix
    export_to_csv(R, recipe_names, ingredient_names, "full_recipe_matrix.csv")
    export_to_numpy(R, "full_recipe_matrix.npy")
    export_summary_stats(R, recipe_names, ingredient_names, "matrix_statistics.json")
    
    # Export similarity matrix
    sim = cosine_similarity(R)
    export_to_numpy(sim, "similarity_matrix.npy")
    export_to_csv(sim[:20, :20], recipe_names[:20], recipe_names[:20], "similarity_sample.csv")
    
    # Export SVD components
    U, S, Vt = svd_decomposition(R, n_components=20)
    export_to_numpy(U, "svd_U.npy")
    export_to_numpy(S, "svd_S.npy")
    export_to_numpy(Vt, "svd_Vt.npy")
    
    # Create small teaching example
    print("\n" + "-" * 40)
    print("Creating small teaching example...")
    export_small_example()
    
    print("\n" + "=" * 60)
    print("ALL EXPORTS COMPLETE!")
    print("=" * 60)


if __name__ == "__main__":
    export_all()
