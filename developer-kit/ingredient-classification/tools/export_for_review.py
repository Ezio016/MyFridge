#!/usr/bin/env python3
"""
Export recipes to CSV for manual review by development team

Usage:
    python export_for_review.py
    python export_for_review.py --output reviews/batch1.csv
    python export_for_review.py --category dessert
    python export_for_review.py --sample 50
"""

import json
import csv
import sys
from pathlib import Path
from datetime import datetime

# Add backend to path
backend_path = Path(__file__).parent.parent.parent.parent / 'backend'
sys.path.insert(0, str(backend_path))


def load_recipes():
    """Load recipes from database"""
    recipes_file = backend_path / 'data' / 'recipes.json'
    with open(recipes_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def export_to_csv(recipes, output_file, include_scores=False):
    """Export recipes to CSV format"""
    
    rows = []
    
    for recipe in recipes:
        structured = recipe.get('ingredients_structured', [])
        
        if not structured:
            continue
        
        for ing in structured:
            row = {
                'recipe_id': recipe.get('id', ''),
                'recipe_name': recipe.get('name', ''),
                'category': recipe.get('category', ''),
                'cuisine': recipe.get('cuisine', ''),
                'ingredient_original': ing.get('original', ''),
                'ingredient_item': ing.get('item', ''),
                'ingredient_amount': ing.get('amount', ''),
                'role': ing.get('role', ''),
                'classification': ing.get('classification', ''),
                'category_tag': ing.get('category', ''),
                'position': ing.get('_position', ''),
            }
            
            if include_scores:
                row['score'] = ing.get('_score', '')
            
            # Add review columns
            row['review_role'] = ''  # For manual input
            row['notes'] = ''  # For manual input
            
            rows.append(row)
    
    # Write CSV
    if rows:
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            fieldnames = list(rows[0].keys())
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        
        return len(rows)
    
    return 0


def export_summary(recipes, output_file):
    """Export recipe-level summary"""
    
    rows = []
    
    for recipe in recipes:
        structured = recipe.get('ingredients_structured', [])
        
        if not structured:
            continue
        
        # Count by role
        main_count = sum(1 for ing in structured if ing.get('role') == 'main')
        secondary_count = sum(1 for ing in structured if ing.get('role') == 'secondary')
        optional_count = sum(1 for ing in structured if ing.get('role') == 'optional')
        
        row = {
            'recipe_id': recipe.get('id', ''),
            'recipe_name': recipe.get('name', ''),
            'category': recipe.get('category', ''),
            'cuisine': recipe.get('cuisine', ''),
            'total_ingredients': len(structured),
            'main_count': main_count,
            'secondary_count': secondary_count,
            'optional_count': optional_count,
            'main_ratio': f"{main_count/len(structured):.2%}" if structured else '0%',
            'review_ok': '',  # For manual input
            'issues': '',  # For manual input
        }
        
        rows.append(row)
    
    # Write CSV
    if rows:
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            fieldnames = list(rows[0].keys())
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        
        return len(rows)
    
    return 0


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Export recipes for manual review')
    parser.add_argument('--output', default=None, help='Output CSV file')
    parser.add_argument('--summary', action='store_true', help='Export summary (recipe-level) instead of detail')
    parser.add_argument('--category', help='Filter by category (e.g., dessert, main)')
    parser.add_argument('--cuisine', help='Filter by cuisine (e.g., Italian, Mexican)')
    parser.add_argument('--sample', type=int, help='Random sample of N recipes')
    parser.add_argument('--include-scores', action='store_true', help='Include classification scores')
    args = parser.parse_args()
    
    # Generate default output filename
    if not args.output:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_type = 'summary' if args.summary else 'detail'
        args.output = f'recipe_review_{output_type}_{timestamp}.csv'
    
    # Load recipes
    print("📖 Loading recipes...")
    recipes = load_recipes()
    print(f"✅ Loaded {len(recipes)} recipes\n")
    
    # Filter
    filtered = recipes
    
    if args.category:
        filtered = [r for r in filtered if r.get('category', '').lower() == args.category.lower()]
        print(f"🔍 Filtered to {len(filtered)} recipes in category '{args.category}'")
    
    if args.cuisine:
        filtered = [r for r in filtered if r.get('cuisine', '').lower() == args.cuisine.lower()]
        print(f"🔍 Filtered to {len(filtered)} recipes in cuisine '{args.cuisine}'")
    
    if args.sample:
        import random
        filtered = random.sample(filtered, min(args.sample, len(filtered)))
        print(f"🎲 Sampled {len(filtered)} recipes")
    
    if not filtered:
        print("❌ No recipes match filters!")
        sys.exit(1)
    
    # Export
    print(f"\n💾 Exporting to {args.output}...")
    
    if args.summary:
        count = export_summary(filtered, args.output)
        print(f"✅ Exported {count} recipe summaries")
    else:
        count = export_to_csv(filtered, args.output, include_scores=args.include_scores)
        print(f"✅ Exported {count} ingredient entries")
    
    print(f"\n📊 Review file created: {args.output}")
    print(f"\n💡 Instructions:")
    print(f"  1. Open {args.output} in Excel/Google Sheets")
    print(f"  2. Review classifications in 'role' column")
    print(f"  3. Add corrections in 'review_role' column (main/secondary/optional)")
    print(f"  4. Add notes in 'notes' column")
    print(f"  5. Save and share with team\n")


if __name__ == '__main__':
    main()

