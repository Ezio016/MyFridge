/**
 * Ingredient Groups & Recipe Variants
 * 
 * Handles cases where:
 * 1. A single ingredient can be replaced by a GROUP of ingredients
 * 2. Recipe variants exist (e.g., "Teriyaki Chicken with bottled sauce" vs "from scratch")
 * 
 * Example: Teriyaki Sauce = Soy Sauce + Honey + Rice Vinegar + Sesame Oil + Garlic + Ginger
 */

/**
 * Define ingredient groups that can substitute for each other
 * Format:
 * {
 *   groupName: {
 *     primary: 'ready-made ingredient',
 *     components: ['ingredient1', 'ingredient2', ...],
 *     description: 'human-readable explanation'
 *   }
 * }
 */
export const INGREDIENT_GROUPS = {
  teriyakiSauce: {
    primary: 'teriyaki sauce',
    components: ['soy sauce', 'honey', 'rice vinegar', 'sesame oil', 'garlic', 'ginger'],
    description: 'Teriyaki sauce (or make your own: soy sauce, honey, rice vinegar, sesame oil, garlic, ginger)',
    category: 'sauce',
  },
  
  curryPaste: {
    primary: 'curry paste',
    components: ['curry powder', 'garlic', 'ginger', 'onion', 'oil'],
    description: 'Curry paste (or make your own: curry powder, garlic, ginger, onion, oil)',
    category: 'sauce',
  },
  
  pestoSauce: {
    primary: 'pesto',
    components: ['basil', 'garlic', 'pine nuts', 'parmesan', 'olive oil'],
    description: 'Pesto (or make your own: basil, garlic, pine nuts, parmesan, olive oil)',
    category: 'sauce',
  },
  
  tomatoSauce: {
    primary: 'marinara sauce',
    components: ['tomato', 'garlic', 'onion', 'olive oil', 'basil', 'oregano'],
    description: 'Marinara sauce (or make your own: tomatoes, garlic, onion, olive oil, herbs)',
    category: 'sauce',
  },
  
  alfredoSauce: {
    primary: 'alfredo sauce',
    components: ['butter', 'cream', 'parmesan', 'garlic'],
    description: 'Alfredo sauce (or make your own: butter, cream, parmesan, garlic)',
    category: 'sauce',
  },
}

/**
 * Check if a recipe ingredient can be satisfied by either:
 * 1. The primary ingredient (e.g., bottled teriyaki sauce)
 * 2. ALL components of the group (e.g., soy sauce + honey + vinegar + ...)
 * 
 * @param {string} recipeIngredient - The ingredient called for in the recipe
 * @param {Array<string>} inventoryItems - List of items in user's fridge
 * @returns {Object} { satisfied: boolean, method: 'primary'|'components'|'none', missing: [] }
 */
export const checkIngredientGroup = (recipeIngredient, inventoryItems) => {
  const cleanIng = (ing) => ing.toLowerCase().replace(/[^a-z\s]/g, '').trim()
  const recipeClean = cleanIng(recipeIngredient)
  const inventoryClean = inventoryItems.map(cleanIng)
  
  // Check if this ingredient is part of any group
  for (const [groupName, group] of Object.entries(INGREDIENT_GROUPS)) {
    const primaryMatch = inventoryClean.some(inv => 
      inv.includes(cleanIng(group.primary)) || cleanIng(group.primary).includes(inv)
    )
    
    // If user has the primary (bottled sauce), they're good!
    if (primaryMatch) {
      return {
        satisfied: true,
        method: 'primary',
        groupName,
        description: `Using ${group.primary}`,
        missing: [],
      }
    }
    
    // Check if recipe asks for the primary OR any component
    const isAskingForPrimary = recipeClean.includes(cleanIng(group.primary))
    const isAskingForComponent = group.components.some(comp => 
      recipeClean.includes(cleanIng(comp))
    )
    
    if (isAskingForPrimary || isAskingForComponent) {
      // Check if user has ALL components
      const missingComponents = []
      const hasAllComponents = group.components.every(comp => {
        const compClean = cleanIng(comp)
        const hasIt = inventoryClean.some(inv => 
          inv.includes(compClean) || compClean.includes(inv)
        )
        if (!hasIt) missingComponents.push(comp)
        return hasIt
      })
      
      if (hasAllComponents) {
        return {
          satisfied: true,
          method: 'components',
          groupName,
          description: `Making from scratch (${group.components.slice(0, 3).join(', ')}...)`,
          missing: [],
        }
      }
      
      // Neither primary nor all components available
      return {
        satisfied: false,
        method: 'none',
        groupName,
        description: group.description,
        missing: missingComponents,
        alternative: group.primary,
      }
    }
  }
  
  // Not part of any group
  return null
}

/**
 * For smart shopping: If user has all components, suggest they DON'T need the primary
 * If user has the primary, don't recommend components
 * 
 * @param {string} ingredient - Ingredient being considered for recommendation
 * @param {Array<string>} inventoryItems - Current inventory
 * @returns {Object} { shouldRecommend: boolean, reason: string }
 */
export const shouldRecommendIngredient = (ingredient, inventoryItems) => {
  const cleanIng = (ing) => ing.toLowerCase().replace(/[^a-z\s]/g, '').trim()
  const ingClean = cleanIng(ingredient)
  const inventoryClean = inventoryItems.map(cleanIng)
  
  for (const [groupName, group] of Object.entries(INGREDIENT_GROUPS)) {
    const isPrimary = ingClean.includes(cleanIng(group.primary))
    const isComponent = group.components.some(comp => ingClean.includes(cleanIng(comp)))
    
    if (isPrimary) {
      // Check if user already has all components
      const hasAllComponents = group.components.every(comp => {
        const compClean = cleanIng(comp)
        return inventoryClean.some(inv => inv.includes(compClean) || compClean.includes(inv))
      })
      
      if (hasAllComponents) {
        return {
          shouldRecommend: false,
          reason: `You can make ${group.primary} from ingredients you have`,
        }
      }
      
      return {
        shouldRecommend: true,
        reason: `Quick shortcut instead of making from scratch`,
      }
    }
    
    if (isComponent) {
      // Check if user already has the primary
      const hasPrimary = inventoryClean.some(inv => 
        inv.includes(cleanIng(group.primary)) || cleanIng(group.primary).includes(inv)
      )
      
      if (hasPrimary) {
        return {
          shouldRecommend: false,
          reason: `You already have ${group.primary}`,
        }
      }
    }
  }
  
  return { shouldRecommend: true, reason: null }
}

/**
 * Get a user-friendly explanation for why an ingredient is marked as available
 * 
 * @param {string} recipeIngredient - Recipe ingredient
 * @param {Array<string>} inventoryItems - User's inventory
 * @returns {string} Human-readable explanation
 */
export const getIngredientGroupExplanation = (recipeIngredient, inventoryItems) => {
  const result = checkIngredientGroup(recipeIngredient, inventoryItems)
  
  if (!result || !result.satisfied) return null
  
  if (result.method === 'primary') {
    return `✓ ${result.description}`
  } else if (result.method === 'components') {
    return `✓ ${result.description}`
  }
  
  return null
}

