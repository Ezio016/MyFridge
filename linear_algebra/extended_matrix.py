"""
Extended Recipe-Ingredient Matrix

A comprehensive matrix with ~100 normalized ingredients extracted from
the recipe database. This provides a more complete representation for
linear algebra demonstrations.

Matrix dimensions: (n_recipes × ~100 ingredients)
"""

import json
import re
import numpy as np
from pathlib import Path

# ============================================================
# EXTENDED INGREDIENT LIST (~100 Basic Ingredients)
# Organized by food category
# ============================================================

EXTENDED_INGREDIENTS = {
    # ==================== PROTEINS (20) ====================
    "proteins": [
        "chicken",      # chicken, chicken breast, chicken thigh
        "beef",         # beef, steak, ground beef, sirloin
        "pork",         # pork, ham
        "lamb",         # lamb, lamb mince
        "bacon",        # bacon, rashers
        "sausage",      # sausage, sausages, chorizo
        "fish",         # fish, white fish, salmon, tuna, cod
        "shrimp",       # shrimp, prawns, king prawns
        "squid",        # squid, calamari
        "clams",        # clams, mussels, shellfish
        "eggs",         # egg, eggs, egg yolks, egg whites
        "tofu",         # tofu
        "duck",         # duck
        "turkey",       # turkey
        "liver",        # liver, chicken liver
        "mince",        # mince, ground meat
        "anchovy",      # anchovies
        "sardines",     # sardines
        "crab",         # crab
        "lobster",      # lobster
    ],
    
    # ==================== DAIRY (12) ====================
    "dairy": [
        "milk",         # milk, whole milk
        "butter",       # butter, unsalted butter
        "cream",        # cream, heavy cream, double cream, sour cream
        "cheese",       # cheese, cheddar, parmesan
        "mozzarella",   # mozzarella
        "feta",         # feta
        "ricotta",      # ricotta
        "yogurt",       # yogurt, greek yogurt
        "creme_fraiche",# creme fraiche
        "goat_cheese",  # goat cheese
        "gruyere",      # gruyere
        "parmesan",     # parmesan cheese
    ],
    
    # ==================== VEGETABLES (25) ====================
    "vegetables": [
        "onion",        # onion, onions, red onion, spring onion
        "garlic",       # garlic, garlic cloves
        "tomato",       # tomato, tomatoes, cherry tomatoes, plum tomatoes
        "potato",       # potato, potatoes
        "carrot",       # carrot, carrots
        "celery",       # celery
        "pepper",       # bell pepper, red pepper, green pepper
        "chili",        # chili, chilli, red chilli, green chilli
        "mushroom",     # mushroom, mushrooms
        "spinach",      # spinach
        "broccoli",     # broccoli
        "cabbage",      # cabbage, red cabbage
        "lettuce",      # lettuce, leaves
        "cucumber",     # cucumber
        "zucchini",     # zucchini, courgette
        "eggplant",     # eggplant, aubergine
        "leek",         # leek, leeks
        "fennel",       # fennel
        "beetroot",     # beetroot, beets
        "peas",         # peas, green peas
        "green_beans",  # green beans, beans
        "corn",         # corn, sweetcorn
        "asparagus",    # asparagus
        "kale",         # kale
        "avocado",      # avocado
    ],
    
    # ==================== AROMATICS & HERBS (15) ====================
    "herbs": [
        "parsley",      # parsley
        "cilantro",     # cilantro, coriander (leaves)
        "basil",        # basil
        "thyme",        # thyme
        "rosemary",     # rosemary
        "oregano",      # oregano
        "mint",         # mint
        "dill",         # dill
        "bay_leaf",     # bay leaf, bay leaves
        "sage",         # sage
        "chives",       # chives
        "tarragon",     # tarragon
        "marjoram",     # marjoram
        "ginger",       # ginger, fresh ginger
        "lemongrass",   # lemongrass
    ],
    
    # ==================== GRAINS & CARBS (12) ====================
    "grains": [
        "rice",         # rice, basmati rice, jasmine rice
        "pasta",        # pasta, spaghetti, fettuccine, penne
        "noodles",      # noodles, rice noodles
        "bread",        # bread, baguette
        "flour",        # flour, plain flour, all-purpose flour
        "breadcrumbs",  # breadcrumbs
        "couscous",     # couscous
        "tortilla",     # tortilla, tortillas
        "pita",         # pita bread
        "oats",         # oats, oatmeal
        "cornmeal",     # cornmeal, polenta
        "pastry",       # pastry, puff pastry, filo pastry
    ],
    
    # ==================== OILS & FATS (6) ====================
    "oils": [
        "olive_oil",    # olive oil, extra virgin olive oil
        "vegetable_oil",# vegetable oil, canola oil
        "sesame_oil",   # sesame oil
        "coconut_oil",  # coconut oil
        "sunflower_oil",# sunflower oil
        "lard",         # lard
    ],
    
    # ==================== SEASONINGS & SPICES (20) ====================
    "seasonings": [
        "salt",         # salt, sea salt, kosher salt
        "black_pepper", # black pepper, pepper
        "sugar",        # sugar, caster sugar, brown sugar
        "paprika",      # paprika, smoked paprika
        "cumin",        # cumin, cumin seeds
        "cinnamon",     # cinnamon
        "coriander_seed",# coriander seeds (spice, not leaves)
        "turmeric",     # turmeric
        "cayenne",      # cayenne pepper, red pepper flakes
        "chili_powder", # chili powder
        "nutmeg",       # nutmeg
        "allspice",     # allspice
        "cardamom",     # cardamom
        "saffron",      # saffron
        "star_anise",   # star anise
        "cloves",       # cloves
        "garam_masala", # garam masala
        "curry_powder", # curry powder
        "mustard",      # mustard, mustard powder
        "vanilla",      # vanilla, vanilla extract
    ],
    
    # ==================== SAUCES & LIQUIDS (15) ====================
    "sauces": [
        "soy_sauce",    # soy sauce
        "fish_sauce",   # fish sauce
        "oyster_sauce", # oyster sauce
        "tomato_paste", # tomato paste, tomato puree
        "tomato_sauce", # tomato sauce, passata
        "vinegar",      # vinegar, wine vinegar, rice vinegar
        "lemon_juice",  # lemon juice, lemon
        "lime_juice",   # lime juice, lime
        "wine",         # wine, white wine, red wine
        "stock",        # stock, chicken stock, beef stock, vegetable stock
        "coconut_milk", # coconut milk
        "worcestershire",# worcestershire sauce
        "hot_sauce",    # hot sauce
        "honey",        # honey
        "maple_syrup",  # maple syrup
    ],
    
    # ==================== NUTS & SEEDS (8) ====================
    "nuts": [
        "almonds",      # almonds
        "walnuts",      # walnuts
        "peanuts",      # peanuts, peanut butter
        "cashews",      # cashews
        "pine_nuts",    # pine nuts
        "sesame_seeds", # sesame seeds
        "pecans",       # pecans
        "hazelnuts",    # hazelnuts
    ],
    
    # ==================== LEGUMES (6) ====================
    "legumes": [
        "chickpeas",    # chickpeas, garbanzo beans
        "lentils",      # lentils
        "black_beans",  # black beans
        "white_beans",  # white beans, cannellini
        "kidney_beans", # kidney beans
        "bean_sprouts", # bean sprouts
    ],
    
    # ==================== BAKING (6) ====================
    "baking": [
        "baking_powder",# baking powder
        "baking_soda",  # baking soda, bicarbonate
        "yeast",        # yeast
        "cornstarch",   # cornstarch, corn flour
        "cocoa",        # cocoa, cocoa powder
        "chocolate",    # chocolate
    ],
}

# Flatten to get full list
INGREDIENT_LIST = []
INGREDIENT_CATEGORIES = {}
for category, ingredients in EXTENDED_INGREDIENTS.items():
    for ing in ingredients:
        INGREDIENT_LIST.append(ing)
        INGREDIENT_CATEGORIES[ing] = category

N_INGREDIENTS = len(INGREDIENT_LIST)
INGREDIENT_INDEX = {ing: i for i, ing in enumerate(INGREDIENT_LIST)}


def normalize_to_extended(raw_ingredient: str) -> list[str]:
    """
    Map a raw ingredient string to matching extended ingredients.
    Returns list of matched ingredient names.
    """
    raw = raw_ingredient.lower()
    matches = []
    
    # Comprehensive mapping rules
    mappings = [
        # Proteins
        (r'\bchicken\b', 'chicken'),
        (r'\b(beef|steak|sirloin)\b', 'beef'),
        (r'\b(pork|ham)\b', 'pork'),
        (r'\blamb\b', 'lamb'),
        (r'\bbacon\b', 'bacon'),
        (r'\b(sausages?|chorizo)\b', 'sausage'),
        (r'\b(fish|salmon|tuna|cod|tilapia|white fish)\b', 'fish'),
        (r'\b(shrimp|prawns?|king prawns?)\b', 'shrimp'),
        (r'\bsquid\b', 'squid'),
        (r'\b(clams?|mussels?|shellfish)\b', 'clams'),
        (r'\beggs?\b', 'eggs'),
        (r'\btofu\b', 'tofu'),
        (r'\bduck\b', 'duck'),
        (r'\bturkey\b', 'turkey'),
        (r'\bliver\b', 'liver'),
        (r'\bmince\b', 'mince'),
        (r'\banchov', 'anchovy'),
        (r'\bsardines?\b', 'sardines'),
        (r'\bcrab\b', 'crab'),
        (r'\blobster\b', 'lobster'),
        
        # Dairy
        (r'\bmilk\b', 'milk'),
        (r'\bbutter\b', 'butter'),
        (r'\b(cream|double cream|heavy cream|sour cream)\b', 'cream'),
        (r'\bcheese\b', 'cheese'),
        (r'\bmozzarella\b', 'mozzarella'),
        (r'\bfeta\b', 'feta'),
        (r'\bricotta\b', 'ricotta'),
        (r'\b(yogurt|yoghurt)\b', 'yogurt'),
        (r'\bcreme fraiche\b', 'creme_fraiche'),
        (r'\bgoat.?s? cheese\b', 'goat_cheese'),
        (r'\bgruyere\b', 'gruyere'),
        (r'\bparmesan\b', 'parmesan'),
        
        # Vegetables
        (r'\bonions?\b', 'onion'),
        (r'\bgarlic\b', 'garlic'),
        (r'\b(tomato|tomatoes)\b', 'tomato'),
        (r'\b(potato|potatoes)\b', 'potato'),
        (r'\b(carrot|carrots)\b', 'carrot'),
        (r'\bcelery\b', 'celery'),
        (r'\b(bell pepper|pepper)\b(?!corn)', 'pepper'),
        (r'\b(chili|chilli|scotch bonnet)\b', 'chili'),
        (r'\bmushrooms?\b', 'mushroom'),
        (r'\bspinach\b', 'spinach'),
        (r'\bbroccoli\b', 'broccoli'),
        (r'\bcabbage\b', 'cabbage'),
        (r'\blettuce\b', 'lettuce'),
        (r'\bcucumber\b', 'cucumber'),
        (r'\b(zucchini|courgette)\b', 'zucchini'),
        (r'\b(eggplant|aubergine)\b', 'eggplant'),
        (r'\bleeks?\b', 'leek'),
        (r'\bfennel\b', 'fennel'),
        (r'\b(beetroot|beets?)\b', 'beetroot'),
        (r'\bpeas\b', 'peas'),
        (r'\bgreen beans?\b', 'green_beans'),
        (r'\b(corn|sweetcorn)\b(?!starch)', 'corn'),
        (r'\basparagus\b', 'asparagus'),
        (r'\bkale\b', 'kale'),
        (r'\bavocado\b', 'avocado'),
        
        # Herbs
        (r'\bparsley\b', 'parsley'),
        (r'\b(cilantro|coriander)\b(?! seed)', 'cilantro'),
        (r'\bbasil\b', 'basil'),
        (r'\bthyme\b', 'thyme'),
        (r'\brosemary\b', 'rosemary'),
        (r'\boregano\b', 'oregano'),
        (r'\bmint\b', 'mint'),
        (r'\bdill\b', 'dill'),
        (r'\bbay leaf|bay leaves\b', 'bay_leaf'),
        (r'\bsage\b', 'sage'),
        (r'\bchives\b', 'chives'),
        (r'\btarragon\b', 'tarragon'),
        (r'\bmarjoram\b', 'marjoram'),
        (r'\bginger\b', 'ginger'),
        (r'\blemongrass\b', 'lemongrass'),
        
        # Grains
        (r'\brice\b(?! vinegar| noodle| wine)', 'rice'),
        (r'\b(pasta|spaghetti|fettuccine|penne|macaroni)\b', 'pasta'),
        (r'\b(noodles?|rice noodles?)\b', 'noodles'),
        (r'\bbread\b', 'bread'),
        (r'\bflour\b', 'flour'),
        (r'\bbreadcrumbs?\b', 'breadcrumbs'),
        (r'\bcouscous\b', 'couscous'),
        (r'\btortillas?\b', 'tortilla'),
        (r'\bpita\b', 'pita'),
        (r'\boats\b', 'oats'),
        (r'\b(cornmeal|polenta)\b', 'cornmeal'),
        (r'\bpastry\b', 'pastry'),
        
        # Oils
        (r'\bolive oil\b', 'olive_oil'),
        (r'\b(vegetable oil|canola oil|cooking oil)\b', 'vegetable_oil'),
        (r'\bsesame oil\b', 'sesame_oil'),
        (r'\bcoconut oil\b', 'coconut_oil'),
        (r'\bsunflower oil\b', 'sunflower_oil'),
        (r'\blard\b', 'lard'),
        
        # Seasonings
        (r'\bsalt\b', 'salt'),
        (r'\b(black pepper|pepper)\b(?! bell| red| green)', 'black_pepper'),
        (r'\bsugar\b', 'sugar'),
        (r'\bpaprika\b', 'paprika'),
        (r'\bcumin\b', 'cumin'),
        (r'\bcinnamon\b', 'cinnamon'),
        (r'\bcoriander seed', 'coriander_seed'),
        (r'\bturmeric\b', 'turmeric'),
        (r'\b(cayenne|red pepper flakes?)\b', 'cayenne'),
        (r'\bchili powder\b', 'chili_powder'),
        (r'\bnutmeg\b', 'nutmeg'),
        (r'\ballspice\b', 'allspice'),
        (r'\bcardamom\b', 'cardamom'),
        (r'\bsaffron\b', 'saffron'),
        (r'\bstar anise\b', 'star_anise'),
        (r'\bcloves\b', 'cloves'),
        (r'\bgaram masala\b', 'garam_masala'),
        (r'\bcurry powder\b', 'curry_powder'),
        (r'\bmustard\b', 'mustard'),
        (r'\bvanilla\b', 'vanilla'),
        
        # Sauces
        (r'\bsoy sauce\b', 'soy_sauce'),
        (r'\bfish sauce\b', 'fish_sauce'),
        (r'\boyster sauce\b', 'oyster_sauce'),
        (r'\b(tomato paste|tomato puree)\b', 'tomato_paste'),
        (r'\b(tomato sauce|passata)\b', 'tomato_sauce'),
        (r'\bvinegar\b', 'vinegar'),
        (r'\blemon\b(?! grass)', 'lemon_juice'),
        (r'\blime\b', 'lime_juice'),
        (r'\bwine\b', 'wine'),
        (r'\bstock\b', 'stock'),
        (r'\bcoconut milk\b', 'coconut_milk'),
        (r'\bworcestershire\b', 'worcestershire'),
        (r'\bhot.?sauce\b', 'hot_sauce'),
        (r'\bhoney\b', 'honey'),
        (r'\bmaple syrup\b', 'maple_syrup'),
        
        # Nuts
        (r'\balmonds?\b', 'almonds'),
        (r'\bwalnuts?\b', 'walnuts'),
        (r'\b(peanuts?|peanut butter)\b', 'peanuts'),
        (r'\bcashews?\b', 'cashews'),
        (r'\bpine nuts?\b', 'pine_nuts'),
        (r'\bsesame seeds?\b', 'sesame_seeds'),
        (r'\bpecans?\b', 'pecans'),
        (r'\bhazelnuts?\b', 'hazelnuts'),
        
        # Legumes
        (r'\bchickpeas?\b', 'chickpeas'),
        (r'\blentils?\b', 'lentils'),
        (r'\bblack beans?\b', 'black_beans'),
        (r'\b(white beans?|cannellini)\b', 'white_beans'),
        (r'\bkidney beans?\b', 'kidney_beans'),
        (r'\bbean sprouts?\b', 'bean_sprouts'),
        
        # Baking
        (r'\bbaking powder\b', 'baking_powder'),
        (r'\b(baking soda|bicarbonate)\b', 'baking_soda'),
        (r'\byeast\b', 'yeast'),
        (r'\b(cornstarch|corn flour)\b', 'cornstarch'),
        (r'\bcocoa\b', 'cocoa'),
        (r'\bchocolate\b', 'chocolate'),
    ]
    
    for pattern, ingredient in mappings:
        if re.search(pattern, raw, re.IGNORECASE):
            if ingredient not in matches:
                matches.append(ingredient)
    
    return matches


def build_extended_matrix(recipes: list[dict]) -> tuple[np.ndarray, list[str]]:
    """Build the extended recipe-ingredient matrix."""
    n_recipes = len(recipes)
    matrix = np.zeros((n_recipes, N_INGREDIENTS), dtype=np.int8)
    recipe_names = []
    
    for i, recipe in enumerate(recipes):
        recipe_names.append(recipe.get('name', f'Recipe_{i}'))
        
        for ing_str in recipe.get('ingredients', []):
            matched = normalize_to_extended(ing_str)
            for ing in matched:
                if ing in INGREDIENT_INDEX:
                    col = INGREDIENT_INDEX[ing]
                    matrix[i, col] = 1
    
    return matrix, recipe_names


def build_inventory_vector(inventory_items: list[str]) -> np.ndarray:
    """Build an inventory vector for the extended ingredient list."""
    vector = np.zeros(N_INGREDIENTS, dtype=np.int8)
    
    for item in inventory_items:
        matched = normalize_to_extended(item)
        for ing in matched:
            if ing in INGREDIENT_INDEX:
                col = INGREDIENT_INDEX[ing]
                vector[col] = 1
    
    return vector


def print_matrix_info(matrix: np.ndarray, recipe_names: list[str]):
    """Print comprehensive matrix information."""
    print("\n" + "=" * 80)
    print("EXTENDED RECIPE-INGREDIENT MATRIX")
    print("=" * 80)
    print(f"\nMatrix dimensions: {matrix.shape[0]} recipes × {matrix.shape[1]} ingredients")
    
    print(f"\nIngredient Categories ({N_INGREDIENTS} total):")
    for category, ingredients in EXTENDED_INGREDIENTS.items():
        print(f"  {category.upper()}: {len(ingredients)} ingredients")
        print(f"    {', '.join(ingredients[:8])}{'...' if len(ingredients) > 8 else ''}")
    
    # Statistics
    print("\n" + "-" * 80)
    print("STATISTICS")
    print("-" * 80)
    
    non_zero = matrix.sum()
    total = matrix.size
    print(f"Total entries: {total:,}")
    print(f"Non-zero entries: {non_zero:,} ({100*non_zero/total:.1f}%)")
    print(f"Sparsity: {100*(1-non_zero/total):.1f}%")
    print(f"Average ingredients per recipe: {matrix.sum(axis=1).mean():.1f}")
    
    # Most common ingredients
    ing_counts = matrix.sum(axis=0)
    sorted_idx = np.argsort(ing_counts)[::-1]
    
    print(f"\nTop 20 Most Common Ingredients:")
    for rank, idx in enumerate(sorted_idx[:20], 1):
        ing = INGREDIENT_LIST[idx]
        count = ing_counts[idx]
        pct = 100 * count / len(recipe_names)
        category = INGREDIENT_CATEGORIES[ing]
        print(f"  {rank:2d}. {ing:<15} {count:3d} recipes ({pct:5.1f}%) [{category}]")
    
    # Category coverage
    print(f"\nCategory Coverage:")
    for category, ingredients in EXTENDED_INGREDIENTS.items():
        cat_cols = [INGREDIENT_INDEX[ing] for ing in ingredients]
        cat_sum = matrix[:, cat_cols].sum()
        cat_recipes = (matrix[:, cat_cols].sum(axis=1) > 0).sum()
        print(f"  {category:<12}: {cat_recipes:3d} recipes use at least one ({100*cat_recipes/len(recipe_names):.0f}%)")


def export_extended_matrix(output_dir: str = None):
    """Export the extended matrix in multiple formats."""
    if output_dir is None:
        output_dir = Path(__file__).parent / "exports"
    else:
        output_dir = Path(output_dir)
    
    output_dir.mkdir(exist_ok=True)
    
    # Load recipes
    recipes_path = Path(__file__).parent.parent / "backend" / "data" / "recipes.json"
    with open(recipes_path, 'r') as f:
        recipes = json.load(f)
    
    # Build matrix
    R, names = build_extended_matrix(recipes)
    
    print(f"\nBuilt extended matrix: {R.shape}")
    print_matrix_info(R, names)
    
    # Export files
    print("\n" + "=" * 80)
    print("EXPORTING FILES")
    print("=" * 80)
    
    # NumPy
    np.save(output_dir / "extended_matrix.npy", R)
    np.save(output_dir / "extended_recipe_names.npy", np.array(names))
    np.save(output_dir / "extended_ingredient_names.npy", np.array(INGREDIENT_LIST))
    print(f"  ✓ NumPy: extended_matrix.npy ({R.shape})")
    
    # CSV
    import csv
    with open(output_dir / "extended_matrix.csv", 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['recipe'] + INGREDIENT_LIST)
        for i, name in enumerate(names):
            writer.writerow([name] + list(map(int, R[i])))
    print(f"  ✓ CSV: extended_matrix.csv")
    
    # Metadata JSON
    metadata = {
        "description": "Extended Recipe-Ingredient Matrix",
        "dimensions": {"rows": len(names), "columns": N_INGREDIENTS},
        "ingredients": INGREDIENT_LIST,
        "categories": {cat: ings for cat, ings in EXTENDED_INGREDIENTS.items()},
        "statistics": {
            "total_recipes": len(names),
            "total_ingredients": N_INGREDIENTS,
            "non_zero_entries": int(R.sum()),
            "sparsity_percent": round(100 * (1 - R.sum() / R.size), 2),
            "avg_ingredients_per_recipe": round(R.sum(axis=1).mean(), 2),
        },
        "ingredient_frequencies": {
            INGREDIENT_LIST[i]: int(R[:, i].sum()) 
            for i in range(N_INGREDIENTS)
        }
    }
    with open(output_dir / "extended_metadata.json", 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"  ✓ Metadata: extended_metadata.json")
    
    # LaTeX sample (first 15 rows, first 20 columns)
    latex = []
    latex.append("% Extended Recipe-Ingredient Matrix (sample)")
    latex.append("% First 20 columns: " + ", ".join(INGREDIENT_LIST[:20]))
    latex.append("")
    latex.append("\\begin{equation}")
    latex.append("R_{\\text{extended}} = \\begin{bmatrix}")
    for i in range(min(12, len(names))):
        row_vals = [str(int(x)) for x in R[i, :20]]
        latex.append("  " + " & ".join(row_vals) + " \\\\")
    latex.append("\\end{bmatrix}")
    latex.append("\\end{equation}")
    
    with open(output_dir / "extended_matrix_sample.tex", 'w') as f:
        f.write("\n".join(latex))
    print(f"  ✓ LaTeX: extended_matrix_sample.tex")
    
    print(f"\nAll files exported to: {output_dir}")
    
    return R, names


def demo():
    """Run demonstration."""
    print("\n" + "=" * 80)
    print("EXTENDED MATRIX DEMO")
    print("=" * 80)
    
    # Load and build
    recipes_path = Path(__file__).parent.parent / "backend" / "data" / "recipes.json"
    with open(recipes_path, 'r') as f:
        recipes = json.load(f)
    
    R, names = build_extended_matrix(recipes)
    print_matrix_info(R, names)
    
    # Demo: Inventory matching
    print("\n" + "=" * 80)
    print("DEMO: RECIPE MATCHING WITH INVENTORY")
    print("=" * 80)
    
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
        "tomatoes",
        "parsley",
        "lemon",
    ]
    
    print(f"\nYour inventory ({len(sample_inventory)} items):")
    for item in sample_inventory:
        print(f"  - {item}")
    
    v = build_inventory_vector(sample_inventory)
    matched_ings = [INGREDIENT_LIST[i] for i in np.where(v)[0]]
    print(f"\nMatched to {len(matched_ings)} ingredients in matrix:")
    print(f"  {', '.join(matched_ings)}")
    
    # Compute scores
    scores = R @ v
    totals = R.sum(axis=1)
    totals = np.where(totals == 0, 1, totals)
    percentages = (scores / totals) * 100
    
    # Show top matches
    top_idx = np.argsort(percentages)[::-1][:15]
    
    print(f"\nTop 15 Recipe Matches:")
    print("-" * 70)
    print(f"{'Recipe':<45} {'Score':>6} {'Match%':>8}")
    print("-" * 70)
    for idx in top_idx:
        if scores[idx] > 0:
            print(f"{names[idx][:43]:<45} {int(scores[idx]):>6} {percentages[idx]:>7.1f}%")


if __name__ == "__main__":
    demo()
    print("\n")
    export_extended_matrix()
