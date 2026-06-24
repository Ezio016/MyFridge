"""Column-Vector Recipe Matrix: Ingredients as ROWS, Recipes as COLUMNS"""
import json, csv, re
from pathlib import Path

INGREDIENTS = [
    "chicken", "beef", "pork", "fish", "eggs", "bacon", "tofu",
    "milk", "butter", "cheese", "cream", "yogurt",
    "onion", "garlic", "tomato", "potato", "carrot", "pepper", "mushroom", "spinach",
    "rice", "pasta", "bread", "flour", "noodles", "tortilla",
    "salt", "sugar", "paprika", "cumin", "ginger", "basil",
    "olive_oil", "soy_sauce", "vinegar", "lemon", "stock",
]
ING_IDX = {ing: i for i, ing in enumerate(INGREDIENTS)}

def match(raw):
    raw = raw.lower()
    found = []
    for ing in INGREDIENTS:
        if ing.replace('_', ' ') in raw or ing in raw:
            found.append(ing)
    return found

def build(recipes):
    n_ing, n_rec = len(INGREDIENTS), len(recipes)
    M = [[0]*n_rec for _ in range(n_ing)]
    names = [r.get('name','') for r in recipes]
    for c, r in enumerate(recipes):
        for s in r.get('ingredients', []):
            for ing in match(s):
                M[ING_IDX[ing]][c] = 1
    return M, names

def main():
    with open(Path(__file__).parent.parent/"backend/data/recipes.json") as f:
        recipes = json.load(f)
    M, names = build(recipes)
    print(f"Matrix: {len(INGREDIENTS)} ingredients x {len(names)} recipes")
    print("Each COLUMN = one recipe, Each ROW = one ingredient")
    
    out = Path(__file__).parent/"exports"
    out.mkdir(exist_ok=True)
    with open(out/"column_matrix.csv", 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['ingredient'] + names)
        for i, ing in enumerate(INGREDIENTS):
            w.writerow([ing] + M[i])
    print(f"Exported: column_matrix.csv")

if __name__ == "__main__":
    main()
