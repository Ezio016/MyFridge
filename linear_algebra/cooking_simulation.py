"""
Cooking Simulation using Linear Algebra

This module models cooking as matrix transformations on ingredient vectors.

Key Concepts:
1. Each ingredient has a flavor vector (8D)
2. Each cooking method is a TRANSFORMATION MATRIX that changes flavors
3. Different ingredients react differently to the same cooking method
4. Final_Flavor = Cooking_Matrix × Ingredient_Vector

Linear Algebra Concepts Demonstrated:
- Matrix multiplication as transformation
- Rank and linear independence
- Eigenvalues (dominant flavor changes)
- Matrix composition (combining cooking steps)
"""

import json
from pathlib import Path

# ============================================================
# FLAVOR DIMENSIONS
# ============================================================
FLAVOR_DIMS = ["sweet", "salty", "sour", "bitter", "umami", "spicy", "fatty", "aromatic"]
N = len(FLAVOR_DIMS)

# ============================================================
# COOKING METHOD TRANSFORMATION MATRICES
# Each matrix transforms the flavor vector
# Matrix[i][j] = how much dimension j contributes to output dimension i
# ============================================================

# Identity matrix (no cooking / raw)
RAW = [
    [1, 0, 0, 0, 0, 0, 0, 0],  # sweet stays sweet
    [0, 1, 0, 0, 0, 0, 0, 0],  # salty stays salty
    [0, 0, 1, 0, 0, 0, 0, 0],  # etc...
    [0, 0, 0, 1, 0, 0, 0, 0],
    [0, 0, 0, 0, 1, 0, 0, 0],
    [0, 0, 0, 0, 0, 1, 0, 0],
    [0, 0, 0, 0, 0, 0, 1, 0],
    [0, 0, 0, 0, 0, 0, 0, 1],
]

# High heat searing/grilling - Maillard reaction
# Increases: umami, aromatic, bitter (char)
# Decreases: moisture-related freshness
GRILL = [
    [0.8, 0, 0, 0, 0.1, 0, 0, 0],   # sweet slightly reduced, some from umami
    [0, 1.1, 0, 0, 0, 0, 0, 0],     # salt concentrates
    [0, 0, 0.6, 0, 0, 0, 0, 0],     # sour reduces (acids evaporate)
    [0.1, 0, 0, 1.2, 0, 0, 0, 0.1], # bitter increases (char), some from sweet
    [0.2, 0, 0, 0, 1.4, 0, 0.1, 0], # umami increases significantly (Maillard)
    [0, 0, 0, 0, 0, 1.1, 0, 0],     # spicy slightly intensifies
    [0, 0, 0, 0, 0, 0, 0.7, 0],     # fat renders out
    [0.1, 0, 0, 0, 0.2, 0, 0, 1.5], # aromatic increases (smoke, char)
]

# Slow cooking/braising - long gentle heat
# Increases: umami, sweet (caramelization), fatty (melts into dish)
# Decreases: aromatic (volatile compounds escape)
BRAISE = [
    [1.3, 0, 0, 0, 0.1, 0, 0, 0],   # sweet increases (caramelization)
    [0, 1.2, 0, 0, 0, 0, 0, 0],     # salt concentrates
    [0, 0, 0.7, 0, 0, 0, 0, 0],     # sour reduces
    [0, 0, 0, 0.9, 0, 0, 0, 0],     # bitter slightly reduces
    [0.1, 0, 0, 0, 1.5, 0, 0.2, 0], # umami increases a lot
    [0, 0, 0, 0, 0, 0.8, 0, 0],     # spicy mellows
    [0, 0, 0, 0, 0, 0, 1.3, 0],     # fatty increases (renders)
    [0, 0, 0, 0, 0, 0, 0, 0.6],     # aromatic decreases (volatiles escape)
]

# Boiling - water-based cooking
# Decreases: most water-soluble flavors leach out
# Neutral on: fat (doesn't mix with water)
BOIL = [
    [0.7, 0, 0, 0, 0, 0, 0, 0],     # sweet leaches
    [0.0, 0.6, 0, 0, 0, 0, 0, 0],   # salt leaches significantly
    [0, 0, 0.8, 0, 0, 0, 0, 0],     # sour reduces
    [0, 0, 0, 0.7, 0, 0, 0, 0],     # bitter reduces
    [0, 0, 0, 0, 0.8, 0, 0, 0],     # umami leaches
    [0, 0, 0, 0, 0, 0.9, 0, 0],     # spicy slightly reduces
    [0, 0, 0, 0, 0, 0, 1.0, 0],     # fat unchanged
    [0, 0, 0, 0, 0, 0, 0, 0.5],     # aromatic escapes with steam
]

# Steaming - gentle, retains nutrients
# Minimal changes, retains most properties
STEAM = [
    [0.95, 0, 0, 0, 0, 0, 0, 0],
    [0, 0.95, 0, 0, 0, 0, 0, 0],
    [0, 0, 0.9, 0, 0, 0, 0, 0],
    [0, 0, 0, 0.9, 0, 0, 0, 0],
    [0, 0, 0, 0, 1.0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0.95, 0, 0],
    [0, 0, 0, 0, 0, 0, 0.95, 0],
    [0, 0, 0, 0, 0, 0, 0, 0.8],     # some aromatic escapes
]

# Frying - high heat in fat
# Increases: fatty, aromatic, umami (Maillard)
# Creates: crispy texture (not in flavor vector but important)
FRY = [
    [0.9, 0, 0, 0, 0.1, 0, 0, 0],
    [0, 1.0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0.7, 0, 0, 0, 0, 0],
    [0, 0, 0, 1.1, 0, 0, 0, 0],     # slight bitter from browning
    [0.15, 0, 0, 0, 1.3, 0, 0.1, 0],# umami from Maillard
    [0, 0, 0, 0, 0, 1.0, 0, 0],
    [0, 0, 0, 0, 0, 0, 1.5, 0],     # significant fat absorption
    [0.1, 0, 0, 0, 0.1, 0, 0, 1.4], # aromatic increases
]

# Caramelization - sugar transformation
# Converts sweet to complex flavors
CARAMELIZE = [
    [0.5, 0, 0, 0, 0, 0, 0, 0],     # sweet reduces (transforms)
    [0, 1.1, 0, 0, 0, 0, 0, 0],
    [0, 0, 0.8, 0, 0, 0, 0, 0],
    [0.3, 0, 0, 1.3, 0, 0, 0, 0],   # bitter increases (from sweet)
    [0.2, 0, 0, 0, 1.2, 0, 0, 0],   # umami from sweet
    [0, 0, 0, 0, 0, 1.0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0.9, 0],
    [0.3, 0, 0, 0, 0, 0, 0, 1.5],   # aromatic from caramel
]

# Fermentation - microbial transformation
# Increases: umami, sour, aromatic
FERMENT = [
    [0.6, 0, 0, 0, 0, 0, 0, 0],     # sugars consumed
    [0, 1.2, 0, 0, 0, 0, 0, 0],
    [0.2, 0, 1.5, 0, 0, 0, 0, 0],   # sour increases significantly
    [0, 0, 0, 1.1, 0, 0, 0, 0],
    [0.1, 0, 0, 0, 1.6, 0, 0, 0],   # umami increases a lot
    [0, 0, 0, 0, 0, 1.0, 0, 0],
    [0, 0, 0, 0, 0, 0, 1.0, 0],
    [0.1, 0, 0.1, 0, 0.1, 0, 0, 1.4],# complex aromatics
]

# Smoking - wood smoke infusion
SMOKE = [
    [0.8, 0, 0, 0, 0, 0, 0, 0],
    [0, 1.1, 0, 0, 0, 0, 0, 0],
    [0, 0, 0.9, 0, 0, 0, 0, 0],
    [0, 0, 0, 1.4, 0, 0, 0, 0.2],   # bitter from smoke
    [0.1, 0, 0, 0, 1.3, 0, 0, 0.1],
    [0, 0, 0, 0, 0, 1.0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0.8, 0],
    [0, 0, 0, 0.1, 0.1, 0, 0, 1.8], # very aromatic (smoke)
]

COOKING_MATRICES = {
    "raw": RAW,
    "grill": GRILL,
    "braise": BRAISE,
    "boil": BOIL,
    "steam": STEAM,
    "fry": FRY,
    "caramelize": CARAMELIZE,
    "ferment": FERMENT,
    "smoke": SMOKE,
}

# ============================================================
# INGREDIENT-SPECIFIC REACTION MODIFIERS
# Some ingredients react more/less to certain cooking methods
# ============================================================
INGREDIENT_REACTIONS = {
    # Proteins - react strongly to Maillard
    "beef": {"grill": 1.3, "braise": 1.2, "smoke": 1.4},
    "chicken": {"grill": 1.2, "fry": 1.3, "braise": 1.1},
    "pork": {"braise": 1.3, "smoke": 1.5, "grill": 1.2},
    "fish": {"steam": 1.2, "grill": 1.1, "smoke": 1.3},
    "eggs": {"fry": 1.2, "boil": 1.0, "steam": 1.1},
    
    # Vegetables - react to caramelization
    "onion": {"caramelize": 1.5, "fry": 1.3, "braise": 1.2},
    "garlic": {"fry": 1.4, "grill": 1.2, "raw": 1.3},
    "tomato": {"braise": 1.3, "grill": 1.2, "raw": 1.1},
    "potato": {"fry": 1.4, "boil": 1.0, "grill": 1.2},
    "mushroom": {"fry": 1.4, "grill": 1.3, "braise": 1.2},
    
    # Others
    "sugar": {"caramelize": 2.0},
    "butter": {"braise": 1.2, "fry": 1.1},
}


def matrix_multiply(matrix, vector):
    """Multiply matrix by vector."""
    result = []
    for row in matrix:
        val = sum(row[i] * vector[i] for i in range(len(vector)))
        result.append(round(val, 3))
    return result


def apply_cooking(ingredient_flavor, cooking_method, ingredient_name=None):
    """
    Apply a cooking transformation to an ingredient's flavor vector.
    
    Final_Flavor = Cooking_Matrix × Ingredient_Vector × Reaction_Modifier
    """
    if cooking_method not in COOKING_MATRICES:
        cooking_method = "raw"
    
    matrix = COOKING_MATRICES[cooking_method]
    result = matrix_multiply(matrix, ingredient_flavor)
    
    # Apply ingredient-specific reaction modifier
    if ingredient_name:
        ing_lower = ingredient_name.lower()
        for ing_key, reactions in INGREDIENT_REACTIONS.items():
            if ing_key in ing_lower:
                if cooking_method in reactions:
                    modifier = reactions[cooking_method]
                    # Amplify the changes (not the base)
                    for i in range(len(result)):
                        change = result[i] - ingredient_flavor[i]
                        result[i] = ingredient_flavor[i] + (change * modifier)
                break
    
    return [round(v, 3) for v in result]


def calculate_matrix_rank(matrix):
    """
    Calculate the rank of a matrix using row reduction.
    Rank tells us how many linearly independent rows/columns.
    """
    # Simple rank calculation via elimination
    m = [row[:] for row in matrix]  # Copy
    rows, cols = len(m), len(m[0])
    rank = 0
    
    for col in range(cols):
        # Find pivot
        pivot_row = None
        for row in range(rank, rows):
            if abs(m[row][col]) > 0.001:
                pivot_row = row
                break
        
        if pivot_row is None:
            continue
        
        # Swap rows
        m[rank], m[pivot_row] = m[pivot_row], m[rank]
        
        # Eliminate below
        for row in range(rank + 1, rows):
            if abs(m[row][col]) > 0.001:
                factor = m[row][col] / m[rank][col]
                for j in range(cols):
                    m[row][j] -= factor * m[rank][j]
        
        rank += 1
    
    return rank


def analyze_cooking_matrix(cooking_method):
    """
    Analyze properties of a cooking transformation matrix.
    """
    if cooking_method not in COOKING_MATRICES:
        return None
    
    matrix = COOKING_MATRICES[cooking_method]
    rank = calculate_matrix_rank(matrix)
    
    # Diagonal dominance (how much each flavor is preserved)
    diagonal = [matrix[i][i] for i in range(N)]
    preservation = sum(diagonal) / N
    
    # Off-diagonal sum (how much cross-flavor transfer)
    off_diag = sum(matrix[i][j] for i in range(N) for j in range(N) if i != j)
    
    # Which flavors increase/decrease most
    changes = []
    for i, flavor in enumerate(FLAVOR_DIMS):
        row_sum = sum(matrix[i])
        changes.append((flavor, round(row_sum - 1, 2)))  # Deviation from identity
    
    changes.sort(key=lambda x: x[1], reverse=True)
    increases = [f for f, c in changes if c > 0.1]
    decreases = [f for f, c in changes if c < -0.1]
    
    return {
        "method": cooking_method,
        "rank": rank,
        "full_rank": rank == N,
        "preservation_score": round(preservation, 2),
        "cross_transfer": round(off_diag, 2),
        "increases": increases,
        "decreases": decreases,
        "is_reversible": rank == N,  # Full rank = invertible
    }


def compose_cooking_methods(methods):
    """
    Compose multiple cooking methods into one transformation.
    M_final = M_n × ... × M_2 × M_1
    
    Order matters! (Matrix multiplication is not commutative)
    """
    if not methods:
        return RAW
    
    result = COOKING_MATRICES.get(methods[0], RAW)
    
    for method in methods[1:]:
        m = COOKING_MATRICES.get(method, RAW)
        # Matrix multiplication: result = m × result
        new_result = []
        for i in range(N):
            row = []
            for j in range(N):
                val = sum(m[i][k] * result[k][j] for k in range(N))
                row.append(round(val, 3))
            new_result.append(row)
        result = new_result
    
    return result


def simulate_cooking(ingredients_with_flavors, cooking_steps):
    """
    Simulate cooking a dish with multiple ingredients and steps.
    
    Args:
        ingredients_with_flavors: dict of {ingredient: flavor_vector}
        cooking_steps: list of (cooking_method, ingredient_name or "all")
    
    Returns:
        Final combined flavor profile
    """
    # Start with ingredient flavors
    current_flavors = {ing: vec[:] for ing, vec in ingredients_with_flavors.items()}
    
    # Apply each cooking step
    for method, target in cooking_steps:
        if target == "all":
            for ing in current_flavors:
                current_flavors[ing] = apply_cooking(
                    current_flavors[ing], method, ing
                )
        elif target in current_flavors:
            current_flavors[target] = apply_cooking(
                current_flavors[target], method, target
            )
    
    # Sum all flavors for final dish
    final = [0.0] * N
    for flavor_vec in current_flavors.values():
        for i in range(N):
            final[i] += flavor_vec[i]
    
    return {
        "final_flavor": [round(v, 2) for v in final],
        "ingredient_contributions": current_flavors,
        "dimensions": FLAVOR_DIMS,
    }


def demo():
    """Demonstrate cooking simulation."""
    print("=" * 70)
    print("COOKING SIMULATION - Linear Algebra in Action")
    print("=" * 70)
    
    # Sample ingredient flavors
    ingredients = {
        "beef": [0.0, 0.1, 0.0, 0.0, 0.8, 0.0, 0.5, 0.2],
        "onion": [0.3, 0.0, 0.0, 0.0, 0.2, 0.1, 0.0, 0.6],
        "garlic": [0.0, 0.0, 0.0, 0.1, 0.3, 0.2, 0.0, 0.9],
        "mushroom": [0.0, 0.0, 0.0, 0.0, 0.8, 0.0, 0.0, 0.5],
    }
    
    print("\n1. RAW INGREDIENTS")
    print("-" * 50)
    for ing, vec in ingredients.items():
        print(f"  {ing}: {vec}")
    
    print("\n2. COOKING MATRIX ANALYSIS")
    print("-" * 50)
    for method in ["grill", "braise", "fry"]:
        analysis = analyze_cooking_matrix(method)
        print(f"\n  {method.upper()}:")
        print(f"    Rank: {analysis['rank']}/{N} (Full rank: {analysis['full_rank']})")
        print(f"    Preservation: {analysis['preservation_score']}")
        print(f"    Increases: {analysis['increases']}")
        print(f"    Decreases: {analysis['decreases']}")
    
    print("\n3. COOKING SIMULATION: Beef Stew")
    print("-" * 50)
    
    cooking_steps = [
        ("fry", "onion"),       # Sauté onions first
        ("fry", "garlic"),      # Add garlic
        ("grill", "beef"),      # Sear beef
        ("braise", "all"),      # Braise everything together
    ]
    
    print("  Cooking steps:")
    for i, (method, target) in enumerate(cooking_steps, 1):
        print(f"    {i}. {method} → {target}")
    
    result = simulate_cooking(ingredients, cooking_steps)
    
    print("\n  Final Flavor Profile:")
    for i, flavor in enumerate(FLAVOR_DIMS):
        val = result['final_flavor'][i]
        bar = "█" * int(val * 10)
        print(f"    {flavor:10}: {bar} ({val:.2f})")
    
    print("\n4. MATRIX COMPOSITION (Order Matters!)")
    print("-" * 50)
    
    # Fry then braise
    m1 = compose_cooking_methods(["fry", "braise"])
    # Braise then fry
    m2 = compose_cooking_methods(["braise", "fry"])
    
    test_vec = [0.5, 0.2, 0.1, 0.1, 0.5, 0.2, 0.3, 0.4]
    result1 = matrix_multiply(m1, test_vec)
    result2 = matrix_multiply(m2, test_vec)
    
    print("  Test vector:", test_vec)
    print(f"  Fry→Braise result: {result1}")
    print(f"  Braise→Fry result: {result2}")
    print(f"  Different? {result1 != result2} (AB ≠ BA)")


if __name__ == "__main__":
    demo()
