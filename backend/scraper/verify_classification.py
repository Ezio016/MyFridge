"""
Quick verification script to check ingredient classification results
"""

import json
from pathlib import Path

def verify_classification():
    """Verify that recipes have been properly classified."""
    script_dir = Path(__file__).parent
    data_dir = script_dir.parent / 'data'
    recipes_file = data_dir / 'recipes.json'
    
    print("🔍 Verifying ingredient classification...")
    print("=" * 60)
    
    with open(recipes_file, 'r', encoding='utf-8') as f:
        recipes = json.load(f)
    
    print(f"✅ Loaded {len(recipes)} recipes\n")
    
    # Check if recipes have structured ingredients
    recipes_with_structured = [r for r in recipes if 'ingredients_structured' in r]
    print(f"📊 Recipes with structured ingredients: {len(recipes_with_structured)}/{len(recipes)}")
    
    if len(recipes_with_structured) == 0:
        print("❌ No recipes have structured ingredients!")
        return
    
    # Sample classification stats
    all_classifications = []
    all_roles = []
    for r in recipes_with_structured:
        for ing in r.get('ingredients_structured', []):
            all_classifications.append(ing['classification'])
            all_roles.append(ing.get('role', 'secondary'))
    
    essential_count = all_classifications.count('essential')
    common_count = all_classifications.count('common')
    optional_count = all_classifications.count('optional')
    
    print(f"\n📈 Classification breakdown:")
    print(f"  Essential: {essential_count} ({essential_count/len(all_classifications)*100:.1f}%)")
    print(f"  Common: {common_count} ({common_count/len(all_classifications)*100:.1f}%)")
    print(f"  Optional: {optional_count} ({optional_count/len(all_classifications)*100:.1f}%)")

    main_count = all_roles.count('main')
    secondary_count = all_roles.count('secondary')
    optional_role_count = all_roles.count('optional')
    print(f"\n📈 Role breakdown (main vs optional):")
    print(f"  Main: {main_count} ({main_count/len(all_roles)*100:.1f}%)")
    print(f"  Secondary: {secondary_count} ({secondary_count/len(all_roles)*100:.1f}%)")
    print(f"  Optional: {optional_role_count} ({optional_role_count/len(all_roles)*100:.1f}%)")
    
    # Show a few examples
    print(f"\n📝 Sample recipes with classification:\n")
    
    for recipe in recipes_with_structured[:3]:
        print(f"  Recipe: {recipe['name']}")
        print(f"  Category: {recipe.get('category', 'N/A')}, Cuisine: {recipe.get('cuisine', 'N/A')}")
        
        # Group by classification
        essential = [ing for ing in recipe['ingredients_structured'] if ing['classification'] == 'essential']
        common = [ing for ing in recipe['ingredients_structured'] if ing['classification'] == 'common']
        optional = [ing for ing in recipe['ingredients_structured'] if ing['classification'] == 'optional']
        
        if essential:
            print(f"  Essential ({len(essential)}):")
            for ing in essential[:3]:
                print(f"    - {ing['item']} ({ing['category']})")
        
        if common:
            print(f"  Common ({len(common)}):")
            for ing in common[:3]:
                print(f"    - {ing['item']} ({ing['category']})")
        
        if optional:
            print(f"  Optional ({len(optional)}):")
            for ing in optional[:3]:
                print(f"    - {ing['item']} ({ing['category']})")
        
        print()
    
    # Check specific examples
    print(f"\n🎯 Checking specific recipes:")
    
    french_toast = next((r for r in recipes if 'french toast' in r['name'].lower()), None)
    if french_toast:
        print(f"\n  French Toast:")
        for ing in french_toast.get('ingredients_structured', []):
            print(f"    {ing.get('role','?'):9s} | {ing['classification']:10s} | {ing['category']:10s} | {ing['item']}")
    
    pasta = next((r for r in recipes if 'pasta' in r['name'].lower() and 'marinara' in r['name'].lower()), None)
    if pasta:
        print(f"\n  Simple Pasta Marinara:")
        for ing in pasta.get('ingredients_structured', []):
            print(f"    {ing.get('role','?'):9s} | {ing['classification']:10s} | {ing['category']:10s} | {ing['item']}")
    
    print(f"\n✅ Classification verification complete!")


if __name__ == "__main__":
    verify_classification()

