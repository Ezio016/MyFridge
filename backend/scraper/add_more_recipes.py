"""
Add more curated recipes to MyFridge database.
These are manually curated from various sources.
"""
import json
import os

def get_additional_recipes():
    """Return a list of additional curated recipes."""
    return [
        # Italian Recipes
        {
            'id': 'spaghetti_carbonara',
            'source': 'Curated',
            'name': 'Classic Spaghetti Carbonara',
            'description': 'Creamy Italian pasta with bacon, eggs, and parmesan',
            'prep_time': 5,
            'cook_time': 15,
            'total_time': 20,
            'servings': 4,
            'difficulty': 'medium',
            'ingredients': [
                '400g spaghetti',
                '200g bacon or pancetta, diced',
                '4 large eggs',
                '100g parmesan cheese, grated',
                '2 cloves garlic, minced',
                'Black pepper to taste',
                'Salt for pasta water'
            ],
            'instructions': [
                'Bring a large pot of salted water to boil. Cook spaghetti according to package directions.',
                'While pasta cooks, fry bacon in a large pan over medium heat until crispy (5-7 minutes).',
                'In a bowl, whisk together eggs, parmesan, and lots of black pepper.',
                'When pasta is done, reserve 1 cup pasta water, then drain.',
                'Add hot pasta to the pan with bacon (off heat). Toss to coat.',
                'Quickly pour in egg mixture while tossing constantly. The heat will cook the eggs into a creamy sauce.',
                'Add pasta water a little at a time if sauce is too thick.',
                'Serve immediately with extra parmesan and black pepper.'
            ],
            'tags': ['italian', 'pasta', 'quick', 'comfort-food', 'dinner'],
            'cuisine': 'Italian',
            'category': 'main',
            'image_url': 'https://images.unsplash.com/photo-1612874742237-6526221588e3?w=800'
        },
        {
            'id': 'margherita_pizza',
            'source': 'Curated',
            'name': 'Margherita Pizza',
            'description': 'Simple Italian pizza with tomato, mozzarella, and basil',
            'prep_time': 15,
            'cook_time': 12,
            'total_time': 27,
            'servings': 2,
            'difficulty': 'medium',
            'ingredients': [
                '1 pizza dough (store-bought or homemade)',
                '1/2 cup tomato sauce',
                '200g fresh mozzarella, sliced',
                'Fresh basil leaves',
                '2 tablespoons olive oil',
                'Salt and pepper to taste',
                'Flour for dusting'
            ],
            'instructions': [
                'Preheat oven to 475°F (245°C). If you have a pizza stone, put it in to heat.',
                'Roll out pizza dough on a floured surface to about 12 inches diameter.',
                'Transfer to a pizza pan or parchment paper.',
                'Spread tomato sauce evenly, leaving a 1-inch border for crust.',
                'Arrange mozzarella slices on top. Drizzle with olive oil.',
                'Season with salt and pepper.',
                'Bake for 10-12 minutes until crust is golden and cheese is bubbly.',
                'Remove from oven, top with fresh basil leaves.',
                'Let cool for 2 minutes, slice, and serve.'
            ],
            'tags': ['italian', 'pizza', 'vegetarian', 'dinner', 'kid-friendly'],
            'cuisine': 'Italian',
            'category': 'main',
            'image_url': 'https://images.unsplash.com/photo-1574071318508-1cdbab80d002?w=800'
        },
        
        # Asian Recipes
        {
            'id': 'pad_thai',
            'source': 'Curated',
            'name': 'Easy Pad Thai',
            'description': 'Thai stir-fried noodles with shrimp, peanuts, and lime',
            'prep_time': 15,
            'cook_time': 10,
            'total_time': 25,
            'servings': 3,
            'difficulty': 'medium',
            'ingredients': [
                '8 oz rice noodles',
                '200g shrimp, peeled',
                '2 eggs',
                '3 tablespoons fish sauce',
                '2 tablespoons tamarind paste or lime juice',
                '2 tablespoons brown sugar',
                '3 cloves garlic, minced',
                '1 cup bean sprouts',
                '1/4 cup peanuts, crushed',
                '2 green onions, chopped',
                'Lime wedges for serving',
                '3 tablespoons vegetable oil'
            ],
            'instructions': [
                'Soak rice noodles in warm water for 20 minutes until soft. Drain.',
                'Mix fish sauce, tamarind paste, and brown sugar in a small bowl.',
                'Heat 2 tablespoons oil in a wok over high heat.',
                'Add shrimp and cook for 2-3 minutes until pink. Remove and set aside.',
                'Add remaining oil and garlic, stir-fry for 30 seconds.',
                'Push to side, crack eggs into wok and scramble.',
                'Add drained noodles and sauce mixture. Toss for 2-3 minutes.',
                'Add shrimp back in, plus bean sprouts and green onions. Toss for 1 minute.',
                'Serve topped with crushed peanuts and lime wedges.'
            ],
            'tags': ['thai', 'asian', 'seafood', 'noodles', 'dinner'],
            'cuisine': 'Thai',
            'category': 'main',
            'image_url': 'https://images.unsplash.com/photo-1559314809-0d155014e29e?w=800'
        },
        {
            'id': 'teriyaki_chicken',
            'source': 'Curated',
            'name': 'Teriyaki Chicken Bowl',
            'description': 'Sweet and savory Japanese chicken over rice with vegetables',
            'prep_time': 10,
            'cook_time': 15,
            'total_time': 25,
            'servings': 4,
            'difficulty': 'easy',
            'ingredients': [
                '500g chicken thighs, cut into bite-sized pieces',
                '1/4 cup soy sauce',
                '2 tablespoons honey',
                '2 tablespoons rice vinegar',
                '1 tablespoon sesame oil',
                '2 cloves garlic, minced',
                '1 teaspoon ginger, minced',
                '1 tablespoon cornstarch',
                '2 cups cooked rice',
                '1 cup broccoli florets',
                'Sesame seeds for garnish',
                '2 tablespoons vegetable oil'
            ],
            'instructions': [
                'Mix soy sauce, honey, vinegar, sesame oil, garlic, and ginger in a bowl.',
                'Heat vegetable oil in a large pan over medium-high heat.',
                'Add chicken and cook for 5-7 minutes until golden and cooked through.',
                'While chicken cooks, steam broccoli for 3-4 minutes until tender-crisp.',
                'Pour teriyaki sauce over chicken. Let simmer for 2 minutes.',
                'Mix cornstarch with 2 tablespoons water, add to pan to thicken sauce.',
                'Serve chicken and sauce over rice with steamed broccoli.',
                'Garnish with sesame seeds.'
            ],
            'tags': ['japanese', 'asian', 'chicken', 'rice-bowl', 'dinner', 'healthy'],
            'cuisine': 'Japanese',
            'category': 'main',
            'image_url': 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=800'
        },
        
        # Mexican Recipes
        {
            'id': 'chicken_tacos',
            'source': 'Curated',
            'name': 'Quick Chicken Tacos',
            'description': 'Flavorful chicken tacos with fresh toppings',
            'prep_time': 10,
            'cook_time': 12,
            'total_time': 22,
            'servings': 4,
            'difficulty': 'easy',
            'ingredients': [
                '500g chicken breast, diced',
                '1 tablespoon chili powder',
                '1 teaspoon cumin',
                '1 teaspoon paprika',
                '1/2 teaspoon garlic powder',
                'Salt and pepper to taste',
                '8 small tortillas',
                '1 cup shredded lettuce',
                '1 tomato, diced',
                '1/2 cup shredded cheese',
                '1/2 cup sour cream',
                'Lime wedges',
                '2 tablespoons vegetable oil'
            ],
            'instructions': [
                'Mix chili powder, cumin, paprika, garlic powder, salt, and pepper in a bowl.',
                'Toss chicken pieces with spice mixture until well coated.',
                'Heat oil in a large skillet over medium-high heat.',
                'Add chicken and cook for 8-10 minutes, stirring occasionally, until cooked through.',
                'Warm tortillas in a dry pan or microwave for 20 seconds.',
                'Fill each tortilla with chicken.',
                'Top with lettuce, tomato, cheese, and sour cream.',
                'Serve with lime wedges on the side.'
            ],
            'tags': ['mexican', 'tacos', 'chicken', 'quick', 'dinner', 'kid-friendly'],
            'cuisine': 'Mexican',
            'category': 'main',
            'image_url': 'https://images.unsplash.com/photo-1565299585323-38d6b0865b47?w=800'
        },
        {
            'id': 'guacamole',
            'source': 'Curated',
            'name': 'Fresh Guacamole',
            'description': 'Creamy avocado dip with lime and cilantro',
            'prep_time': 10,
            'cook_time': 0,
            'total_time': 10,
            'servings': 4,
            'difficulty': 'easy',
            'ingredients': [
                '3 ripe avocados',
                '1 lime, juiced',
                '1/2 small onion, finely diced',
                '1 tomato, diced',
                '2 tablespoons fresh cilantro, chopped',
                '1 clove garlic, minced',
                '1/2 teaspoon salt',
                '1/4 teaspoon cumin',
                'Tortilla chips for serving'
            ],
            'instructions': [
                'Cut avocados in half, remove pit, and scoop flesh into a bowl.',
                'Mash avocados with a fork to desired consistency (chunky or smooth).',
                'Add lime juice immediately to prevent browning.',
                'Stir in onion, tomato, cilantro, garlic, salt, and cumin.',
                'Mix well and taste. Adjust seasoning if needed.',
                'Serve immediately with tortilla chips.',
                'To store: press plastic wrap directly on surface to prevent browning.'
            ],
            'tags': ['mexican', 'dip', 'appetizer', 'no-cook', 'vegan', 'healthy'],
            'cuisine': 'Mexican',
            'category': 'appetizer',
            'image_url': 'https://images.unsplash.com/photo-1604909052743-94e838986d24?w=800'
        },
        
        # Breakfast Recipes
        {
            'id': 'french_toast',
            'source': 'Curated',
            'name': 'Classic French Toast',
            'description': 'Golden, crispy French toast perfect for weekend brunch',
            'prep_time': 5,
            'cook_time': 10,
            'total_time': 15,
            'servings': 4,
            'difficulty': 'easy',
            'ingredients': [
                '8 slices bread (brioche or thick white bread)',
                '4 large eggs',
                '1/2 cup milk',
                '1 teaspoon vanilla extract',
                '1 teaspoon cinnamon',
                '2 tablespoons butter',
                'Maple syrup for serving',
                'Powdered sugar for dusting (optional)',
                'Fresh berries (optional)'
            ],
            'instructions': [
                'In a shallow bowl, whisk together eggs, milk, vanilla, and cinnamon.',
                'Heat a large skillet or griddle over medium heat. Add 1 tablespoon butter.',
                'Dip each bread slice into egg mixture, coating both sides but not soaking too long.',
                'Place coated bread on hot skillet. Cook for 2-3 minutes per side until golden brown.',
                'Add more butter as needed for remaining slices.',
                'Serve hot with maple syrup, powdered sugar, and fresh berries if desired.'
            ],
            'tags': ['breakfast', 'brunch', 'quick', 'kid-friendly', 'vegetarian'],
            'cuisine': 'American',
            'category': 'breakfast',
            'image_url': 'https://images.unsplash.com/photo-1484723091739-30a097e8f929?w=800'
        },
        {
            'id': 'avocado_toast',
            'source': 'Curated',
            'name': 'Avocado Toast',
            'description': 'Trendy and nutritious breakfast with mashed avocado on toast',
            'prep_time': 5,
            'cook_time': 3,
            'total_time': 8,
            'servings': 2,
            'difficulty': 'easy',
            'ingredients': [
                '4 slices whole grain bread',
                '2 ripe avocados',
                '1 lemon, juiced',
                'Salt and pepper to taste',
                'Red pepper flakes (optional)',
                'Cherry tomatoes, halved (optional)',
                '2 eggs (optional, for topping)',
                'Everything bagel seasoning (optional)'
            ],
            'instructions': [
                'Toast bread slices until golden and crispy.',
                'While bread toasts, mash avocados in a bowl with lemon juice, salt, and pepper.',
                'Spread mashed avocado generously on each toast.',
                'Top with cherry tomatoes, red pepper flakes, or everything bagel seasoning.',
                'Optional: top with a fried or poached egg for extra protein.',
                'Serve immediately while toast is still warm.'
            ],
            'tags': ['breakfast', 'healthy', 'quick', 'vegetarian', 'trendy', 'no-cook'],
            'cuisine': 'Modern',
            'category': 'breakfast',
            'image_url': 'https://images.unsplash.com/photo-1541519227354-08fa5d50c44d?w=800'
        },
        
        # Soups
        {
            'id': 'tomato_soup',
            'source': 'Curated',
            'name': 'Creamy Tomato Soup',
            'description': 'Comforting homemade tomato soup, perfect with grilled cheese',
            'prep_time': 5,
            'cook_time': 20,
            'total_time': 25,
            'servings': 4,
            'difficulty': 'easy',
            'ingredients': [
                '2 cans (28 oz each) crushed tomatoes',
                '1 onion, diced',
                '3 cloves garlic, minced',
                '2 cups vegetable broth',
                '1/2 cup heavy cream',
                '2 tablespoons butter',
                '1 teaspoon sugar',
                '1 teaspoon dried basil',
                'Salt and pepper to taste',
                'Fresh basil for garnish'
            ],
            'instructions': [
                'Melt butter in a large pot over medium heat.',
                'Add onion and cook for 5 minutes until soft. Add garlic and cook 1 more minute.',
                'Pour in crushed tomatoes and vegetable broth.',
                'Add sugar, dried basil, salt, and pepper. Stir well.',
                'Bring to a boil, then reduce heat and simmer for 15 minutes.',
                'Use an immersion blender to puree soup until smooth (or transfer to blender in batches).',
                'Stir in heavy cream and heat through (don\'t boil).',
                'Serve hot, garnished with fresh basil.'
            ],
            'tags': ['soup', 'comfort-food', 'vegetarian', 'lunch', 'dinner'],
            'cuisine': 'American',
            'category': 'soup',
            'image_url': 'https://images.unsplash.com/photo-1547592166-23ac45744acd?w=800'
        },
        {
            'id': 'chicken_noodle_soup',
            'source': 'Curated',
            'name': 'Classic Chicken Noodle Soup',
            'description': 'Healing soup with tender chicken, vegetables, and noodles',
            'prep_time': 10,
            'cook_time': 30,
            'total_time': 40,
            'servings': 6,
            'difficulty': 'easy',
            'ingredients': [
                '2 chicken breasts',
                '8 cups chicken broth',
                '2 carrots, sliced',
                '2 celery stalks, sliced',
                '1 onion, diced',
                '3 cloves garlic, minced',
                '200g egg noodles',
                '1 bay leaf',
                '1 teaspoon thyme',
                'Salt and pepper to taste',
                'Fresh parsley, chopped',
                '2 tablespoons olive oil'
            ],
            'instructions': [
                'Heat olive oil in a large pot over medium heat.',
                'Add onion, carrots, and celery. Cook for 5 minutes until softened.',
                'Add garlic and cook for 1 more minute.',
                'Pour in chicken broth. Add chicken breasts, bay leaf, and thyme.',
                'Bring to a boil, then reduce heat and simmer for 20 minutes.',
                'Remove chicken, shred with two forks, and return to pot.',
                'Add noodles and cook for 8-10 minutes until tender.',
                'Season with salt and pepper. Remove bay leaf.',
                'Serve hot, garnished with fresh parsley.'
            ],
            'tags': ['soup', 'comfort-food', 'chicken', 'healthy', 'dinner'],
            'cuisine': 'American',
            'category': 'soup',
            'image_url': 'https://images.unsplash.com/photo-1547592166-23ac45744acd?w=800'
        },
        
        # Desserts
        {
            'id': 'chocolate_mug_cake',
            'source': 'Curated',
            'name': 'Microwave Chocolate Mug Cake',
            'description': 'Single-serving chocolate cake ready in 2 minutes',
            'prep_time': 3,
            'cook_time': 2,
            'total_time': 5,
            'servings': 1,
            'difficulty': 'easy',
            'ingredients': [
                '4 tablespoons all-purpose flour',
                '4 tablespoons sugar',
                '2 tablespoons cocoa powder',
                '1 egg',
                '3 tablespoons milk',
                '3 tablespoons vegetable oil',
                '1/4 teaspoon vanilla extract',
                'Pinch of salt',
                'Optional: chocolate chips, ice cream for serving'
            ],
            'instructions': [
                'In a large microwave-safe mug, mix flour, sugar, cocoa powder, and salt.',
                'Add egg and mix well with a fork until smooth.',
                'Stir in milk, oil, and vanilla extract until fully combined.',
                'Optional: add a few chocolate chips on top.',
                'Microwave on high for 1 minute 30 seconds to 2 minutes (time varies by microwave).',
                'Cake should rise and be set in the center. If still wet, microwave for 15 more seconds.',
                'Let cool for 1 minute before eating.',
                'Serve with ice cream or whipped cream if desired.'
            ],
            'tags': ['dessert', 'quick', 'chocolate', 'microwave', 'single-serving'],
            'cuisine': 'American',
            'category': 'dessert',
            'image_url': 'https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=800'
        }
    ]


def main():
    """Add recipes to the database."""
    # Load existing recipes
    data_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        '..',
        'data',
        'recipes.json'
    )
    
    with open(data_path, 'r', encoding='utf-8') as f:
        existing_recipes = json.load(f)
    
    print(f"📊 Current recipes: {len(existing_recipes)}")
    
    # Get new recipes
    new_recipes = get_additional_recipes()
    
    # Check for duplicates
    existing_ids = {r['id'] for r in existing_recipes}
    unique_new = [r for r in new_recipes if r['id'] not in existing_ids]
    
    print(f"✨ Adding {len(unique_new)} new recipes...")
    
    # Merge
    all_recipes = existing_recipes + unique_new
    
    # Save
    with open(data_path, 'w', encoding='utf-8') as f:
        json.dump(all_recipes, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Saved! Total recipes: {len(all_recipes)}")
    
    # Summary
    categories = {}
    cuisines = {}
    for recipe in all_recipes:
        cat = recipe.get('category', 'unknown')
        categories[cat] = categories.get(cat, 0) + 1
        cui = recipe.get('cuisine', 'unknown')
        cuisines[cui] = cuisines.get(cui, 0) + 1
    
    print("\n📂 Recipes by category:")
    for cat, count in sorted(categories.items()):
        print(f"  - {cat}: {count}")
    
    print("\n🌍 Recipes by cuisine:")
    for cui, count in sorted(cuisines.items()):
        print(f"  - {cui}: {count}")


if __name__ == '__main__':
    main()

