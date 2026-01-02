"""
Recipe scraper for building MyFridge recipe database.
Scrapes from: Epicurious, BBC Food, Food.com, The Foreign Fork
"""
import json
import requests
from bs4 import BeautifulSoup
import time
from typing import List, Dict
import re

class RecipeScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.recipes = []
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        if not text:
            return ""
        return re.sub(r'\s+', ' ', text.strip())
    
    def scrape_bbc_food(self, recipe_url: str) -> Dict:
        """Scrape a single BBC Food recipe."""
        try:
            response = requests.get(recipe_url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract recipe data
            recipe = {
                'source': 'BBC Food',
                'url': recipe_url,
                'name': '',
                'description': '',
                'prep_time': 0,
                'cook_time': 0,
                'servings': 0,
                'difficulty': 'medium',
                'ingredients': [],
                'instructions': [],
                'tags': [],
                'cuisine': '',
                'category': '',
                'image_url': ''
            }
            
            # Title
            title_tag = soup.find('h1', class_='gel-trafalgar')
            if title_tag:
                recipe['name'] = self.clean_text(title_tag.text)
            
            # Description
            desc_tag = soup.find('p', class_='recipe-description__text')
            if desc_tag:
                recipe['description'] = self.clean_text(desc_tag.text)
            
            # Time info
            time_tags = soup.find_all('p', class_='recipe-metadata__cook-time')
            for time_tag in time_tags:
                text = time_tag.text.lower()
                if 'prep' in text:
                    recipe['prep_time'] = self._extract_minutes(text)
                elif 'cook' in text:
                    recipe['cook_time'] = self._extract_minutes(text)
            
            # Servings
            servings_tag = soup.find('p', class_='recipe-metadata__serving')
            if servings_tag:
                recipe['servings'] = self._extract_number(servings_tag.text)
            
            # Ingredients
            ingredient_tags = soup.find_all('li', class_='recipe-ingredients__list-item')
            for ing_tag in ingredient_tags:
                ingredient = self.clean_text(ing_tag.text)
                if ingredient:
                    recipe['ingredients'].append(ingredient)
            
            # Instructions
            method_tags = soup.find_all('li', class_='recipe-method__list-item')
            for step_tag in method_tags:
                step_text = step_tag.find('p')
                if step_text:
                    step = self.clean_text(step_text.text)
                    if step:
                        recipe['instructions'].append(step)
            
            # Image
            img_tag = soup.find('img', class_='recipe-media__image')
            if img_tag and img_tag.get('src'):
                recipe['image_url'] = img_tag['src']
            
            return recipe
            
        except Exception as e:
            print(f"Error scraping BBC Food {recipe_url}: {e}")
            return None
    
    def scrape_simple_recipes(self) -> List[Dict]:
        """Create some simple starter recipes manually (for initial testing)."""
        return [
            {
                'id': 'simple_scrambled_eggs',
                'source': 'MyFridge',
                'name': 'Perfect Scrambled Eggs',
                'description': 'Creamy, fluffy scrambled eggs in under 5 minutes',
                'prep_time': 2,
                'cook_time': 3,
                'total_time': 5,
                'servings': 2,
                'difficulty': 'easy',
                'ingredients': [
                    '4 large eggs',
                    '2 tablespoons milk',
                    '1 tablespoon butter',
                    'Salt and pepper to taste'
                ],
                'instructions': [
                    'Crack eggs into a bowl and add milk. Whisk until well combined.',
                    'Heat a non-stick pan over medium-low heat and add butter.',
                    'Once butter melts and foams, pour in egg mixture.',
                    'Let sit for 20 seconds, then gently stir with a spatula.',
                    'Continue stirring every 30 seconds until eggs are just set but still creamy.',
                    'Remove from heat, season with salt and pepper, and serve immediately.'
                ],
                'tags': ['breakfast', 'quick', 'vegetarian', 'protein', 'gluten-free'],
                'cuisine': 'American',
                'category': 'breakfast',
                'image_url': 'https://images.unsplash.com/photo-1525351484163-7529414344d8?w=800'
            },
            {
                'id': 'quick_fried_rice',
                'source': 'MyFridge',
                'name': 'Quick Fried Rice',
                'description': 'Use leftover rice for this fast and satisfying meal',
                'prep_time': 5,
                'cook_time': 10,
                'total_time': 15,
                'servings': 3,
                'difficulty': 'easy',
                'ingredients': [
                    '3 cups cooked rice (preferably day-old)',
                    '2 eggs',
                    '1 cup frozen mixed vegetables',
                    '3 tablespoons soy sauce',
                    '2 tablespoons vegetable oil',
                    '2 cloves garlic, minced',
                    '1/2 onion, diced',
                    'Optional: cooked chicken, shrimp, or tofu'
                ],
                'instructions': [
                    'Heat 1 tablespoon oil in a large wok or pan over high heat.',
                    'Scramble the eggs in the pan, then remove and set aside.',
                    'Add remaining oil, then stir-fry onion and garlic for 1 minute.',
                    'Add frozen vegetables and cook for 2-3 minutes.',
                    'Add rice, breaking up any clumps with your spatula.',
                    'Stir-fry for 3-4 minutes until rice is heated through.',
                    'Add soy sauce and scrambled eggs, toss everything together.',
                    'Cook for 1 more minute, then serve hot.'
                ],
                'tags': ['dinner', 'quick', 'asian', 'leftover-friendly', 'customizable'],
                'cuisine': 'Asian',
                'category': 'main',
                'image_url': 'https://images.unsplash.com/photo-1603133872878-684f208fb84b?w=800'
            },
            {
                'id': 'simple_pasta_marinara',
                'source': 'MyFridge',
                'name': 'Simple Pasta Marinara',
                'description': 'Classic Italian comfort food ready in 20 minutes',
                'prep_time': 5,
                'cook_time': 15,
                'total_time': 20,
                'servings': 4,
                'difficulty': 'easy',
                'ingredients': [
                    '1 pound pasta (spaghetti or penne)',
                    '1 can (28 oz) crushed tomatoes',
                    '4 cloves garlic, minced',
                    '1/4 cup olive oil',
                    '1 teaspoon dried basil',
                    '1 teaspoon dried oregano',
                    'Salt and pepper to taste',
                    'Fresh basil for garnish (optional)',
                    'Parmesan cheese for serving (optional)'
                ],
                'instructions': [
                    'Bring a large pot of salted water to boil. Cook pasta according to package directions.',
                    'While pasta cooks, heat olive oil in a large pan over medium heat.',
                    'Add minced garlic and sauté for 1 minute until fragrant (don\'t burn!).',
                    'Pour in crushed tomatoes and add dried basil and oregano.',
                    'Season with salt and pepper, then simmer for 10 minutes.',
                    'Drain pasta, reserving 1 cup of pasta water.',
                    'Add pasta to sauce, tossing to coat. Add pasta water if needed to thin sauce.',
                    'Serve topped with fresh basil and parmesan if desired.'
                ],
                'tags': ['dinner', 'italian', 'vegetarian', 'comfort-food', 'budget-friendly'],
                'cuisine': 'Italian',
                'category': 'main',
                'image_url': 'https://images.unsplash.com/photo-1621996346565-e3dbc646d9a9?w=800'
            },
            {
                'id': 'chicken_stir_fry',
                'source': 'MyFridge',
                'name': 'Easy Chicken Stir-Fry',
                'description': 'Healthy, colorful stir-fry packed with vegetables',
                'prep_time': 10,
                'cook_time': 12,
                'total_time': 22,
                'servings': 4,
                'difficulty': 'easy',
                'ingredients': [
                    '1 pound chicken breast, sliced thin',
                    '2 bell peppers, sliced',
                    '1 broccoli head, cut into florets',
                    '2 carrots, sliced',
                    '3 tablespoons soy sauce',
                    '2 tablespoons oyster sauce',
                    '1 tablespoon cornstarch',
                    '2 tablespoons vegetable oil',
                    '3 cloves garlic, minced',
                    '1 tablespoon fresh ginger, minced',
                    'Cooked rice for serving'
                ],
                'instructions': [
                    'Mix chicken with 1 tablespoon soy sauce and cornstarch. Let marinate 5 minutes.',
                    'Heat 1 tablespoon oil in a wok over high heat.',
                    'Add chicken and stir-fry for 4-5 minutes until cooked through. Remove and set aside.',
                    'Add remaining oil to wok. Add garlic and ginger, stir-fry for 30 seconds.',
                    'Add all vegetables and stir-fry for 3-4 minutes until crisp-tender.',
                    'Return chicken to wok. Add remaining soy sauce and oyster sauce.',
                    'Toss everything together for 1-2 minutes.',
                    'Serve immediately over hot rice.'
                ],
                'tags': ['dinner', 'healthy', 'asian', 'high-protein', 'gluten-free-adaptable'],
                'cuisine': 'Asian',
                'category': 'main',
                'image_url': 'https://images.unsplash.com/photo-1603133872878-684f208fb84b?w=800'
            },
            {
                'id': 'greek_salad',
                'source': 'MyFridge',
                'name': 'Fresh Greek Salad',
                'description': 'Light, refreshing salad with Mediterranean flavors',
                'prep_time': 10,
                'cook_time': 0,
                'total_time': 10,
                'servings': 4,
                'difficulty': 'easy',
                'ingredients': [
                    '4 tomatoes, cut into chunks',
                    '1 cucumber, sliced',
                    '1 red onion, thinly sliced',
                    '1 green bell pepper, chopped',
                    '1 cup Kalamata olives',
                    '200g feta cheese, cubed',
                    '1/4 cup extra virgin olive oil',
                    '2 tablespoons red wine vinegar',
                    '1 teaspoon dried oregano',
                    'Salt and pepper to taste'
                ],
                'instructions': [
                    'Cut all vegetables into bite-sized pieces and place in a large bowl.',
                    'Add olives and feta cheese.',
                    'In a small bowl, whisk together olive oil, vinegar, oregano, salt, and pepper.',
                    'Pour dressing over salad and toss gently to combine.',
                    'Let sit for 5 minutes for flavors to meld.',
                    'Serve immediately or refrigerate for up to 2 hours.'
                ],
                'tags': ['salad', 'vegetarian', 'mediterranean', 'no-cook', 'gluten-free', 'healthy'],
                'cuisine': 'Mediterranean',
                'category': 'salad',
                'image_url': 'https://images.unsplash.com/photo-1540189549336-e6e99c3679fe?w=800'
            },
            {
                'id': 'banana_pancakes',
                'source': 'MyFridge',
                'name': '3-Ingredient Banana Pancakes',
                'description': 'Healthy pancakes with just banana, eggs, and oats',
                'prep_time': 5,
                'cook_time': 10,
                'total_time': 15,
                'servings': 2,
                'difficulty': 'easy',
                'ingredients': [
                    '2 ripe bananas',
                    '2 large eggs',
                    '1/4 cup oats (optional, for texture)',
                    'Butter or oil for cooking',
                    'Optional toppings: honey, berries, nuts'
                ],
                'instructions': [
                    'Mash bananas in a bowl until smooth.',
                    'Add eggs and oats, mix until well combined (batter will be thin).',
                    'Heat a non-stick pan over medium heat and add a small amount of butter.',
                    'Pour 1/4 cup batter for each pancake.',
                    'Cook for 2-3 minutes until bubbles form and edges look set.',
                    'Flip carefully and cook for another 1-2 minutes.',
                    'Serve warm with your favorite toppings.'
                ],
                'tags': ['breakfast', 'healthy', 'gluten-free', 'quick', 'kid-friendly'],
                'cuisine': 'American',
                'category': 'breakfast',
                'image_url': 'https://images.unsplash.com/photo-1567620905732-2d1ec7ab7445?w=800'
            },
            {
                'id': 'veggie_quesadilla',
                'source': 'MyFridge',
                'name': 'Veggie Quesadilla',
                'description': 'Crispy, cheesy quesadilla loaded with vegetables',
                'prep_time': 8,
                'cook_time': 8,
                'total_time': 16,
                'servings': 2,
                'difficulty': 'easy',
                'ingredients': [
                    '4 flour tortillas',
                    '2 cups shredded cheese (cheddar or Mexican blend)',
                    '1 bell pepper, diced',
                    '1/2 onion, diced',
                    '1 cup corn (frozen or canned)',
                    '1 can black beans, drained',
                    '1 tablespoon olive oil',
                    'Optional: sour cream, salsa, guacamole for serving'
                ],
                'instructions': [
                    'Heat olive oil in a pan over medium heat.',
                    'Sauté bell pepper and onion for 3-4 minutes until soft.',
                    'Add corn and black beans, cook for 2 more minutes. Remove from heat.',
                    'Heat a clean pan or griddle over medium heat.',
                    'Place one tortilla on the pan, sprinkle with cheese.',
                    'Add a layer of vegetable mixture, then more cheese.',
                    'Top with another tortilla and cook for 2-3 minutes per side until golden and crispy.',
                    'Cut into wedges and serve with sour cream, salsa, or guacamole.'
                ],
                'tags': ['lunch', 'dinner', 'vegetarian', 'mexican', 'quick', 'kid-friendly'],
                'cuisine': 'Mexican',
                'category': 'main',
                'image_url': 'https://images.unsplash.com/photo-1618040996337-56904b7850b9?w=800'
            },
            {
                'id': 'caprese_salad',
                'source': 'MyFridge',
                'name': 'Classic Caprese Salad',
                'description': 'Simple Italian salad with tomatoes, mozzarella, and basil',
                'prep_time': 10,
                'cook_time': 0,
                'total_time': 10,
                'servings': 4,
                'difficulty': 'easy',
                'ingredients': [
                    '4 large tomatoes, sliced',
                    '16 oz fresh mozzarella, sliced',
                    '1 cup fresh basil leaves',
                    '1/4 cup extra virgin olive oil',
                    '2 tablespoons balsamic vinegar',
                    'Salt and pepper to taste'
                ],
                'instructions': [
                    'Slice tomatoes and mozzarella into 1/4-inch thick rounds.',
                    'Arrange tomato and mozzarella slices on a platter, alternating and overlapping.',
                    'Tuck fresh basil leaves between the slices.',
                    'Drizzle olive oil and balsamic vinegar over the salad.',
                    'Season with salt and freshly ground black pepper.',
                    'Serve immediately at room temperature for best flavor.'
                ],
                'tags': ['salad', 'vegetarian', 'italian', 'no-cook', 'gluten-free', 'appetizer'],
                'cuisine': 'Italian',
                'category': 'salad',
                'image_url': 'https://images.unsplash.com/photo-1592417817038-d13fd7342605?w=800'
            }
        ]
    
    def _extract_minutes(self, text: str) -> int:
        """Extract minutes from time string like '30 mins' or '1 hr 20 mins'."""
        minutes = 0
        hours = re.search(r'(\d+)\s*h', text)
        mins = re.search(r'(\d+)\s*m', text)
        
        if hours:
            minutes += int(hours.group(1)) * 60
        if mins:
            minutes += int(mins.group(1))
        
        return minutes
    
    def _extract_number(self, text: str) -> int:
        """Extract first number from text."""
        match = re.search(r'\d+', text)
        return int(match.group()) if match else 0
    
    def save_to_json(self, filename: str):
        """Save recipes to JSON file."""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.recipes, f, indent=2, ensure_ascii=False)
        print(f"✅ Saved {len(self.recipes)} recipes to {filename}")


def scrape_bbc_food_recipes():
    """Scrape multiple BBC Food recipes."""
    bbc_urls = [
        # Quick & Easy
        'https://www.bbc.co.uk/food/recipes/quick_chicken_stir-fry_91200',
        'https://www.bbc.co.uk/food/recipes/spaghetti_carbonara_89347',
        'https://www.bbc.co.uk/food/recipes/perfect_pancakes_71620',
        'https://www.bbc.co.uk/food/recipes/easy_spanish_omelette_86005',
        'https://www.bbc.co.uk/food/recipes/easy_chicken_curry_89334',
        
        # Healthy
        'https://www.bbc.co.uk/food/recipes/quinoa_salad_with_feta_30556',
        'https://www.bbc.co.uk/food/recipes/salmon_teriyaki_12289',
        'https://www.bbc.co.uk/food/recipes/greek_salad_76803',
        
        # Comfort Food
        'https://www.bbc.co.uk/food/recipes/spag_bol_74322',
        'https://www.bbc.co.uk/food/recipes/simple_fish_pie_12346',
        'https://www.bbc.co.uk/food/recipes/macaroni_cheese_76699',
        'https://www.bbc.co.uk/food/recipes/cottage_pie_11605',
        
        # Vegetarian
        'https://www.bbc.co.uk/food/recipes/veggie_chilli_83038',
        'https://www.bbc.co.uk/food/recipes/cheese_and_tomato_pizza_24251',
        'https://www.bbc.co.uk/food/recipes/mushroom_risotto_77569',
    ]
    
    scraper = RecipeScraper()
    recipes = []
    
    print("\n🌐 Scraping BBC Food recipes...")
    for i, url in enumerate(bbc_urls, 1):
        print(f"  [{i}/{len(bbc_urls)}] {url}")
        try:
            recipe = scraper.scrape_bbc_food(url)
            if recipe and recipe.get('name'):
                recipes.append(recipe)
                print(f"    ✅ {recipe['name']}")
                time.sleep(2)  # Be polite to the server
            else:
                print(f"    ⚠️ Skipped (incomplete data)")
        except Exception as e:
            print(f"    ❌ Error: {e}")
            continue
    
    return recipes


def main():
    """Main scraper function."""
    scraper = RecipeScraper()
    
    print("🍳 MyFridge Recipe Scraper")
    print("=" * 50)
    
    # Start with simple recipes
    print("\n📝 Loading starter recipes...")
    scraper.recipes = scraper.scrape_simple_recipes()
    print(f"✅ Added {len(scraper.recipes)} starter recipes")
    
    # Scrape BBC Food
    try:
        bbc_recipes = scrape_bbc_food_recipes()
        scraper.recipes.extend(bbc_recipes)
        print(f"\n✅ Added {len(bbc_recipes)} recipes from BBC Food")
    except Exception as e:
        print(f"\n⚠️ BBC Food scraping failed: {e}")
        print("   Continuing with starter recipes only...")
    
    # Add unique IDs if missing
    for i, recipe in enumerate(scraper.recipes):
        if 'id' not in recipe or not recipe['id']:
            # Create ID from name
            recipe['id'] = recipe['name'].lower().replace(' ', '_').replace('-', '_')
            # Ensure uniqueness
            base_id = recipe['id']
            counter = 1
            while any(r.get('id') == recipe['id'] for r in scraper.recipes[:i]):
                recipe['id'] = f"{base_id}_{counter}"
                counter += 1
    
    # Save to JSON
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(script_dir, '..', 'data', 'recipes.json')
    scraper.save_to_json(output_file)
    
    print("\n✨ Recipe database created successfully!")
    print(f"📊 Total recipes: {len(scraper.recipes)}")
    
    # Print summary
    categories = {}
    sources = {}
    for recipe in scraper.recipes:
        cat = recipe.get('category', 'unknown')
        categories[cat] = categories.get(cat, 0) + 1
        src = recipe.get('source', 'unknown')
        sources[src] = sources.get(src, 0) + 1
    
    print("\n📂 Recipes by category:")
    for cat, count in sorted(categories.items()):
        print(f"  - {cat}: {count}")
    
    print("\n🌐 Recipes by source:")
    for src, count in sorted(sources.items()):
        print(f"  - {src}: {count}")


if __name__ == '__main__':
    main()

