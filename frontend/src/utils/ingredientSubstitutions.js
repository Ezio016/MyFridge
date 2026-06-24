/**
 * Ingredient Substitution System
 * Defines which ingredients can substitute for each other, with context awareness
 */

// Substitution groups: ingredients that are often interchangeable
export const SUBSTITUTION_GROUPS = {
  // Cooking fats/oils (interchangeable for sautéing, frying, general cooking)
  cooking_fats: {
    primary: ['oil', 'olive oil', 'vegetable oil', 'canola oil', 'sunflower oil', 'avocado oil'],
    butter: ['butter', 'ghee', 'clarified butter'],
    all: ['oil', 'olive oil', 'vegetable oil', 'canola oil', 'sunflower oil', 'butter', 'ghee', 'clarified butter'],
    context: ['sauté', 'fry', 'cook', 'stir fry', 'pan fry', 'sear', 'brown']
  },

  // Baking fats (NOT always interchangeable - butter has different properties)
  baking_fats: {
    primary: ['butter', 'margarine'],
    alternatives: ['coconut oil', 'shortening'],
    not_substitutable: ['olive oil', 'vegetable oil'], // Don't substitute liquid oils in baking
    context: ['bake', 'pastry', 'cake', 'cookie', 'dough', 'frosting']
  },

  // Vinegars (often interchangeable in dressings, marinades)
  vinegars: {
    all: ['vinegar', 'white vinegar', 'red wine vinegar', 'apple cider vinegar', 'rice vinegar', 'balsamic vinegar'],
    specialty: ['balsamic vinegar'], // Less substitutable
    context: ['dressing', 'marinade', 'pickle', 'sauce']
  },

  // Soy sauces and similar umami liquids
  soy_based: {
    all: ['soy sauce', 'tamari', 'liquid aminos', 'coconut aminos'],
    context: ['season', 'marinade', 'stir fry', 'asian']
  },

  // Milk and dairy alternatives
  milk: {
    dairy: ['milk', 'whole milk', '2% milk', 'skim milk', 'half and half', 'cream'],
    non_dairy: ['almond milk', 'soy milk', 'oat milk', 'coconut milk'],
    all: ['milk', 'whole milk', 'almond milk', 'soy milk', 'oat milk', 'coconut milk'],
    context: ['cereal', 'smoothie', 'sauce', 'soup']
  },

  // Proteins (in some contexts)
  ground_meat: {
    all: ['ground beef', 'ground turkey', 'ground chicken', 'ground pork'],
    context: ['taco', 'burger', 'meatball', 'bolognese', 'chili']
  },

  chicken_cuts: {
    all: ['chicken breast', 'chicken thigh', 'chicken drumstick', 'chicken tender'],
    preferred: ['chicken breast', 'chicken thigh'], // Most versatile
    context: ['grill', 'bake', 'roast', 'pan fry']
  },

  // Sweeteners
  sugar: {
    granulated: ['sugar', 'white sugar', 'granulated sugar', 'cane sugar'],
    brown: ['brown sugar', 'coconut sugar', 'demerara sugar'],
    alternatives: ['honey', 'maple syrup', 'agave nectar'],
    context: ['sweeten', 'bake', 'dessert']
  },

  // Tomato products
  tomato_products: {
    sauce: ['tomato sauce', 'marinara sauce', 'tomato puree'],
    crushed: ['crushed tomatoes', 'diced tomatoes', 'chopped tomatoes'],
    paste: ['tomato paste', 'tomato concentrate'],
    context: ['sauce', 'pasta', 'curry', 'stew']
  },

  // Herbs (fresh ↔ dried, but not always 1:1)
  basil: {
    all: ['basil', 'fresh basil', 'dried basil'],
    ratio: { fresh: 1, dried: 0.33 } // 1 tbsp fresh = 1 tsp dried
  },

  oregano: {
    all: ['oregano', 'fresh oregano', 'dried oregano'],
    ratio: { fresh: 1, dried: 0.33 }
  },

  parsley: {
    all: ['parsley', 'fresh parsley', 'dried parsley'],
    ratio: { fresh: 1, dried: 0.33 }
  },
}

/**
 * Check if two ingredients are substitutable in a given context
 */
export function areSubstitutable(ingredient1, ingredient2, recipeContext = '') {
  const ing1 = ingredient1.toLowerCase()
  const ing2 = ingredient2.toLowerCase()

  // Exact match
  if (ing1 === ing2) return true

  // Check each substitution group
  for (const [groupName, group] of Object.entries(SUBSTITUTION_GROUPS)) {
    const allItems = group.all || []
    const hasIng1 = allItems.some(item => ing1.includes(item) || item.includes(ing1))
    const hasIng2 = allItems.some(item => ing2.includes(item) || item.includes(ing2))

    if (hasIng1 && hasIng2) {
      // Both in same group - check context if specified
      if (group.context && recipeContext) {
        const contextMatch = group.context.some(ctx => 
          recipeContext.toLowerCase().includes(ctx)
        )
        
        // If context matters and doesn't match, not substitutable
        if (!contextMatch && group.not_substitutable) {
          const isNotSub = group.not_substitutable.some(item => 
            ing1.includes(item) || ing2.includes(item)
          )
          if (isNotSub) return false
        }
        
        return contextMatch || !group.context
      }
      
      return true
    }
  }

  return false
}

/**
 * Get all possible substitutes for an ingredient
 */
export function getSubstitutes(ingredient) {
  const ing = ingredient.toLowerCase()
  const substitutes = new Set()

  for (const [groupName, group] of Object.entries(SUBSTITUTION_GROUPS)) {
    const allItems = group.all || []
    const hasIng = allItems.some(item => ing.includes(item) || item.includes(ing))

    if (hasIng) {
      allItems.forEach(item => {
        if (item !== ing && !ing.includes(item)) {
          substitutes.add(item)
        }
      })
    }
  }

  return Array.from(substitutes)
}

/**
 * Normalize ingredient name to canonical form for grouping
 */
export function normalizeIngredient(ingredient) {
  const ing = ingredient.toLowerCase()

  // Map to canonical form
  for (const [groupName, group] of Object.entries(SUBSTITUTION_GROUPS)) {
    const allItems = group.all || []
    const primary = group.primary ? group.primary[0] : allItems[0]
    
    const match = allItems.find(item => ing.includes(item) || item.includes(ing))
    if (match) {
      return primary // Return the primary/canonical form
    }
  }

  return ingredient // Return as-is if no group found
}

/**
 * Check if user's inventory has a suitable substitute for a recipe ingredient
 */
export function hasSubstituteInInventory(recipeIngredient, inventory, recipeContext = '') {
  const normalized = normalizeIngredient(recipeIngredient)
  
  return inventory.some(item => 
    areSubstitutable(item.name, normalized, recipeContext)
  )
}

/**
 * Find which inventory items can substitute for a recipe ingredient
 */
export function findSubstitutesInInventory(recipeIngredient, inventory, recipeContext = '') {
  const normalized = normalizeIngredient(recipeIngredient)
  
  return inventory.filter(item => 
    areSubstitutable(item.name, normalized, recipeContext)
  )
}

/**
 * Recipe name similarity detection (for grouping variants)
 */
export function areRecipeVariants(recipe1Name, recipe2Name) {
  const name1 = recipe1Name.toLowerCase()
  const name2 = recipe2Name.toLowerCase()

  // Remove common variations
  const clean1 = name1
    .replace(/\s+with\s+.*/g, '') // Remove "with X"
    .replace(/\s+using\s+.*/g, '') // Remove "using X"
    .replace(/\s+\(.*?\)/g, '') // Remove parentheses
    .trim()

  const clean2 = name2
    .replace(/\s+with\s+.*/g, '')
    .replace(/\s+using\s+.*/g, '')
    .replace(/\s+\(.*?\)/g, '')
    .trim()

  // Check if base names match
  if (clean1 === clean2) return true

  // Check if one is substring of other (e.g., "Chicken Curry" and "Quick Chicken Curry")
  if (clean1.includes(clean2) || clean2.includes(clean1)) {
    return true
  }

  // Calculate word overlap
  const words1 = clean1.split(/\s+/)
  const words2 = clean2.split(/\s+/)
  const commonWords = words1.filter(w => words2.includes(w) && w.length > 3)
  
  // If 70%+ words match, likely variants
  const similarity = (commonWords.length * 2) / (words1.length + words2.length)
  return similarity >= 0.7
}

export default {
  SUBSTITUTION_GROUPS,
  areSubstitutable,
  getSubstitutes,
  normalizeIngredient,
  hasSubstituteInInventory,
  findSubstitutesInInventory,
  areRecipeVariants
}

