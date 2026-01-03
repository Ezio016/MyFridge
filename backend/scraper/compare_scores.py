#!/usr/bin/env python3
"""
Compare old heuristic scores with new real-world popularity scores.
Useful for validating the new system.
"""

import json
from pathlib import Path

def compare_scoring_systems():
    """Compare old vs new popularity scores."""
    
    # Load recipes
    script_dir = Path(__file__).parent
    data_dir = script_dir.parent / 'data'
    recipes_file = data_dir / 'recipes.json'
    
    with open(recipes_file, 'r', encoding='utf-8') as f:
        recipes = json.load(f)
    
    print("=" * 80)
    print("📊 POPULARITY SCORING COMPARISON")
    print("=" * 80)
    print()
    
    # Check if we have both old and new scores
    has_old = any(r.get('popularity_score_old') for r in recipes)
    has_new = any(r.get('popularity_score') for r in recipes)
    
    if not has_old or not has_new:
        print("⚠️  Not enough data to compare.")
        print(f"   Old scores: {'✅' if has_old else '❌'}")
        print(f"   New scores: {'✅' if has_new else '❌'}")
        print()
        print("Run real_popularity_system.py first to generate new scores.")
        return
    
    # Calculate statistics
    old_scores = [r.get('popularity_score_old', 0) for r in recipes]
    new_scores = [r.get('popularity_score', 0) for r in recipes]
    
    old_avg = sum(old_scores) / len(old_scores)
    new_avg = sum(new_scores) / len(new_scores)
    
    print(f"📈 Average Scores:")
    print(f"   Old (heuristic): {old_avg:.1f}")
    print(f"   New (real-world): {new_avg:.1f}")
    print(f"   Change: {new_avg - old_avg:+.1f}")
    print()
    
    # Show recipes with biggest changes
    changes = []
    for r in recipes:
        old = r.get('popularity_score_old', 0)
        new = r.get('popularity_score', 0)
        changes.append({
            'name': r.get('name', 'Unknown'),
            'old': old,
            'new': new,
            'diff': new - old
        })
    
    # Sort by absolute change
    changes.sort(key=lambda x: abs(x['diff']), reverse=True)
    
    print("🔥 Top 10 Biggest Score INCREASES:")
    increases = [c for c in changes if c['diff'] > 0]
    for i, c in enumerate(increases[:10], 1):
        print(f"   {i}. {c['name']}")
        print(f"      {c['old']:.1f} → {c['new']:.1f} ({c['diff']:+.1f})")
    
    print()
    print("❄️  Top 10 Biggest Score DECREASES:")
    decreases = [c for c in changes if c['diff'] < 0]
    for i, c in enumerate(decreases[:10], 1):
        print(f"   {i}. {c['name']}")
        print(f"      {c['old']:.1f} → {c['new']:.1f} ({c['diff']:+.1f})")
    
    print()
    print("=" * 80)
    
    # Validate: Check for suspicious patterns
    print("\n🔍 Validation Checks:")
    
    # Check 1: Are all scores in valid range?
    invalid = [r for r in recipes if not (0 <= r.get('popularity_score', 0) <= 100)]
    if invalid:
        print(f"   ❌ {len(invalid)} recipes have invalid scores (not 0-100)")
    else:
        print(f"   ✅ All scores in valid range (0-100)")
    
    # Check 2: Is there enough variation?
    score_range = max(new_scores) - min(new_scores)
    if score_range < 20:
        print(f"   ⚠️  Low score variation ({score_range:.1f} points)")
    else:
        print(f"   ✅ Good score variation ({score_range:.1f} points)")
    
    # Check 3: Are popular recipes scoring high?
    popular_dishes = [
        "Pad Thai", "Pizza", "Fried Rice", "Pasta", "Tacos",
        "Sushi", "Burger", "Curry", "Ramen", "Stir Fry"
    ]
    
    popular_in_db = []
    for r in recipes:
        name_lower = r.get('name', '').lower()
        for dish in popular_dishes:
            if dish.lower() in name_lower:
                popular_in_db.append((r.get('name'), r.get('popularity_score', 0)))
                break
    
    if popular_in_db:
        avg_popular = sum(s for _, s in popular_in_db) / len(popular_in_db)
        print(f"   📊 Known popular dishes average: {avg_popular:.1f}")
        if avg_popular > new_avg:
            print(f"   ✅ Popular dishes score above average")
        else:
            print(f"   ⚠️  Popular dishes score below average (check algorithm)")


if __name__ == '__main__':
    compare_scoring_systems()

