#!/usr/bin/env python3
"""
Export the entire recipe ingredient database to a detailed XML file for manual review/editing.

Usage:
  python export_ingredients_xml.py
  python export_ingredients_xml.py --output ../recipes_ingredients.xml
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import xml.etree.ElementTree as ET


def indent(elem: ET.Element, level: int = 0) -> None:
    """In-place pretty print indentation (Python 3.9+ compatible)."""
    i = "\n" + level * "  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        for child in elem:
            indent(child, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


def safe_text(v) -> str:
    if v is None:
        return ""
    return str(v)


def load_recipes(backend_dir: Path) -> list[dict]:
    recipes_file = backend_dir / "data" / "recipes.json"
    with open(recipes_file, "r", encoding="utf-8") as f:
        return json.load(f)


def build_xml(recipes: list[dict]) -> ET.ElementTree:
    root = ET.Element("recipeDatabase")
    root.set("version", "1.0")
    root.set("recipesCount", str(len(recipes)))

    for r in recipes:
        recipe_el = ET.SubElement(root, "recipe")
        recipe_el.set("id", safe_text(r.get("id")))

        ET.SubElement(recipe_el, "name").text = safe_text(r.get("name"))
        ET.SubElement(recipe_el, "category").text = safe_text(r.get("category"))
        ET.SubElement(recipe_el, "cuisine").text = safe_text(r.get("cuisine"))
        ET.SubElement(recipe_el, "prepTimeMinutes").text = safe_text(r.get("prep_time"))
        ET.SubElement(recipe_el, "cookTimeMinutes").text = safe_text(r.get("cook_time"))
        ET.SubElement(recipe_el, "totalTimeMinutes").text = safe_text(r.get("total_time"))
        ET.SubElement(recipe_el, "servings").text = safe_text(r.get("servings"))

        # Ingredients: prefer structured list; fallback to raw list.
        ingredients_el = ET.SubElement(recipe_el, "ingredients")
        structured = r.get("ingredients_structured")
        if isinstance(structured, list) and structured:
            for idx, ing in enumerate(structured):
                ing_el = ET.SubElement(ingredients_el, "ingredient")
                ing_el.set("index", str(idx))

                # Fields you’ll want when manually sorting
                ET.SubElement(ing_el, "original").text = safe_text(ing.get("original"))
                ET.SubElement(ing_el, "item").text = safe_text(ing.get("item"))
                ET.SubElement(ing_el, "amount").text = safe_text(ing.get("amount"))

                # Current classification (you can change these)
                ET.SubElement(ing_el, "role").text = safe_text(ing.get("role"))  # main/secondary/optional
                ET.SubElement(ing_el, "classification").text = safe_text(
                    ing.get("classification")
                )  # essential/common/optional
                ET.SubElement(ing_el, "categoryTag").text = safe_text(ing.get("category"))
        else:
            raw = r.get("ingredients") or []
            for idx, raw_text in enumerate(raw):
                ing_el = ET.SubElement(ingredients_el, "ingredient")
                ing_el.set("index", str(idx))
                ET.SubElement(ing_el, "original").text = safe_text(raw_text)
                ET.SubElement(ing_el, "item").text = ""
                ET.SubElement(ing_el, "amount").text = ""
                ET.SubElement(ing_el, "role").text = ""
                ET.SubElement(ing_el, "classification").text = ""
                ET.SubElement(ing_el, "categoryTag").text = ""

    return ET.ElementTree(root)


def main() -> None:
    parser = argparse.ArgumentParser(description="Export recipe ingredients to XML for manual sorting.")
    parser.add_argument(
        "--output",
        default=None,
        help="Output XML path (default: developer-kit/ingredient-classification/recipes_ingredients.xml)",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[3]
    backend_dir = repo_root / "backend"
    out_path = Path(args.output) if args.output else (repo_root / "developer-kit" / "ingredient-classification" / "recipes_ingredients.xml")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    recipes = load_recipes(backend_dir)
    tree = build_xml(recipes)
    indent(tree.getroot())
    tree.write(out_path, encoding="utf-8", xml_declaration=True)

    print(f"✅ Wrote XML: {out_path}")
    print(f"   Recipes: {len(recipes)}")


if __name__ == "__main__":
    main()


