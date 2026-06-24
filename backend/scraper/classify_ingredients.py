"""
Ingredient Classification System
Analyzes and classifies ingredients in recipes.

This implements a scoring-based algorithm to distinguish:
- main ingredients (a.k.a. essential / defining)
- secondary ingredients (supporting; commonly pantry/seasoning)
- optional ingredients (garnish, "to taste", "for serving", etc.)

Heuristics used (best-effort for recipe text, not FDA labels):
- Position in ingredient list (strong prior; earlier is more "main")
- Estimated weight/proportion (derived from parsed quantity + unit)
- Standards of Identity (SOI) for a small set of common foods
- Defining characteristic (ingredient tokens appear in recipe title)
"""

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

OPTIONAL_MARKERS = [
    "optional",
    "to taste",
    "for serving",
    "for garnish",
    "garnish",
    "if desired",
    "as needed",
]

# Very small SOI-ish rule set (best-effort for recipes)
# Key: trigger if recipe title contains the key (case-insensitive).
# Value: mandatory ingredient keywords (if present -> strong main signal).
SOI_RULES: Dict[str, List[str]] = {
    "mayonnaise": ["oil", "egg", "vinegar", "lemon"],
    "milk chocolate": ["cocoa", "cacao", "sugar", "milk"],
    "bread": ["flour", "water", "yeast", "salt"],
    "pasta": ["flour", "water", "egg"],
    "butter": ["cream", "salt"],
    # Dish archetypes (not FDA SOI, but "defining characteristic" helpers)
    "taco": ["tortilla"],
    "sandwich": ["bread"],
    "pizza": ["flour", "cheese", "tomato"],
    "omelet": ["egg"],
    "pancake": ["flour", "milk", "egg"],
    "french toast": ["bread", "egg"],
}

# Dish-specific optional topping overrides (heuristics).
# If recipe title contains the key, and an ingredient matches one of the keywords,
# treat it as optional unless it is explicitly title-defining.
DISH_OPTIONAL_OVERRIDES: Dict[str, List[str]] = {
    "taco": ["lettuce", "tomato", "cheese", "sour cream", "lime", "cilantro", "salsa", "avocado"],
    "burger": ["lettuce", "tomato", "onion", "pickle", "cheese", "ketchup", "mustard", "mayo"],
    "pizza": ["basil", "oregano", "chili", "pepper flakes", "parsley", "parmesan"],
}

# Unit conversions / approximations.
VOLUME_TO_ML = {
    "tsp": 4.92892,
    "teaspoon": 4.92892,
    "teaspoons": 4.92892,
    "tbsp": 14.7868,
    "tablespoon": 14.7868,
    "tablespoons": 14.7868,
    "cup": 240.0,
    "cups": 240.0,
    "ml": 1.0,
    "milliliter": 1.0,
    "milliliters": 1.0,
    "l": 1000.0,
    "liter": 1000.0,
    "liters": 1000.0,
}

WEIGHT_TO_G = {
    "g": 1.0,
    "gram": 1.0,
    "grams": 1.0,
    "kg": 1000.0,
    "kilogram": 1000.0,
    "kilograms": 1000.0,
    "oz": 28.3495,
    "ounce": 28.3495,
    "ounces": 28.3495,
    "lb": 453.592,
    "lbs": 453.592,
    "pound": 453.592,
    "pounds": 453.592,
}

# Count-like units (very approximate)
COUNT_TO_G = {
    "egg": 50.0,
    "eggs": 50.0,
    "clove": 3.0,
    "cloves": 3.0,
    "slice": 25.0,
    "slices": 25.0,
    "piece": 30.0,
    "pieces": 30.0,
    "can": 400.0,   # very rough; varies a lot
    "cans": 400.0,
    "tortilla": 30.0,
    "tortillas": 30.0,
    "wedge": 10.0,
    "wedges": 10.0,
}

# Grams per cup for common items (used to estimate density)
GRAMS_PER_CUP = {
    "all-purpose flour": 120.0,
    "flour": 120.0,
    "sugar": 200.0,
    "brown sugar": 220.0,
    "powdered sugar": 120.0,
    "butter": 227.0,
    "olive oil": 216.0,
    "milk": 245.0,
    "water": 240.0,
    "rice": 185.0,  # uncooked
}

STOPWORDS = {
    "and", "or", "the", "a", "an", "of", "to", "with", "for", "fresh", "optional",
    "taste", "serving", "garnish", "as", "needed", "plus", "more",
}

CATEGORY_KEYWORDS = {
    "protein": ["chicken", "beef", "pork", "lamb", "fish", "salmon", "tuna", "shrimp", "tofu", "tempeh", "egg"],
    "carb": ["pasta", "spaghetti", "noodle", "rice", "bread", "tortilla", "wrap", "pita", "potato", "quinoa", "oat"],
    "produce": ["tomato", "lettuce", "cucumber", "pepper", "carrot", "broccoli", "cauliflower", "zucchini", "spinach", "kale", "mushroom", "lemon", "lime", "onion", "garlic"],
    "dairy": ["milk", "cream", "cheese", "yogurt", "butter"],
    "condiment": ["soy sauce", "vinegar", "ketchup", "mustard", "mayo", "mayonnaise", "hot sauce", "sriracha"],
    "spice": ["cinnamon", "nutmeg", "ginger", "cloves", "pepper", "paprika", "cumin", "coriander", "chili", "oregano", "basil", "thyme", "rosemary"],
    "topping": ["maple syrup", "honey", "powdered sugar", "berries", "whipped cream", "ice cream", "for serving", "for garnish"],
}


def _normalize_text(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "")).strip().lower()


def _tokenize(s: str) -> List[str]:
    s = _normalize_text(s)
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    toks = [t for t in s.split() if t and t not in STOPWORDS and len(t) > 2]
    return toks


def _parse_number(num_str: str) -> Optional[float]:
    """
    Parse number strings like:
      "1", "1.5", "1/2", "1 1/2", "1-2"
    Returns float or None.
    """
    s = (num_str or "").strip()
    if not s:
        return None

    # ranges: "1-2" or "1 - 2"
    m = re.match(r"^(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)$", s)
    if m:
        a = float(m.group(1))
        b = float(m.group(2))
        return (a + b) / 2.0

    # mixed number: "1 1/2"
    m = re.match(r"^(\d+)\s+(\d+)\s*/\s*(\d+)$", s)
    if m:
        whole = float(m.group(1))
        num = float(m.group(2))
        den = float(m.group(3)) if float(m.group(3)) != 0 else 1.0
        return whole + (num / den)

    # fraction: "1/2"
    m = re.match(r"^(\d+)\s*/\s*(\d+)$", s)
    if m:
        num = float(m.group(1))
        den = float(m.group(2)) if float(m.group(2)) != 0 else 1.0
        return num / den

    # decimal/int
    try:
        return float(s)
    except ValueError:
        return None


def parse_ingredient_amount(ingredient_text: str) -> str:
    """
    Extract amount/quantity from ingredient string (best-effort).
    """
    text = ingredient_text or ""
    # IMPORTANT: keep this strict so we don't accidentally swallow the ingredient name.
    unit_re = r"(?:cups?|cup|tablespoons?|tbsp|teaspoons?|tsp|ounces?|oz|pounds?|lbs?|lb|grams?|g|kilograms?|kg|milliliters?|ml|liters?|l|slices?|slice|cloves?|clove|eggs?|egg|cans?|can)"
    amount_patterns = [
        # "1 1/2 cups", "1/4 cup", "2 tbsp", "1-2 tsp"
        rf"^((?:\d+\s+\d+/\d+|\d+/\d+|\d+(?:\.\d+)?(?:\s*-\s*\d+(?:\.\d+)?)?)\s*{unit_re})\b",
        # "4 large" (eggs), "2 small" (onions) -> we'll infer count units later
        r"^(\d+(?:\s+\d+/\d+)?\s*(?:large|medium|small))\b",
        r"^(a handful|a pinch|to taste|for serving|for garnish)",
    ]
    for pattern in amount_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return ""


def parse_ingredient_item(ingredient_text: str, amount: str) -> str:
    """
    Extract the ingredient 'item' name (without the amount prefix).
    """
    item = ingredient_text or ""
    if amount:
        item = item.replace(amount, "", 1).strip()

    # Remove parenthetical notes
    item = re.sub(r"\([^)]*\)", "", item).strip()

    # Remove some leading descriptors
    item = re.sub(
        r"^(fresh|frozen|dried|chopped|diced|sliced|minced|grated|shredded|ground|crushed|peeled)\s+",
        "",
        item,
        flags=re.IGNORECASE,
    )
    return item.strip()


def _parse_amount_to_qty_unit(amount: str) -> Tuple[Optional[float], Optional[str], Optional[str]]:
    """
    Parse an extracted amount string into (qty, unit, count_noun).
    - unit: normalized for weight/volume units where possible
    - count_noun: noun like 'eggs', 'cloves', 'slices' if detected
    """
    a = _normalize_text(amount)
    if not a:
        return (None, None, None)

    if a in {"to taste", "for serving", "for garnish", "a pinch", "a handful"}:
        return (None, a, None)

    # Try: "<number> <unit>"
    # Examples: "2 cups", "1 1/2 tbsp", "4 large"
    m = re.match(r"^(\d+\s+\d+/\d+|\d+/\d+|\d+(?:\.\d+)?(?:\s*-\s*\d+(?:\.\d+)?)?)\s*([a-zA-Z]+)?", a)
    if not m:
        return (None, None, None)

    qty = _parse_number(m.group(1))
    unit_raw = (m.group(2) or "").lower()

    # Normalize common unit aliases
    unit_map = {
        "tsp": "tsp",
        "teaspoon": "tsp",
        "teaspoons": "tsp",
        "tbsp": "tbsp",
        "tablespoon": "tbsp",
        "tablespoons": "tbsp",
        "cup": "cup",
        "cups": "cup",
        "oz": "oz",
        "ounce": "oz",
        "ounces": "oz",
        "g": "g",
        "gram": "g",
        "grams": "g",
        "kg": "kg",
        "lb": "lb",
        "lbs": "lb",
        "pound": "lb",
        "pounds": "lb",
        "ml": "ml",
        "l": "l",
        "liter": "l",
        "liters": "l",
        "slice": "slice",
        "slices": "slice",
        "clove": "clove",
        "cloves": "clove",
        "egg": "egg",
        "eggs": "egg",
        "can": "can",
        "cans": "can",
    }
    # adjectives are not units
    if unit_raw in {"large", "medium", "small"}:
        unit = None
    else:
        unit = unit_map.get(unit_raw, unit_raw or None)

    # Heuristic: if unit is a count noun, return it as count_noun too
    count_noun = unit if unit in {"egg", "clove", "slice", "can"} else None
    return (qty, unit, count_noun)


def _guess_category(item: str, original: str) -> str:
    txt = _normalize_text(f"{item} {original}")
    # Special-case powders (garlic powder != garlic clove)
    if "powder" in txt and ("garlic" in txt or "onion" in txt):
        return "spice"
    if "seasoning" in txt or "spice" in txt:
        return "spice"
    for cat, kws in CATEGORY_KEYWORDS.items():
        for kw in kws:
            if kw in txt:
                return cat
    return "main"


def _estimate_grams(item: str, qty: Optional[float], unit: Optional[str], original: str) -> Optional[float]:
    """
    Best-effort conversion to grams.
    Not perfect, but good enough to compare relative proportions within a recipe.
    """
    if qty is None or unit is None:
        # If we have a qty but no unit, try to infer from the ingredient item.
        if qty is None:
            return None
        item_norm = _normalize_text(item)
        if "egg" in item_norm:
            return qty * COUNT_TO_G["egg"]
        if "clove" in item_norm:
            return qty * COUNT_TO_G["clove"]
        if "slice" in item_norm:
            return qty * COUNT_TO_G["slice"]
        if "can" in item_norm:
            return qty * COUNT_TO_G["can"]
        if "tortilla" in item_norm:
            return qty * COUNT_TO_G["tortilla"]
        if "wedge" in item_norm:
            return qty * COUNT_TO_G["wedge"]
        return None

    # explicit "to taste"/serving markers -> no weight
    if unit in {"to taste", "for serving", "for garnish", "a pinch", "a handful"}:
        return None

    if unit in WEIGHT_TO_G:
        return qty * WEIGHT_TO_G[unit]

    if unit in {"egg", "clove", "slice", "can"}:
        return qty * COUNT_TO_G.get(unit, 30.0)

    # volume conversions
    if unit in VOLUME_TO_ML:
        ml = qty * VOLUME_TO_ML[unit]
        item_norm = _normalize_text(item)
        # pick best grams-per-cup match
        grams_per_cup = None
        for k, v in GRAMS_PER_CUP.items():
            if k in item_norm:
                grams_per_cup = v
                break
        if grams_per_cup is None:
            # default ~ water-like density
            return ml * 1.0
        # convert grams-per-cup to g/ml
        g_per_ml = grams_per_cup / 240.0
        return ml * g_per_ml

    return None


def _soi_mandatory_keywords_for_title(title: str) -> List[str]:
    t = _normalize_text(title)
    out: List[str] = []
    for trigger, mandatory in SOI_RULES.items():
        if trigger in t:
            out.extend(mandatory)
    return out


def _title_matches_ingredient(title: str, ingredient_item: str, ingredient_original: str) -> bool:
    title_toks = set(_tokenize(title))
    ing_toks = set(_tokenize(f"{ingredient_item} {ingredient_original}"))
    # if any meaningful token overlaps, treat as defining characteristic
    return len(title_toks.intersection(ing_toks)) > 0


def _has_optional_marker(ingredient_text: str) -> bool:
    s = _normalize_text(ingredient_text)
    return any(m in s for m in OPTIONAL_MARKERS)


def classify_ingredient_role(
    recipe_title: str,
    ingredient_text: str,
    ingredient_item: str,
    idx: int,
    grams: Optional[float],
    max_grams_in_recipe: Optional[float],
) -> Tuple[str, Dict[str, Any]]:
    """
    Return (role, debug_signals).
    role ∈ {'main','secondary','optional'}
    """
    signals: Dict[str, Any] = {
        "idx": idx,
        "grams": grams,
    }

    txt = _normalize_text(ingredient_text)

    # Hard optional markers
    if _has_optional_marker(txt):
        signals["marker_optional"] = True
        return ("optional", signals)

    # SOI mandatory components (strongest "main" signal)
    mandatory = _soi_mandatory_keywords_for_title(recipe_title)
    if mandatory:
        signals["soi_triggers"] = mandatory
        if any(k in txt for k in mandatory):
            signals["soi_mandatory_hit"] = True
            return ("main", signals)

    # Position prior: first few ingredients are more likely "main"
    # (In true FDA labels it's by weight; in recipes it's often by usage, but still correlates.)
    pos_score = max(0.0, 1.0 - (idx / 6.0))  # idx 0..6 maps ~1.0..0.0
    signals["pos_score"] = pos_score

    # Weight/proportion score (relative within recipe)
    weight_score = 0.0
    if grams is not None and max_grams_in_recipe and max_grams_in_recipe > 0:
        weight_score = min(1.0, grams / max_grams_in_recipe)
    signals["weight_score"] = weight_score

    # Defining characteristic: ingredient tokens appear in title
    title_match = _title_matches_ingredient(recipe_title, ingredient_item, ingredient_text)
    signals["title_match"] = title_match
    title_score = 0.35 if title_match else 0.0

    # Dish-specific optional toppings: e.g., in tacos lettuce/tomato/cheese are usually optional.
    title_norm = _normalize_text(recipe_title)
    for dish, opt_kws in DISH_OPTIONAL_OVERRIDES.items():
        if dish in title_norm and not title_match:
            if any(k in txt for k in opt_kws):
                signals["dish_optional_override"] = dish
                return ("optional", signals)

    # Small-amount heuristic (spices/seasoning tend not to be "main")
    small_amount_penalty = 0.0
    if grams is not None and max_grams_in_recipe and max_grams_in_recipe > 0:
        rel = grams / max_grams_in_recipe
        signals["rel_weight"] = rel
        if rel < 0.05 and ("tsp" in txt or "teaspoon" in txt or "tbsp" in txt or "tablespoon" in txt or "pinch" in txt):
            small_amount_penalty = 0.15
    signals["small_amount_penalty"] = small_amount_penalty

    # Category priors: proteins/carbs are often defining; spices rarely are.
    cat = _guess_category(ingredient_item, ingredient_text)
    cat_boost = 0.0
    if cat in {"protein", "carb"}:
        cat_boost = 0.20
    elif cat in {"produce", "dairy"}:
        cat_boost = 0.10
    elif cat in {"spice", "condiment"}:
        cat_boost = -0.05
    signals["category"] = cat
    signals["cat_boost"] = cat_boost

    # Main score: position + proportion + title match + priors
    main_score = (0.60 * pos_score) + (0.60 * weight_score) + title_score + cat_boost - small_amount_penalty
    signals["main_score"] = main_score

    # Cooking fats (oil/butter) are rarely defining unless very prominent or title-defining.
    # This prevents small amounts of oil from being promoted to "main" in dishes like tacos.
    if ("oil" in txt or "butter" in txt) and not title_match:
        rel = signals.get("rel_weight")
        if (rel is None or rel < 0.20) and pos_score < 0.50:
            signals["fat_demoted"] = True
            return ("secondary", signals)

    # Decision thresholds
    if main_score >= 0.60:
        return ("main", signals)

    # If it's very small relative amount and not title-defining, call it secondary (or optional if it's a garnish-like category)
    if grams is not None and max_grams_in_recipe and max_grams_in_recipe > 0:
        rel = grams / max_grams_in_recipe
        if rel < 0.03 and not title_match:
            # very tiny, but not explicitly optional -> secondary
            return ("secondary", signals)

    return ("secondary", signals)


def classify_recipe_ingredients(recipe, include_debug: bool = False):
    """
    Convert flat ingredient list to structured format with classification
    """
    if not isinstance(recipe.get('ingredients'), list):
        return recipe

    title = recipe.get("name") or recipe.get("title") or ""
    structured_ingredients: List[Dict[str, Any]] = []

    # First pass: parse + estimate grams
    parsed_rows: List[Dict[str, Any]] = []
    for idx, ing_text in enumerate(recipe["ingredients"]):
        if not isinstance(ing_text, str):
            continue

        amount = parse_ingredient_amount(ing_text)
        item = parse_ingredient_item(ing_text, amount)
        qty, unit, count_noun = _parse_amount_to_qty_unit(amount)
        grams = _estimate_grams(item, qty, unit, ing_text)
        category = _guess_category(item, ing_text)

        parsed_rows.append(
            {
                "idx": idx,
                "original": ing_text,
                "amount": amount if amount else "",
                "item": item if item else ing_text,
                "qty": qty,
                "unit": unit,
                "count_noun": count_noun,
                "est_grams": grams,
                "category": category,
            }
        )

    max_grams = max([r["est_grams"] for r in parsed_rows if isinstance(r.get("est_grams"), (int, float))] or [0.0])
    max_grams = max_grams if max_grams > 0 else None

    # Second pass: classify role using title + position + proportion + SOI
    pre_roles: List[Dict[str, Any]] = []
    for row in parsed_rows:
        role, signals = classify_ingredient_role(
            recipe_title=title,
            ingredient_text=row["original"],
            ingredient_item=row["item"],
            idx=row["idx"],
            grams=row.get("est_grams"),
            max_grams_in_recipe=max_grams,
        )
        pre_roles.append({"row": row, "role": role, "signals": signals})

    # Enforce a reasonable minimum number of "main" ingredients (based on your position/weight guidelines).
    # This helps when weights can't be estimated reliably for some recipes.
    non_optional = [x for x in pre_roles if x["role"] != "optional"]
    main_count = sum(1 for x in pre_roles if x["role"] == "main")
    desired_main = max(2, min(3, int(round(max(2, len(parsed_rows) * 0.25)))))

    if main_count < desired_main and non_optional:
        candidates: List[Tuple[float, Dict[str, Any]]] = []
        for x in non_optional:
            sig = x.get("signals") or {}
            score = float(sig.get("main_score") or 0.0)
            cat = sig.get("category")
            title_match = bool(sig.get("title_match"))
            grams = x["row"].get("est_grams")
            rel = sig.get("rel_weight")
            orig_txt = _normalize_text(x["row"].get("original", ""))
            # Avoid promoting pure spices unless title-defining or sizeable.
            if cat == "spice" and not title_match and (rel is None or rel < 0.10):
                continue
            # Avoid promoting small amounts of fats/oils unless title-defining or very prominent.
            if ("oil" in orig_txt or "butter" in orig_txt) and not title_match and (rel is None or rel < 0.20):
                continue
            candidates.append((score, x))

        candidates.sort(key=lambda t: t[0], reverse=True)
        promoted = 0
        for _, x in candidates:
            if main_count >= desired_main:
                break
            if x["role"] != "main":
                x["role"] = "main"
                x["signals"]["promoted_to_main"] = True
                main_count += 1
                promoted += 1

    # Build final structured ingredients
    for x in pre_roles:
        row = x["row"]
        role = x["role"]
        signals = x["signals"]

        # Map role -> existing classification field for backward compatibility.
        if role == "main":
            classification = "essential"
        elif role == "optional":
            classification = "optional"
        else:
            classification = "common"

        ing_obj: Dict[str, Any] = {
            "item": row["item"],
            "amount": row["amount"],
            "original": row["original"],
            "role": role,  # main/secondary/optional
            "classification": classification,  # essential/common/optional (backward compatible)
            "category": row.get("category") or "main",
        }

        # Debug-only / developer-facing fields (omit from production DB by default)
        if include_debug:
            ing_obj.update(
                {
                    "quantity": row.get("qty"),
                    "unit": row.get("unit"),
                    "est_grams": row.get("est_grams"),
                    "position": row["idx"],
                    "signals": signals,
                }
            )

        structured_ingredients.append(ing_obj)
    
    # Create new recipe with structured ingredients
    new_recipe = recipe.copy()
    new_recipe['ingredients_structured'] = structured_ingredients
    # Keep original for backward compatibility
    new_recipe['ingredients'] = recipe['ingredients']
    
    return new_recipe


def classify_all_recipes(input_file, output_file):
    """
    Process entire recipe database and add classifications
    """
    print(f"📖 Reading recipes from {input_file}")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        recipes = json.load(f)
    
    print(f"✅ Loaded {len(recipes)} recipes")
    print(f"🔍 Classifying ingredients...")
    
    classified_recipes = []
    stats = {"essential": 0, "common": 0, "optional": 0}
    role_stats = {"main": 0, "secondary": 0, "optional": 0}
    
    for i, recipe in enumerate(recipes):
        if (i + 1) % 50 == 0:
            print(f"  Processed {i + 1}/{len(recipes)} recipes...")
        
        classified_recipe = classify_recipe_ingredients(recipe)
        classified_recipes.append(classified_recipe)
        
        # Collect stats
        for ing in classified_recipe.get("ingredients_structured", []):
            stats[ing.get("classification", "common")] += 1
            role_stats[ing.get("role", "secondary")] += 1
    
    print(f"\n📊 Classification Statistics:")
    print(f"  Essential ingredients: {stats['essential']}")
    print(f"  Common ingredients: {stats['common']}")
    print(f"  Optional ingredients: {stats['optional']}")
    print(f"  Total ingredients: {sum(stats.values())}")
    print(f"\n📊 Role Statistics (main vs optional as requested):")
    print(f"  Main: {role_stats['main']}")
    print(f"  Secondary: {role_stats['secondary']}")
    print(f"  Optional: {role_stats['optional']}")
    
    # Save to output file
    print(f"\n💾 Saving to {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(classified_recipes, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Done! Classified {len(classified_recipes)} recipes")
    
    # Show example
    print(f"\n📝 Example classified recipe:")
    example = classified_recipes[0]
    print(f"  Recipe: {example['name']}")
    print(f"  Ingredients:")
    for ing in example.get('ingredients_structured', [])[:5]:
        print(f"    - {ing['original']}")
        print(f"      → Item: {ing['item']}, Role: {ing.get('role')}, Classification: {ing['classification']}, Category: {ing['category']}")


if __name__ == "__main__":
    # Paths
    script_dir = Path(__file__).parent
    data_dir = script_dir.parent / 'data'
    input_file = data_dir / 'recipes.json'
    output_file = data_dir / 'recipes.classified.json'
    
    # Backup original
    backup_file = data_dir / 'recipes.backup.json'
    if input_file.exists() and not backup_file.exists():
        import shutil
        print(f"📦 Creating backup at {backup_file}")
        shutil.copy(input_file, backup_file)
    
    # Classify all recipes
    classify_all_recipes(input_file, output_file)
    
    print(f"\n🎯 Next steps:")
    print(f"  1. Review {output_file}")
    print(f"  2. If satisfied, rename to recipes.json")
    print(f"  3. Update frontend to use 'ingredients_structured'")

