# Enhanced Recipe Card Schema

**Version:** 2.1  
**Purpose:** Comprehensive recipe information for rich, informative recipe cards

---

## 🎯 Philosophy

A great recipe card should tell the **complete story** of a dish:
- What it is and where it comes from
- How it tastes and feels
- What makes it special
- How to customize it
- Tips for success

---

## 📋 Enhanced Schema

### **Core Fields** (Existing)
```json
{
  "id": "string",
  "source": "string",
  "name": "string",
  "description": "string (50-200 chars, quick overview)",
  "prep_time": "number",
  "cook_time": "number",
  "total_time": "number",
  "servings": "number",
  "difficulty": "easy|medium|hard",
  "ingredients": ["array"],
  "instructions": ["array"],
  "category": "string",
  "tags": ["array"],
  "cuisine": "string",
  "image_url": "string",
  "ingredients_structured": ["array"]
}
```

### **NEW: Extended Information** (Rich Content)
```json
{
  "about": {
    "long_description": "string (detailed, 200-500 words)",
    "origin": {
      "region": "string (e.g., 'Northern Italy', 'Southern USA')",
      "history": "string (cultural/historical context)",
      "traditional_context": "string (when/how it's traditionally served)"
    },
    "what_makes_it_special": "string (what sets this recipe apart)"
  },
  
  "flavor_profile": {
    "primary_flavors": ["array (sweet, savory, spicy, tangy, umami, bitter)"],
    "intensity": "mild|moderate|bold",
    "texture": "string (creamy, crunchy, tender, chewy, etc.)",
    "aroma": "string (description of smell)",
    "mouthfeel": "string (rich, light, silky, hearty, etc.)"
  },
  
  "variations": [
    {
      "name": "string (e.g., 'Vegetarian Version')",
      "description": "string (what changes)",
      "ingredient_swaps": [
        {
          "original": "string (ingredient to replace)",
          "substitute": "string (replacement)",
          "notes": "string (how it affects the dish)"
        }
      ]
    }
  ],
  
  "serving_suggestions": {
    "best_served": "string (hot, cold, room temp, etc.)",
    "pairs_well_with": ["array (side dishes, beverages)"],
    "garnish_ideas": ["array (optional garnishes)"],
    "presentation_tips": "string (plating suggestions)"
  },
  
  "storage": {
    "refrigerator": {
      "duration": "string (e.g., '3-5 days')",
      "container": "string (airtight, covered, etc.)",
      "notes": "string"
    },
    "freezer": {
      "can_freeze": "boolean",
      "duration": "string (e.g., '2-3 months')",
      "thawing_instructions": "string",
      "quality_notes": "string (what happens when frozen/thawed)"
    },
    "reheating": {
      "best_method": "string (microwave, oven, stovetop)",
      "instructions": "string (detailed reheating steps)",
      "tips": "string (how to maintain quality)"
    }
  },
  
  "tips_and_tricks": {
    "pro_tips": ["array (expert advice)"],
    "common_mistakes": ["array (what to avoid)"],
    "time_savers": ["array (shortcuts)"],
    "make_ahead": "string (how to prep in advance)"
  },
  
  "nutrition_highlights": {
    "key_nutrients": ["array (e.g., 'High in protein', 'Good source of fiber')"],
    "dietary_notes": ["array (e.g., 'Low carb', 'Heart healthy')"],
    "allergen_warnings": ["array (contains dairy, nuts, etc.)"]
  },
  
  "skill_building": {
    "techniques_learned": ["array (cooking skills this recipe teaches)"],
    "difficulty_explanation": "string (why easy/medium/hard)",
    "beginner_friendly": "boolean",
    "advanced_variations": "string (how to level up)"
  },
  
  "community": {
    "average_rating": "number (1-5)",
    "review_count": "number",
    "featured_reviews": [
      {
        "author": "string",
        "rating": "number",
        "comment": "string",
        "date": "string",
        "helpful_count": "number"
      }
    ],
    "chef_notes": "string (notes from recipe creator)",
    "user_modifications": ["array (popular user tweaks)"]
  }
}
```

---

## 📖 Field Explanations

### **about.long_description**
A thorough, engaging description (200-500 words) that covers:
- What the dish is
- What makes it delicious
- Who will love it
- Perfect occasions for serving it
- Sensory experience (taste, smell, texture)

**Example:**
```
"This Classic Italian Carbonara is the ultimate comfort food—a silky, 
creamy pasta dish made with just a few simple ingredients that come 
together to create something magical. Unlike Americanized versions 
with heavy cream, authentic carbonara gets its luxurious texture from 
the perfect emulsion of eggs, pasta water, and Parmigiano-Reggiano 
cheese. The crispy guanciale (or pancetta) adds a salty, savory depth 
that perfectly complements the rich sauce.

What makes this recipe special is its simplicity and elegance. There's 
no cream, no garlic, no complications—just pure Italian technique. 
The heat from the hot pasta gently cooks the eggs without scrambling 
them, creating a sauce that clings to every strand. Each bite delivers 
that perfect balance of salty pork, sharp cheese, and creamy richness.

This dish is perfect for a cozy weeknight dinner when you want 
something impressive but don't have hours to cook. It's also a 
wonderful date-night meal that shows you know your way around the 
kitchen. The whole thing comes together in about 20 minutes, making 
it ideal for busy evenings when takeout just won't cut it."
```

### **flavor_profile**
Detailed breakdown of the dish's sensory characteristics:

**primary_flavors:**
- `sweet` - Caramelized onions, honey, fruit
- `savory` - Umami, meaty, brothy
- `spicy` - Heat from peppers, spices
- `tangy` - Acidic, citrus, vinegar
- `umami` - Savory depth, mushrooms, soy sauce
- `bitter` - Coffee, dark chocolate, certain greens
- `salty` - Natural saltiness

**Example:**
```json
{
  "primary_flavors": ["savory", "umami", "salty"],
  "intensity": "bold",
  "texture": "Silky smooth sauce coating tender pasta with crispy pork bits",
  "aroma": "Rich, eggy, with hints of sharp cheese and toasted pork",
  "mouthfeel": "Creamy and luxurious, each strand perfectly coated"
}
```

### **variations**
Different ways to make the dish (dietary, regional, preference-based):

**Example:**
```json
{
  "variations": [
    {
      "name": "Vegetarian Carbonara",
      "description": "Plant-based version using mushrooms for umami depth",
      "ingredient_swaps": [
        {
          "original": "Guanciale (or pancetta)",
          "substitute": "Smoked mushrooms + miso paste",
          "notes": "Provides similar smoky, umami flavors without meat"
        },
        {
          "original": "Egg yolks",
          "substitute": "Cashew cream + nutritional yeast",
          "notes": "Creates creamy texture with cheesy flavor"
        }
      ]
    },
    {
      "name": "Roman-Style (Traditional)",
      "description": "Ultra-authentic version with guanciale and pecorino",
      "ingredient_swaps": [
        {
          "original": "Pancetta",
          "substitute": "Guanciale (pork jowl)",
          "notes": "Traditional choice, more flavorful and fatty"
        },
        {
          "original": "Parmesan",
          "substitute": "Pecorino Romano",
          "notes": "Sharper, saltier, more traditional"
        }
      ]
    }
  ]
}
```

### **serving_suggestions**
How to serve and what to serve with:

**Example:**
```json
{
  "best_served": "Immediately while hot (the sauce will continue to thicken as it cools)",
  "pairs_well_with": [
    "Simple arugula salad with lemon vinaigrette",
    "Garlic bread or focaccia",
    "Dry white wine (Pinot Grigio or Vermentino)",
    "Sparkling water with lemon"
  ],
  "garnish_ideas": [
    "Extra grated Parmesan",
    "Freshly cracked black pepper",
    "Chopped fresh parsley",
    "Red pepper flakes (for heat)"
  ],
  "presentation_tips": "Twirl pasta into a nest shape on the plate, top with extra crispy pancetta, and finish with a generous crack of black pepper"
}
```

### **storage**
Complete storage and reheating guide:

**Example:**
```json
{
  "refrigerator": {
    "duration": "2-3 days",
    "container": "Airtight container, store sauce separately if possible",
    "notes": "Sauce may thicken; add a splash of pasta water when reheating"
  },
  "freezer": {
    "can_freeze": false,
    "duration": "Not recommended",
    "quality_notes": "Egg-based sauce doesn't freeze well—eggs can become grainy when thawed"
  },
  "reheating": {
    "best_method": "Stovetop with added pasta water",
    "instructions": "Heat gently in a pan over low heat, adding 2-3 tablespoons of pasta water or milk to loosen the sauce. Stir constantly to prevent eggs from scrambling. Heat just until warm, not boiling.",
    "tips": "Don't microwave on high—the eggs can scramble. Use 50% power in 30-second intervals if using microwave."
  }
}
```

### **tips_and_tricks**
Insider knowledge for success:

**Example:**
```json
{
  "pro_tips": [
    "Reserve at least 1 cup of pasta water—the starchy water is essential for creating the silky sauce",
    "Mix the egg mixture with some hot pasta water first (tempering) to prevent scrambling",
    "Remove the pan from heat before adding the eggs—residual heat is enough to cook them",
    "Use room temperature eggs—they combine more smoothly with the hot pasta",
    "Toss quickly and confidently—hesitation leads to clumping"
  ],
  "common_mistakes": [
    "Adding eggs to too-hot pasta → Results in scrambled eggs instead of creamy sauce",
    "Not saving enough pasta water → Can't thin the sauce properly",
    "Using cold eggs → They don't emulsify well with hot pasta",
    "Overcooking the pancetta → Becomes tough instead of crispy",
    "Adding cream → Not traditional and makes it heavy"
  ],
  "time_savers": [
    "Cook pancetta while water boils for pasta",
    "Mix eggs and cheese ahead of time",
    "Use pre-grated Parmesan (though fresh is better)"
  ],
  "make_ahead": "This dish is best made fresh, but you can prep ingredients: dice pancetta, grate cheese, and mix egg mixture up to 2 hours ahead (keep refrigerated)"
}
```

### **nutrition_highlights**
Health information without full nutritional breakdown:

**Example:**
```json
{
  "key_nutrients": [
    "High in protein (from eggs and pork)",
    "Good source of calcium (from cheese)",
    "Provides iron and B vitamins"
  ],
  "dietary_notes": [
    "High in calories and fat—a special occasion dish",
    "Can be made lower-carb with zucchini noodles",
    "Naturally gluten-free if using GF pasta"
  ],
  "allergen_warnings": [
    "Contains: Eggs, Dairy (cheese)",
    "Contains: Pork (not suitable for vegetarians/vegans)",
    "Contains: Wheat (if using regular pasta)"
  ]
}
```

### **skill_building**
Educational aspect:

**Example:**
```json
{
  "techniques_learned": [
    "Tempering eggs (preventing scrambling)",
    "Creating an emulsion (pasta water + fat + protein)",
    "Rendering fat from pork",
    "Timing multiple components",
    "Working with residual heat"
  ],
  "difficulty_explanation": "Rated 'medium' because while ingredients are simple, the technique of creating a creamy sauce without scrambling eggs requires attention and practice. The timing is crucial but becomes second nature after making it once or twice.",
  "beginner_friendly": false,
  "advanced_variations": "Master the basic recipe, then try adding white wine reduction to the pancetta, or experiment with different pasta shapes and regional cheese varieties"
}
```

### **community**
Social/review features:

**Example:**
```json
{
  "average_rating": 4.8,
  "review_count": 1247,
  "featured_reviews": [
    {
      "author": "Maria K.",
      "rating": 5,
      "comment": "Finally made authentic carbonara! The tip about tempering the eggs was a game-changer. My Italian grandmother would be proud.",
      "date": "2026-01-15",
      "helpful_count": 234
    },
    {
      "author": "James R.",
      "rating": 4,
      "comment": "Delicious! I scrambled the eggs on my first attempt, but followed the tips more carefully the second time and it was perfect.",
      "date": "2026-01-10",
      "helpful_count": 89
    }
  ],
  "chef_notes": "The key to perfect carbonara is confidence and timing. Don't be intimidated—once you make it successfully once, you'll never forget how. Start with room temperature eggs and always reserve extra pasta water. You've got this! —Chef Antonio",
  "user_modifications": [
    "Some users add a splash of white wine to the pancetta",
    "Popular variation: half Parmesan, half Pecorino Romano for more complex flavor",
    "Many home cooks use bacon instead of guanciale for easier sourcing"
  ]
}
```

---

## 🎨 Template Structure

See `recipe_templates/template_enhanced_recipe.json` for a complete example.

---

## 📊 Implementation Phases

### **Phase 1: Core Enhancement** (Immediate)
Add these essential fields:
- `about.long_description`
- `flavor_profile`
- `variations` (at least 2-3)
- `serving_suggestions`

### **Phase 2: Practical Information** (Next)
Add helpful details:
- `storage` (full object)
- `tips_and_tricks`
- `nutrition_highlights`

### **Phase 3: Community Features** (Future)
Add social elements:
- `community.average_rating`
- `community.featured_reviews`
- User-generated content

---

## 🔄 Backward Compatibility

**Existing recipes without enhanced fields will continue to work!**

The app should gracefully handle:
- Missing `about` object → Show only basic description
- Missing `flavor_profile` → Don't display flavor section
- Missing `variations` → Show "No variations available"

---

## 📝 Content Writing Guidelines

### **Long Description** (200-500 words)
Structure:
1. **Opening** (1-2 sentences): What is it?
2. **What makes it special** (2-3 sentences): Why is it delicious/unique?
3. **Sensory experience** (2-3 sentences): How does it taste, smell, look?
4. **Perfect for** (1-2 sentences): Who/when/where to serve it?
5. **Closing** (1 sentence): Call to action or final appeal

### **Tips Writing**
- Be specific and actionable
- Explain the "why" behind each tip
- Use measurements and temperatures
- Include visual cues (e.g., "until golden brown")

### **Variations**
- Focus on practical, tested variations
- Explain how the variation changes the dish
- Include dietary adaptations when relevant

---

## 💡 Example: Complete Enhanced Recipe

See `recipe_templates/template_enhanced_carbonara.json` for a full example of the enhanced schema in action.

---

## 🎯 Benefits of Enhanced Recipe Cards

✅ **Better User Experience** - Users know exactly what to expect  
✅ **Educational** - Users learn techniques and cooking knowledge  
✅ **Customization** - Variations help users adapt recipes  
✅ **Trust** - Detailed information builds confidence  
✅ **Engagement** - Rich content keeps users on the page longer  
✅ **SEO** - More content = better search engine visibility  
✅ **Community** - Reviews and ratings build social proof  

---

**Last Updated:** 2026-01-29  
**Schema Version:** 2.1
