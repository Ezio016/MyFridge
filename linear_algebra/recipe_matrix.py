#!/usr/bin/env python3
"""
Recipe Matrix Representation for Linear Algebra Class
======================================================

This module converts recipes into matrix form for demonstrating:
1. Matrix operations (addition, multiplication)
2. Cosine similarity (finding similar recipes)
3. SVD (dimensionality reduction)
4. Recommendation systems (matrix factorization)

Matrix Structure:
-----------------
- Recipe-Ingredient Matrix (R): Shape (n_recipes, n_ingredients)
  - R[i,j] = 1 if recipe i contains ingredient j, else 0
  - Can also use quantities for weighted matrix

- Inventory Vector (v): Shape (n_ingredients,)
  - v[j] = 1 if user has ingredient j, else 0

- Match Score: R @ v = vector of how many ingredients each recipe matches
"""

import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple
import re


def load_recipes(recipes_path: str = None) -> List[Dict]:
    """Load recipes from JSON file."""
    if recipes_path is None:
        recipes_path = Path(__file__).parent.parent / "backend" / "data" / "recipes.json"
    
    with open(recipes_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def extract_ingredient_name(ingredient_str: str) -> str:
    """
    Extract clean ingredient name from full ingredient string.
    
    Example: "2 cups all-purpose flour" -> "flour"
             "1/2 teaspoon salt" -> "salt"
    """
    # Remove quantities and measurements
    cleaned = re.sub(r'^[\d\s/½¼¾⅓⅔⅛]+', '', ingredient_str)
    cleaned = re.sub(r'\b(cups?|tablespoons?|teaspoons?|tbsp|tsp|oz|ounces?|pounds?|lbs?|grams?|kg|ml|liters?|pieces?|slices?|cloves?|cans?|packages?|bunche?s?)\b', '', cleaned, flags=re.IGNORECASE)
    
    # Remove parenthetical notes
    cleaned = re.sub(r'\([^)]*\)', '', cleaned)
    
    # Remove common descriptors
    cleaned = re.sub(r'\b(fresh|dried|chopped|minced|diced|sliced|grated|shredded|ground|whole|large|medium|small|ripe|optional|to taste|for serving|for garnish)\b', '', cleaned, flags=re.IGNORECASE)
    
    # Clean up
    cleaned = re.sub(r'\s+', ' ', cleaned).strip().lower()
    cleaned = re.sub(r'^[-,.\s]+|[-,.\s]+$', '', cleaned)
    
    return cleaned if cleaned else ingredient_str.lower()


def build_recipe_ingredient_matrix(recipes: List[Dict], binary: bool = True) -> Tuple[np.ndarray, List[str], List[str]]:
    """
    Build Recipe-Ingredient Matrix.
    
    Args:
        recipes: List of recipe dictionaries
        binary: If True, use 0/1 values. If False, could use quantities (future)
    
    Returns:
        matrix: numpy array of shape (n_recipes, n_ingredients)
        recipe_names: list of recipe names (row labels)
        ingredient_names: list of ingredient names (column labels)
    """
    # Extract all unique ingredients
    all_ingredients = set()
    for recipe in recipes:
        for ing in recipe.get('ingredients', []):
            clean_name = extract_ingredient_name(ing)
            if clean_name:
                all_ingredients.add(clean_name)
    
    # Sort for consistent ordering
    ingredient_names = sorted(list(all_ingredients))
    ingredient_to_idx = {ing: i for i, ing in enumerate(ingredient_names)}
    
    # Build matrix
    n_recipes = len(recipes)
    n_ingredients = len(ingredient_names)
    matrix = np.zeros((n_recipes, n_ingredients), dtype=np.float32)
    
    recipe_names = []
    for i, recipe in enumerate(recipes):
        recipe_names.append(recipe.get('name', f'Recipe_{i}'))
        for ing in recipe.get('ingredients', []):
            clean_name = extract_ingredient_name(ing)
            if clean_name in ingredient_to_idx:
                matrix[i, ingredient_to_idx[clean_name]] = 1.0
    
    return matrix, recipe_names, ingredient_names


def build_inventory_vector(inventory: List[str], ingredient_names: List[str]) -> np.ndarray:
    """
    Build inventory vector aligned with ingredient matrix columns.
    
    Args:
        inventory: List of ingredient names user has
        ingredient_names: Column labels from the matrix
    
    Returns:
        vector: numpy array of shape (n_ingredients,)
    """
    inventory_lower = {ing.lower() for ing in inventory}
    vector = np.zeros(len(ingredient_names), dtype=np.float32)
    
    for i, ing in enumerate(ingredient_names):
        if ing in inventory_lower:
            vector[i] = 1.0
        # Fuzzy match
        elif any(ing in inv or inv in ing for inv in inventory_lower):
            vector[i] = 1.0
    
    return vector


def compute_match_scores(R: np.ndarray, v: np.ndarray) -> np.ndarray:
    """
    Compute match scores using matrix-vector multiplication.
    
    score = R @ v
    
    Each score[i] = number of ingredients recipe i has that match inventory.
    
    This is a basic dot product operation!
    """
    return R @ v


def compute_match_percentages(R: np.ndarray, v: np.ndarray) -> np.ndarray:
    """
    Compute match percentage for each recipe.
    
    percentage[i] = (R[i] @ v) / sum(R[i]) * 100
    
    Shows what fraction of recipe ingredients are available.
    """
    scores = R @ v
    totals = R.sum(axis=1)
    totals = np.where(totals == 0, 1, totals)  # Avoid division by zero
    return (scores / totals) * 100


def cosine_similarity(R: np.ndarray) -> np.ndarray:
    """
    Compute pairwise cosine similarity between recipes.
    
    sim(a, b) = (a · b) / (||a|| * ||b||)
    
    Returns similarity matrix of shape (n_recipes, n_recipes)
    """
    # Normalize rows
    norms = np.linalg.norm(R, axis=1, keepdims=True)
    norms = np.where(norms == 0, 1, norms)
    R_normalized = R / norms
    
    # Similarity = R_norm @ R_norm.T
    return R_normalized @ R_normalized.T


def find_similar_recipes(similarity_matrix: np.ndarray, recipe_idx: int, recipe_names: List[str], top_k: int = 5) -> List[Tuple[str, float]]:
    """
    Find most similar recipes to a given recipe.
    """
    similarities = similarity_matrix[recipe_idx]
    # Get top k (excluding itself)
    top_indices = np.argsort(similarities)[::-1][1:top_k+1]
    
    return [(recipe_names[i], similarities[i]) for i in top_indices]


def svd_decomposition(R: np.ndarray, n_components: int = 10) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Perform SVD on the recipe matrix.
    
    R ≈ U @ Σ @ V^T
    
    - U: Recipe embeddings (n_recipes, n_components)
    - Σ: Singular values (importance of each component)
    - V^T: Ingredient embeddings (n_components, n_ingredients)
    
    This is the basis for many recommendation systems!
    """
    U, s, Vt = np.linalg.svd(R, full_matrices=False)
    
    # Truncate to n_components
    U = U[:, :n_components]
    s = s[:n_components]
    Vt = Vt[:n_components, :]
    
    return U, np.diag(s), Vt


def reconstruct_matrix(U: np.ndarray, S: np.ndarray, Vt: np.ndarray) -> np.ndarray:
    """
    Reconstruct matrix from SVD components.
    
    R_approx = U @ S @ Vt
    
    Demonstrates low-rank approximation!
    """
    return U @ S @ Vt


# ============================================================
# DEMO FUNCTIONS FOR CLASS
# ============================================================

def demo_basic_matrix():
    """Demo 1: Basic matrix construction and properties."""
    print("=" * 60)
    print("DEMO 1: Recipe-Ingredient Matrix")
    print("=" * 60)
    
    recipes = load_recipes()
    R, recipe_names, ingredient_names = build_recipe_ingredient_matrix(recipes)
    
    print(f"\nMatrix Shape: {R.shape}")
    print(f"  - {R.shape[0]} recipes (rows)")
    print(f"  - {R.shape[1]} unique ingredients (columns)")
    print(f"\nMatrix Properties:")
    print(f"  - Sparsity: {(R == 0).sum() / R.size * 100:.1f}% zeros")
    print(f"  - Average ingredients per recipe: {R.sum(axis=1).mean():.1f}")
    print(f"  - Most common ingredient appears in: {R.sum(axis=0).max():.0f} recipes")
    
    # Show a small submatrix
    print(f"\nSample 5x5 submatrix (first 5 recipes, first 5 ingredients):")
    print(f"Recipes: {recipe_names[:5]}")
    print(f"Ingredients: {ingredient_names[:5]}")
    print(R[:5, :5])
    
    return R, recipe_names, ingredient_names


def demo_matrix_multiplication():
    """Demo 2: Matrix-vector multiplication for matching."""
    print("\n" + "=" * 60)
    print("DEMO 2: Matrix-Vector Multiplication (Recipe Matching)")
    print("=" * 60)
    
    recipes = load_recipes()
    R, recipe_names, ingredient_names = build_recipe_ingredient_matrix(recipes)
    
    # Simulate inventory
    inventory = ['eggs', 'butter', 'flour', 'sugar', 'milk', 'salt', 'chicken', 'rice', 'onion', 'garlic']
    v = build_inventory_vector(inventory, ingredient_names)
    
    print(f"\nYour Inventory: {inventory}")
    print(f"Inventory Vector v shape: {v.shape}")
    print(f"Non-zero entries in v: {(v > 0).sum()}")
    
    # Matrix-vector multiplication
    print(f"\n🧮 Computing: scores = R @ v")
    scores = compute_match_scores(R, v)
    
    # Top matches
    top_indices = np.argsort(scores)[::-1][:10]
    print(f"\nTop 10 Recipes by Ingredient Match:")
    for i, idx in enumerate(top_indices, 1):
        percentage = compute_match_percentages(R, v)[idx]
        print(f"  {i}. {recipe_names[idx]}: {scores[idx]:.0f} matches ({percentage:.0f}%)")
    
    return scores


def demo_cosine_similarity():
    """Demo 3: Cosine similarity for finding similar recipes."""
    print("\n" + "=" * 60)
    print("DEMO 3: Cosine Similarity (Finding Similar Recipes)")
    print("=" * 60)
    
    recipes = load_recipes()
    R, recipe_names, ingredient_names = build_recipe_ingredient_matrix(recipes)
    
    print(f"\n🧮 Computing: similarity = (R_norm) @ (R_norm)^T")
    similarity = cosine_similarity(R)
    
    print(f"\nSimilarity Matrix Shape: {similarity.shape}")
    print(f"  - Each entry sim[i,j] = cosine similarity between recipe i and j")
    print(f"  - Values range from 0 (different) to 1 (identical)")
    
    # Find similar recipes for a specific recipe
    target_recipe = "Classic French Toast"
    if target_recipe in recipe_names:
        idx = recipe_names.index(target_recipe)
        similar = find_similar_recipes(similarity, idx, recipe_names, top_k=5)
        
        print(f"\nRecipes similar to '{target_recipe}':")
        for name, sim in similar:
            print(f"  - {name}: {sim:.3f}")
    
    return similarity


def demo_svd():
    """Demo 4: SVD decomposition and low-rank approximation."""
    print("\n" + "=" * 60)
    print("DEMO 4: SVD Decomposition")
    print("=" * 60)
    
    recipes = load_recipes()
    R, recipe_names, ingredient_names = build_recipe_ingredient_matrix(recipes)
    
    print(f"\n🧮 Computing: R = U @ Σ @ V^T")
    U, S, Vt = svd_decomposition(R, n_components=20)
    
    print(f"\nSVD Components:")
    print(f"  - U (recipe embeddings): {U.shape}")
    print(f"  - Σ (singular values): {S.shape}")
    print(f"  - V^T (ingredient embeddings): {Vt.shape}")
    
    # Singular values show importance
    print(f"\nTop 10 Singular Values (importance):")
    for i, s in enumerate(np.diag(S)[:10], 1):
        print(f"  {i}. σ_{i} = {s:.2f}")
    
    # Reconstruction error
    R_approx = reconstruct_matrix(U, S, Vt)
    error = np.linalg.norm(R - R_approx, 'fro')
    print(f"\nReconstruction Error (Frobenius norm): {error:.2f}")
    print(f"Original matrix norm: {np.linalg.norm(R, 'fro'):.2f}")
    print(f"Relative error: {error / np.linalg.norm(R, 'fro') * 100:.1f}%")
    
    return U, S, Vt


def demo_recommendation():
    """Demo 5: Simple recommendation using matrix operations."""
    print("\n" + "=" * 60)
    print("DEMO 5: Recipe Recommendation System")
    print("=" * 60)
    
    recipes = load_recipes()
    R, recipe_names, ingredient_names = build_recipe_ingredient_matrix(recipes)
    
    # User preferences (liked recipes)
    liked_recipes = ["Classic French Toast", "Simple Pasta Marinara", "Quick Fried Rice"]
    
    print(f"\nUser liked: {liked_recipes}")
    
    # Create user preference vector
    user_vector = np.zeros(len(recipe_names))
    for recipe in liked_recipes:
        if recipe in recipe_names:
            user_vector[recipe_names.index(recipe)] = 1
    
    # Use similarity to recommend
    similarity = cosine_similarity(R)
    
    # Recommendation score = sum of similarities to liked recipes
    recommendation_scores = similarity @ user_vector
    
    # Exclude already liked
    for recipe in liked_recipes:
        if recipe in recipe_names:
            recommendation_scores[recipe_names.index(recipe)] = -1
    
    # Top recommendations
    top_indices = np.argsort(recommendation_scores)[::-1][:10]
    
    print(f"\n🎯 Recommended Recipes:")
    for i, idx in enumerate(top_indices, 1):
        print(f"  {i}. {recipe_names[idx]} (score: {recommendation_scores[idx]:.3f})")
    
    return recommendation_scores


def run_all_demos():
    """Run all demonstrations."""
    print("\n" + "🍳" * 30)
    print("RECIPE MATRIX - LINEAR ALGEBRA DEMONSTRATIONS")
    print("🍳" * 30)
    
    demo_basic_matrix()
    demo_matrix_multiplication()
    demo_cosine_similarity()
    demo_svd()
    demo_recommendation()
    
    print("\n" + "=" * 60)
    print("ALL DEMOS COMPLETE!")
    print("=" * 60)


if __name__ == "__main__":
    run_all_demos()
