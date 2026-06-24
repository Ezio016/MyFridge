import { useState, useEffect } from 'react'
import { ChefHat, Clock, ArrowLeft, Check, Heart, ShoppingCart, Search, X, Send, Loader, Palette } from 'lucide-react'
import { inventoryAPI, recipeAPI, chatAPI, userAPI } from '../api/client'
import { API_BASE } from '../api/config'
import { useAuth } from '../context/AuthContext'
import { useFavorites } from '../hooks/useFavorites'
import { addMultipleToCart } from '../utils/cartUtils'
import { areSubstitutable, hasSubstituteInInventory, findSubstitutesInInventory, areRecipeVariants } from '../utils/ingredientSubstitutions'
import { checkIngredientGroup, getIngredientGroupExplanation } from '../utils/ingredientGroups'
import styles from './Chef.module.css'

const MODE = {
  LOADING: 'loading',
  RECIPES: 'recipes',
  COOKING: 'cooking',
  CUSTOMIZING: 'customizing',
}

function Chef() {
  const [mode, setMode] = useState(MODE.LOADING)
  const [inventory, setInventory] = useState([])
  const [baseRecipes, setBaseRecipes] = useState([]) // Ranked/base order from backend + local ranking logic
  const [currentPage, setCurrentPage] = useState(1)
  const [recipesPerPage] = useState(12) // Show 12 recipes per page
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedRecipe, setSelectedRecipe] = useState(null)
  const [completedSteps, setCompletedSteps] = useState([])
  const [loading, setLoading] = useState(false)
  const [showCustomizationChat, setShowCustomizationChat] = useState(false)
  const [customizedIngredients, setCustomizedIngredients] = useState(null)
  const [customizedSteps, setCustomizedSteps] = useState(null)
  const [chatMessages, setChatMessages] = useState([])
  const [userInput, setUserInput] = useState('')
  const [isProcessing, setIsProcessing] = useState(false)
  const [flavorProfile, setFlavorProfile] = useState(null)
  const [loadingFlavor, setLoadingFlavor] = useState(false)
  const [remixSwapOut, setRemixSwapOut] = useState('')
  const [remixSwapIn, setRemixSwapIn] = useState('')
  const [remixLoading, setRemixLoading] = useState(false)
  const { favorites, isFavorite, toggleFavorite } = useFavorites()
  const { user, token, isAuthenticated } = useAuth()
  
  // User's flavor preference profile (accumulated from likes, cooks, shops)
  const [userFlavorProfile, setUserFlavorProfile] = useState(() => {
    const saved = localStorage.getItem('userFlavorProfile')
    return saved ? JSON.parse(saved) : {
      sweet: 0, salty: 0, sour: 0, bitter: 0, 
      umami: 0, spicy: 0, fatty: 0, aromatic: 0,
      totalInteractions: 0
    }
  })
  
  // Load user flavor profile from server if authenticated
  useEffect(() => {
    if (isAuthenticated && token) {
      loadUserFlavorProfile()
    }
  }, [isAuthenticated, token])
  
  const loadUserFlavorProfile = async () => {
    try {
      const profile = await userAPI.getFlavorProfile(token)
      if (profile) {
        setUserFlavorProfile(profile)
      }
    } catch (err) {
      console.log('Could not load user flavor profile:', err)
    }
  }
  
  // Simple keyword filters - just an array of strings
  const [keywordFilters, setKeywordFilters] = useState([])
  
  const DEFAULT_CONTROLS = {
    filters: { expiringOnly: false, readyOnly: false },
    customization: { diet: null, excludeIngredients: [] },
    sort: { by: 'ranked', direction: 'asc' },
  }
  const [controlsState, setControlsState] = useState(DEFAULT_CONTROLS)

  useEffect(() => {
    const initializeData = async () => {
      const inventoryItems = await loadInventory() // Load inventory first
      loadRecipes(inventoryItems) // Pass inventory directly to loadRecipes
    }
    initializeData()
  }, [])

  const loadInventory = async () => {
    try {
      const items = await inventoryAPI.getAll()
      console.log('🧊 Loaded inventory items:', items)
      console.log('📝 Inventory names:', items.map(i => i.name))
      
      // DEBUG: Check expiry status for each item
      console.log('\n' + '🔴'.repeat(30))
      console.log('INVENTORY EXPIRY STATUS CHECK:')
      items.forEach(item => {
        const emoji = item.expiry_status === 'expired' ? '❌ EXPIRED' : 
                      item.expiry_status === 'expiring_soon' ? '⚠️ EXPIRING' : '✅ FRESH'
        console.log(`  ${emoji}: ${item.name} (status: "${item.expiry_status}", days: ${item.days_until_expiry})`)
      })
      console.log('🔴'.repeat(30) + '\n')
      
      setInventory(items)
      return items // Return items so they can be used immediately
    } catch (err) {
      console.error('Failed to load inventory:', err)
      return []
    }
  }

  const expiringItems = inventory.filter(i => i.expiry_status === 'expiring_soon')
  const expiringCount = expiringItems.length

  const normalizeControlsState = (state) => {
    const s = state && typeof state === 'object' ? state : {}
    const filters = s.filters && typeof s.filters === 'object' ? s.filters : {}
    const customization = s.customization && typeof s.customization === 'object' ? s.customization : {}
    const sort = s.sort && typeof s.sort === 'object' ? s.sort : {}

    return {
      filters: {
        expiringOnly: !!filters.expiringOnly,
        readyOnly: !!filters.readyOnly,
        maxTimeMinutes: typeof filters.maxTimeMinutes === 'number' ? filters.maxTimeMinutes : null,
        maxMissingMain: typeof filters.maxMissingMain === 'number' ? filters.maxMissingMain : null,
        difficulty: Array.isArray(filters.difficulty) ? filters.difficulty : null,
        includeTags: Array.isArray(filters.includeTags) ? filters.includeTags : [],
        excludeTags: Array.isArray(filters.excludeTags) ? filters.excludeTags : [],
        mealType: filters.mealType || null,
      },
      customization: {
        diet: customization.diet || null,
        excludeIngredients: Array.isArray(customization.excludeIngredients) ? customization.excludeIngredients : [],
        includeIngredients: Array.isArray(customization.includeIngredients) ? customization.includeIngredients : [],
        cuisine: customization.cuisine || null,
        spiceLevel: customization.spiceLevel || null,
      },
      sort: {
        by: sort.by || 'ranked',
        direction: sort.direction || 'asc',
      },
    }
  }

  const applyControls = (recipes, rawControls) => {
    const c = normalizeControlsState(rawControls)
    let out = [...recipes]

    // Simple keyword filtering - ALL keywords must match (AND logic)
    if (keywordFilters.length > 0) {
      out = out.filter(recipe => {
        const searchText = [
          recipe.name || '',
          ...(recipe.ingredients || []),
          recipe.description || '',
          ...(recipe.tags || []),
          recipe.cuisine || ''
        ].join(' ').toLowerCase()
        
        // Recipe must match ALL keywords (either include or exclude)
        return keywordFilters.every(keyword => {
          // Check if it's a negation (no/without/exclude)
          if (keyword.startsWith('no ') || keyword.startsWith('without ') || keyword.startsWith('exclude ')) {
            // Extract the ingredient to exclude
            const toExclude = keyword.replace(/^(no|without|exclude)\s+/, '').trim()
            // Recipe must NOT contain this ingredient
            return !searchText.includes(toExclude)
          } else {
            // Recipe must contain this keyword
            return searchText.includes(keyword)
          }
        })
      })
    }

    const includesAny = (arr, v) => Array.isArray(arr) && arr.some(x => `${x}`.toLowerCase() === `${v}`.toLowerCase())
    const ingText = (r) => (r.ingredients || []).join(' ').toLowerCase()

    const MEAT = [
      // Poultry
      'chicken', 'turkey', 'duck', 'goose', 'quail',
      // Red Meat
      'beef', 'pork', 'lamb', 'veal', 'mutton', 'goat', 'venison',
      // Processed Meats
      'bacon', 'ham', 'sausage', 'chorizo', 'salami', 'pepperoni', 'prosciutto', 'pastrami', 'hot dog', 'bratwurst',
      // Fish & Seafood
      'fish', 'salmon', 'tuna', 'cod', 'haddock', 'tilapia', 'snapper', 'trout', 'bass', 'halibut', 'mahi', 'catfish',
      'shrimp', 'prawn', 'crab', 'lobster', 'crawfish', 'clam', 'mussel', 'oyster', 'scallop', 'squid', 'octopus',
      'anchovy', 'sardine', 'mackerel', 'herring',
      // Specific cuts/preparations (use whole words to avoid false positives)
      ' steak', ' ribs', ' wings', ' drumstick', ' thigh', ' breast',
      'ground beef', 'ground pork', 'ground chicken', 'ground turkey',
      'beef mince', 'pork mince', 'chicken mince',
      'pork chop', 'lamb chop',
      'chicken stock', 'beef stock', 'fish stock', 'bone broth',
      'gelatin', 'gelatine',
      // Other
      ' meat', 'seafood', 'poultry'
    ]
    const DAIRY_EGG = ['milk', 'cheese', 'butter', 'yogurt', 'yoghurt', 'cream', 'egg', 'eggs', 'ghee', 'whey', 'casein', 'lactose']
    const GLUTEN = ['flour', 'bread', 'pasta', 'noodle', 'tortilla', 'bun', 'bagel', 'couscous', 'semolina', 'wheat', 'barley', 'rye', 'malt']

    const isVegetarian = (r) => !MEAT.some(k => ingText(r).includes(k))
    const isVegan = (r) => isVegetarian(r) && !DAIRY_EGG.some(k => ingText(r).includes(k))
    const isGlutenFree = (r) => !GLUTEN.some(k => ingText(r).includes(k))

    // Filters
    if (c.filters.expiringOnly) out = out.filter(r => !!r.usesExpiring)
    if (c.filters.readyOnly) out = out.filter(r => !!r.hasAll)
    if (typeof c.filters.maxTimeMinutes === 'number') out = out.filter(r => (r.time || 0) <= c.filters.maxTimeMinutes)
    if (typeof c.filters.maxMissingMain === 'number') out = out.filter(r => (r.missingMainCount ?? 0) <= c.filters.maxMissingMain)
    if (Array.isArray(c.filters.difficulty) && c.filters.difficulty.length > 0) out = out.filter(r => includesAny(c.filters.difficulty, r.level))
    if (c.filters.includeTags.length > 0) out = out.filter(r => (r.tags || []).some(t => c.filters.includeTags.includes(t)))
    if (c.filters.excludeTags.length > 0) out = out.filter(r => !(r.tags || []).some(t => c.filters.excludeTags.includes(t)))
    
    // Meal type filter - match by tags or recipe name patterns
    if (c.filters.mealType) {
      const mealPatterns = {
        breakfast: ['breakfast', 'morning', 'pancake', 'waffle', 'eggs', 'omelette', 'omelet', 'toast', 'cereal', 'smoothie', 'muffin', 'bagel'],
        lunch: ['lunch', 'sandwich', 'salad', 'wrap', 'soup', 'bowl'],
        dinner: ['dinner', 'steak', 'roast', 'pasta', 'casserole', 'stew', 'curry', 'stir fry', 'grilled'],
        snack: ['snack', 'appetizer', 'dip', 'chips', 'bites', 'finger food', 'popcorn', 'nuts', 'trail mix'],
      }
      const patterns = mealPatterns[c.filters.mealType] || []
      out = out.filter(r => {
        const nameAndTags = `${r.name} ${(r.tags || []).join(' ')}`.toLowerCase()
        return patterns.some(p => nameAndTags.includes(p))
      })
    }

    // Customization (ingredient-based)
    if (c.customization.excludeIngredients.length > 0) {
      const blocked = c.customization.excludeIngredients.map(x => `${x}`.toLowerCase())
      out = out.filter(r => !blocked.some(b => ingText(r).includes(b)))
    }
    if (c.customization.includeIngredients.length > 0) {
      const required = c.customization.includeIngredients.map(x => `${x}`.toLowerCase())
      // Use .every() for AND logic - recipe must contain ALL required ingredients
      out = out.filter(r => required.every(b => ingText(r).includes(b)))
    }
    if (c.customization.diet === 'vegetarian') out = out.filter(isVegetarian)
    if (c.customization.diet === 'vegan') out = out.filter(isVegan)
    if (c.customization.diet === 'gluten_free') out = out.filter(isGlutenFree)
    
    // Cuisine filter
    if (c.customization.cuisine) {
      const cuisineQuery = c.customization.cuisine.toLowerCase()
      out = out.filter(r => {
        const recipeCuisine = (r.cuisine || '').toLowerCase()
        const recipeTags = (r.tags || []).map(t => t.toLowerCase())
        const recipeName = (r.name || '').toLowerCase()
        return recipeCuisine.includes(cuisineQuery) || 
               recipeTags.some(t => t.includes(cuisineQuery)) ||
               recipeName.includes(cuisineQuery)
      })
    }
    
    // Spice level filter
    if (c.customization.spiceLevel) {
      const spicyKeywords = ['pepper', 'chili', 'chile', 'jalapeño', 'habanero', 'cayenne', 
                             'paprika', 'hot sauce', 'sriracha', 'red pepper flakes', 
                             'curry', 'spicy', 'heat', 'hot', 'fire']
      out = out.filter(r => {
        const text = `${ingText(r)} ${r.name} ${(r.tags || []).join(' ')}`.toLowerCase()
        return spicyKeywords.some(keyword => text.includes(keyword))
      })
    }

    // Sorting: keep base ranked order unless user explicitly changes sort
    const direction = c.sort.direction === 'desc' ? -1 : 1
    if (c.sort.by && c.sort.by !== 'ranked') {
      out = out
        .map((r, idx) => ({ r, idx }))
        .sort((a, b) => {
          if (c.sort.by === 'fastest' || c.sort.by === 'time_asc') return direction * ((a.r.time || 0) - (b.r.time || 0)) || (a.idx - b.idx)
          if (c.sort.by === 'fewest_missing') return direction * ((a.r.missingMainCount ?? 0) - (b.r.missingMainCount ?? 0)) || (a.idx - b.idx)
          if (c.sort.by === 'most_popular' || c.sort.by === 'popularity') return direction * -1 * ((a.r.popularity_score || 0) - (b.r.popularity_score || 0)) || (a.idx - b.idx)
          if (c.sort.by === 'alphabetical') return direction * (`${a.r.name}`.localeCompare(`${b.r.name}`)) || (a.idx - b.idx)
          return a.idx - b.idx
        })
        .map(x => x.r)
    }

    return out
  }

  const chefFacets = (() => {
    const times = baseRecipes.map(r => r.time).filter(n => typeof n === 'number')
    const diffs = Array.from(new Set(baseRecipes.map(r => r.level).filter(Boolean))).sort()
    return {
      totals: {
        total: baseRecipes.length,
        ready: baseRecipes.filter(r => r.hasAll).length,
        expiring: baseRecipes.filter(r => r.usesExpiring).length,
      },
      ranges: {
        time: times.length ? { min: Math.min(...times), max: Math.max(...times) } : null,
      },
      difficulties: diffs,
      availableSorts: ['ranked', 'fastest', 'fewest_missing', 'most_popular', 'alphabetical'],
    }
  })()

  const loadRecipes = async (inventoryItems = null) => {
    setMode(MODE.LOADING)
    setLoading(true)
    setControlsState(DEFAULT_CONTROLS)
    setCurrentPage(1) // Reset to first page

    // Use passed inventory or state inventory
    const currentInventory = inventoryItems || inventory

    try {
      console.log(`🍳 Loading recipes from database...`)
      console.log(`🧊 Using inventory with ${currentInventory.length} items`)
      
      // Get ALL recipes for exploration
      const response = await recipeAPI.getAll()
      
      if (!response || !response.recipes || response.recipes.length === 0) {
        throw new Error('No recipes found in database')
      }
      
      console.log(`✅ Got ${response.recipes.length} recipes from database`)
      
      // Check inventory expiry status ONCE (not per recipe)
      console.log('\n' + '='.repeat(60))
      console.log('🧊 INVENTORY EXPIRY STATUS:')
      console.log('='.repeat(60))
      currentInventory.forEach(i => {
        const status = i.expiry_status || 'unknown'
        const emoji = status === 'expired' ? '❌' : status === 'expiring_soon' ? '⚠️' : '✅'
        console.log(`${emoji} ${i.name}: ${status} (days: ${i.days_until_expiry})`)
      })
      
      // Filter out expired items (check multiple conditions)
      const inventoryNames = currentInventory
        .filter(i => {
          // Method 1: Check expiry_status
          let isExpired = i.expiry_status === 'expired'
          
          // Method 2: Check days_until_expiry (negative = expired)
          if (!isExpired && typeof i.days_until_expiry === 'number' && i.days_until_expiry < 0) {
            isExpired = true
          }
          
          // Method 3: Check expiration_date directly
          if (!isExpired && i.expiration_date) {
            const expiryDate = new Date(i.expiration_date)
            const today = new Date()
            today.setHours(0, 0, 0, 0)
            expiryDate.setHours(0, 0, 0, 0)
            if (expiryDate < today) {
              isExpired = true
            }
          }
          
          if (isExpired) {
            console.log(`🚫 EXCLUDING EXPIRED: ${i.name}`)
          } else {
            console.log(`✅ KEEPING: ${i.name} (status: ${i.expiry_status}, days: ${i.days_until_expiry})`)
          }
          return !isExpired
        })
        .map(i => i.name.toLowerCase())
      
      console.log('\n✅ AVAILABLE INVENTORY (after filtering):')
      console.log(inventoryNames)
      
      // SPECIFIC CHECK FOR BREAD
      const hasBread = inventoryNames.some(n => n.includes('bread'))
      console.log('\n🍞 BREAD CHECK: Is bread in available list?', hasBread)
      if (hasBread) {
        console.error('⚠️ WARNING: Bread is still in available list but should be expired!')
      }
      console.log('='.repeat(60) + '\n')
      
      // Transform database recipes to match our UI format
      const formattedRecipes = response.recipes.map((r, idx) => {
        // Use the filtered inventoryNames for matching
        
        // Debug first recipe
        if (idx === 0) {
          console.log('🔍 First recipe:', r.name)
          console.log('📋 Recipe ingredients:', r.ingredients)
          console.log('📊 Structured ingredients:', r.ingredients_structured)
          console.log('🧊 Inventory we have:', inventoryNames)
        }
        
        // Use structured ingredients if available
        const useStructuredIngredients = r.ingredients_structured && Array.isArray(r.ingredients_structured)
        
        // For structured ingredients, we can skip pantry detection - use classification directly
        const isOptionalIngredient = (ing, structuredIng) => {
          if (structuredIng) {
            return structuredIng.classification === 'optional' || structuredIng.classification === 'common'
          }
          // Fallback to keyword detection
          return isPantryStapleFallback(ing)
        }
        
        // Fallback pantry staple detection (for old recipes without structured data)
        const isPantryStapleFallback = (ing) => {
          const ingLower = ing.toLowerCase().trim()
          
          // Optional/serving ingredients (toppings, garnishes, enhancements)
          const optionalKeywords = [
            'for serving', 'for garnish', 'optional', 'to taste',
            'maple syrup', 'honey', 'powdered sugar', 'confectioners',
            'fresh berries', 'fresh fruit', 'whipped cream',
            'vanilla extract', 'almond extract', 'cinnamon', 'nutmeg'
          ]
          if (optionalKeywords.some(k => ingLower.includes(k))) {
            return true // Treat as optional/available
          }
          
          // Specialty ingredients are NEVER pantry staples (150+ keywords)
          const specialtyKeywords = [
            // Specialty flours
            'chickpea', 'almond', 'coconut', 'rice flour', 'cornmeal',
            'semolina', 'buckwheat', 'rye', 'spelt', 'quinoa flour',
            'oat flour', 'whole wheat', 'bread flour', 'cake flour', 'self-raising',
            
            // Specialty dairy & cheeses
            'parmesan', 'parmigiano', 'cheddar', 'mozzarella', 'feta',
            'goat cheese', 'blue cheese', 'brie', 'camembert', 'gruyere',
            'cream cheese', 'sour cream', 'heavy cream', 'whipping cream', 'double cream',
            'greek yogurt', 'buttermilk', 'ricotta', 'mascarpone',
            
            // Specialty proteins
            'prosciutto', 'pancetta', 'bacon', 'sausage', 'chorizo',
            'lamb', 'veal', 'duck', 'venison', 'salmon', 'tuna',
            'shrimp', 'prawns', 'lobster', 'crab', 'scallops',
            'anchovies', 'sardines', 'beef', 'pork', 'chicken breast',
            
            // Specialty produce
            'avocado', 'eggplant', 'aubergine', 'zucchini', 'courgette',
            'asparagus', 'artichoke', 'fennel', 'leek', 'shallot',
            'kale', 'arugula', 'rocket', 'spinach', 'bok choy',
            'broccoli', 'cauliflower', 'brussels sprouts', 'beetroot',
            
            // Specialty condiments
            'tahini', 'miso', 'curry paste', 'fish sauce', 'oyster sauce',
            'hoisin', 'sriracha', 'harissa', 'pesto', 'capers',
            'olives', 'sun-dried tomato', 'tomato paste', 'tomato puree',
            
            // Specialty herbs & spices
            'saffron', 'cardamom', 'turmeric', 'cumin', 'coriander',
            'paprika', 'cayenne', 'chili powder', 'curry powder',
            'garam masala', 'five spice', 'oregano', 'thyme',
            'rosemary', 'basil', 'cilantro', 'parsley', 'dill',
            'mint', 'sage', 'tarragon', 'bay leaf',
            
            // Specialty nuts/seeds
            'pine nuts', 'cashews', 'pistachios', 'hazelnuts',
            'macadamia', 'pecans', 'walnuts', 'almonds',
            'sesame seeds', 'sunflower seeds', 'pumpkin seeds',
            'chia seeds', 'flax seeds',
            
            // Specialty sweeteners
            'honey', 'maple syrup', 'agave', 'molasses',
            'brown sugar', 'powdered sugar', 'confectioners',
            
            // Specialty grains/legumes
            'quinoa', 'couscous', 'bulgur', 'farro', 'barley',
            'lentils', 'chickpeas', 'black beans', 'kidney beans',
            'basmati rice', 'jasmine rice', 'arborio',
            
            // Specialty liquids
            'coconut milk', 'almond milk', 'wine', 'beer', 'sherry',
            'stock', 'broth', 'bouillon',
            
            // Fresh items (always specialty)
            'fresh', 'ripe', 'bunch', 'handful', 'sprig'
          ]
          if (specialtyKeywords.some(keyword => ingLower.includes(keyword))) {
            return false
          }
          
          // Only basic pantry staples (cooking fats, basic seasonings, universal items)
          const basicPantry = [
            'salt', 'pepper', 'water', 
            'olive oil', 'vegetable oil', 'cooking oil', 'oil', 'cooking spray',
            'butter', 'margarine',
            'sugar', 'all-purpose flour', 'flour',
            'garlic', 'onion',
            'vanilla extract', 'cinnamon', 'nutmeg' // Common baking basics
          ]
          
          // Exact or close match to basic pantry items
          return basicPantry.some(staple => {
            // For flour, must be "flour" alone or "all-purpose flour" 
            if (staple === 'flour' || staple === 'all-purpose flour') {
              return ingLower === 'flour' || 
                     ingLower === 'all-purpose flour' || 
                     ingLower === 'plain flour' ||
                     (ingLower.includes('flour') && !ingLower.includes(' flour'))
            }
            
            // For pepper (spice), must NOT be vegetable peppers
            if (staple === 'pepper') {
              // Only match the spice, not vegetable peppers
              return (ingLower === 'pepper' || 
                      ingLower === 'black pepper' || 
                      ingLower === 'white pepper' ||
                      ingLower === 'ground pepper' ||
                      ingLower.includes('peppercorn')) &&
                     // Exclude all vegetable peppers
                     !ingLower.includes('bell pepper') &&
                     !ingLower.includes('padron') &&
                     !ingLower.includes('jalapeno') &&
                     !ingLower.includes('chili pepper') &&
                     !ingLower.includes('red pepper') &&
                     !ingLower.includes('green pepper') &&
                     !ingLower.includes('yellow pepper') &&
                     !ingLower.includes('sweet pepper') &&
                     !ingLower.includes('hot pepper') &&
                     !ingLower.includes('shishito') &&
                     !ingLower.includes('poblano') &&
                     !ingLower.includes('serrano') &&
                     !ingLower.includes('habanero') &&
                     !ingLower.includes('cayenne pepper') && // cayenne is a spice but often called "pepper"
                     !ingLower.includes('peppers') // plural usually means vegetables
            }
            
            // For garlic/onion, must be the vegetable not powder
            if (staple === 'garlic') {
              return (ingLower === 'garlic' || 
                      ingLower.includes('garlic clove') ||
                      ingLower.includes('fresh garlic')) &&
                     !ingLower.includes('garlic powder')
            }
            
            if (staple === 'onion') {
              return (ingLower.includes('onion')) &&
                     !ingLower.includes('onion powder')
            }
            
            return ingLower === staple || ingLower.includes(staple)
          })
        }
        
        // Smart ingredient matching helper with substitution support
        const matchIngredient = (recipeIng, inventoryIng, recipeContext = '') => {
          // Ingredients that should NEVER match each other (strict barriers)
          const nonSubstitutable = {
            'tortilla': ['bread', 'naan', 'pita', 'baguette', 'roll', 'bun'],
            'bread': ['tortilla', 'rice', 'pasta', 'noodle'],
            'rice': ['pasta', 'noodle', 'bread', 'quinoa', 'couscous'],
            'pasta': ['rice', 'noodle', 'bread'],
            'noodle': ['rice', 'pasta', 'bread'],
            'chicken': ['beef', 'pork', 'lamb', 'turkey', 'duck'],
            'beef': ['chicken', 'pork', 'lamb', 'turkey'],
            'pork': ['chicken', 'beef', 'lamb', 'turkey'],
            'shrimp': ['chicken', 'beef', 'pork', 'fish', 'crab'],
            'fish': ['chicken', 'beef', 'pork', 'shrimp'],
            'tofu': ['chicken', 'beef', 'pork', 'tempeh'],
            'milk': ['cream', 'yogurt', 'buttermilk'], // Note: removed butter/oil - now handled by substitution system
            'cream': ['milk', 'yogurt'],
            'cheese': ['yogurt', 'cream cheese'],
            'potato': ['sweet potato', 'yam'],
            'sweet potato': ['potato', 'yam']
          }
          
          // Remove filler words that don't change the ingredient
          const fillers = ['fresh', 'frozen', 'mixed', 'chopped', 'diced', 'sliced', 
                          'minced', 'dried', 'canned', 'cooked', 'raw', 'whole',
                          'ground', 'shredded', 'grated', 'crushed', 'peeled', 'large', 'small']
          
          const cleanIngredient = (ing) => {
            let cleaned = ing.toLowerCase().trim()
            fillers.forEach(filler => {
              cleaned = cleaned.replace(new RegExp(`\\b${filler}\\b`, 'g'), '')
            })
            return cleaned.replace(/\s+/g, ' ').trim()
          }
          
          const recipeClean = cleanIngredient(recipeIng)
          const invClean = cleanIngredient(inventoryIng)
          
          // Check if these ingredients are explicitly non-substitutable
          for (const [key, incompatible] of Object.entries(nonSubstitutable)) {
            if (recipeClean.includes(key)) {
              for (const incompat of incompatible) {
                if (invClean.includes(incompat)) {
                  return false // Definitely not a match
                }
              }
            }
            if (invClean.includes(key)) {
              for (const incompat of incompatible) {
                if (recipeClean.includes(incompat)) {
                  return false // Definitely not a match
                }
              }
            }
          }
          
          // Exact match after cleaning
          if (recipeClean === invClean) return { match: true, exact: true }
          
          // One fully contains the other (e.g., "vegetables" contains "vegetable")
          if (recipeClean.includes(invClean) || invClean.includes(recipeClean)) return { match: true, exact: true }
          
          // Check substitution system (butter ↔ ghee, oil variations, etc.)
          const recipeNameLower = r.name.toLowerCase()
          const recipeInstructionsLower = r.instructions?.join(' ').toLowerCase() || ''
          const contextClues = recipeNameLower + ' ' + recipeInstructionsLower
          
          if (areSubstitutable(recipeClean, invClean, contextClues)) {
            return { match: true, exact: false, substitute: invClean }
          }
          
          // Check if MOST significant words match (not just ANY word)
          const recipeWords = recipeClean.split(' ').filter(w => w.length > 2)
          const invWords = invClean.split(' ').filter(w => w.length > 2)
          
          // If either is a single word, require exact match
          if (recipeWords.length === 1 || invWords.length === 1) {
            const wordMatch = recipeWords.some(rw => invWords.includes(rw))
            return wordMatch ? { match: true, exact: true } : { match: false }
          }
          
          // For multi-word ingredients, require at least 50% word overlap
          const matchingWords = recipeWords.filter(rw => invWords.includes(rw))
          const overlapRatio = matchingWords.length / Math.min(recipeWords.length, invWords.length)
          
          return overlapRatio >= 0.5 ? { match: true, exact: true } : { match: false }
        }
        
        const hasIngredient = r.ingredients.map((ing, ingIdx) => {
          const structuredIng = useStructuredIngredients ? r.ingredients_structured[ingIdx] : null
          // Assume they have optional/common ingredients
          if (isOptionalIngredient(ing, structuredIng)) {
            return { has: true, original: ing, matched: 'optional' }
          }
          
          // Check for ingredient GROUPS first (e.g., teriyaki sauce or components)
          const groupCheck = checkIngredientGroup(ing, inventoryNames)
          if (groupCheck && groupCheck.satisfied) {
            return {
              has: true,
              original: ing,
              matched: groupCheck.description,
              method: groupCheck.method, // 'primary' or 'components'
              groupName: groupCheck.groupName,
              isGroup: true
          }
          }
          
          // Check if in fridge with smart matching
          for (const inv of inventoryNames) {
            const matchResult = matchIngredient(ing, inv)
            if (matchResult.match) {
              return {
                has: true,
                original: ing,
                matched: inv,
                exact: matchResult.exact,
                substitute: matchResult.substitute
              }
            }
          }
          
          // Check if this is part of an unsatisfied group (provide helpful message)
          if (groupCheck && !groupCheck.satisfied) {
            return { 
              has: false, 
              original: ing,
              groupInfo: {
                description: groupCheck.description,
                missing: groupCheck.missing,
                alternative: groupCheck.alternative
              }
            }
          }
          
          return { has: false, original: ing }
        })
        
        // Separate main vs optional ingredients
        const isOptional = r.ingredients.map((ing, ingIdx) => {
          const structuredIng = useStructuredIngredients ? r.ingredients_structured[ingIdx] : null
          return isOptionalIngredient(ing, structuredIng)
        })
        
        const mainIngredients = r.ingredients.filter((_, i) => !isOptional[i])
        const optionalIngredients = r.ingredients.filter((_, i) => isOptional[i])
        
        const hasMain = mainIngredients.map(ing => {
          // Universal ingredients that everyone has (check whole word match)
          const universalIngredients = ['water', 'ice cubes', 'ice cube', 'hot water', 'cold water', 'tap water', 'boiling water']
          const ingLower = ing.toLowerCase()
          // Use word boundary check - ingredient must START with or CONTAIN the word surrounded by spaces/punctuation
          const isUniversal = universalIngredients.some(u => {
            // Check if ingredient starts with the universal word or contains it as a whole word
            const regex = new RegExp(`\\b${u}\\b`, 'i')
            return regex.test(ingLower)
          })
          if (isUniversal) {
            return {
              has: true,
              original: ing,
              matched: 'Always available',
              universal: true
            }
          }
          
          // Check for ingredient groups first
          const groupCheck = checkIngredientGroup(ing, inventoryNames)
          if (groupCheck && groupCheck.satisfied) {
            return {
              has: true,
              original: ing,
              matched: groupCheck.description,
              method: groupCheck.method,
              groupName: groupCheck.groupName,
              isGroup: true
            }
          }
          
          // Then check regular matching
          for (const inv of inventoryNames) {
            const matchResult = matchIngredient(ing, inv)
            if (matchResult.match) {
              return {
                has: true,
                original: ing,
                matched: inv,
                exact: matchResult.exact,
                substitute: matchResult.substitute
              }
            }
          }
          
          // DEBUG: Log if bread is being checked but not found
          if (ing.toLowerCase().includes('bread')) {
            console.log(`🍞 BREAD INGREDIENT CHECK:`)
            console.log(`   Looking for: "${ing}"`)
            console.log(`   Available inventory: ${inventoryNames.join(', ')}`)
            console.log(`   Has bread in list: ${inventoryNames.some(n => n.includes('bread'))}`)
          }
          
          // If part of unsatisfied group, provide info
          if (groupCheck && !groupCheck.satisfied) {
            return { 
              has: false, 
              original: ing,
              groupInfo: {
                description: groupCheck.description,
                missing: groupCheck.missing,
                alternative: groupCheck.alternative
              }
            }
          }
          
          return { has: false, original: ing }
        })
        
        // Check which optional ingredients are actually in inventory
        const hasOptional = optionalIngredients.map(ing => {
          // Universal ingredients that everyone has (check whole word match)
          const universalIngredients = ['water', 'ice cubes', 'ice cube', 'hot water', 'cold water', 'tap water', 'boiling water']
          const ingLower = ing.toLowerCase()
          // Use word boundary check - ingredient must START with or CONTAIN the word surrounded by spaces/punctuation
          const isUniversal = universalIngredients.some(u => {
            const regex = new RegExp(`\\b${u}\\b`, 'i')
            return regex.test(ingLower)
          })
          if (isUniversal) {
            return {
              has: true,
              original: ing,
              matched: 'Always available',
              universal: true
            }
          }
          
          // Check for ingredient groups first
          const groupCheck = checkIngredientGroup(ing, inventoryNames)
          if (groupCheck && groupCheck.satisfied) {
            return {
              has: true,
              original: ing,
              matched: groupCheck.description,
              method: groupCheck.method,
              groupName: groupCheck.groupName,
              isGroup: true
            }
          }
          
          // Then check regular matching
          for (const inv of inventoryNames) {
            const matchResult = matchIngredient(ing, inv)
            if (matchResult.match) {
              return {
                has: true,
                original: ing,
                matched: inv,
                exact: matchResult.exact,
                substitute: matchResult.substitute
              }
            }
          }
          return { has: false, original: ing }
        })
        
        const missingMainCount = hasMain.filter(h => !h.has).length
        const totalMainCount = mainIngredients.length
        const missingCount = hasIngredient.filter(h => !h.has).length
        
        const hasAtLeastOneMain = hasMain.some(h => h.has) // Has at least 1 main ingredient

        // Mark if this recipe uses any expiring-soon inventory items (best-effort match)
        const currentExpiringItems = currentInventory.filter(i => i.expiry_status === 'expiring_soon')
        const expiringNames = currentExpiringItems.map(i => i.name.toLowerCase())
        const usesExpiring = r.ingredients.some(ing =>
          expiringNames.some(exp => matchIngredient(ing, exp).match)
        )
        
        return {
          id: r.id || `recipe_${idx}`,
          name: r.name,
          time: r.total_time || r.cook_time + r.prep_time,
          level: r.difficulty || 'easy',
          usesExpiring,
          ingredients: r.ingredients,
          mainIngredients,
          optionalIngredients,
          hasIngredient,
          hasMain,
          hasOptional,
          isOptional,
          missingCount,
          missingMainCount,
          totalMainCount,
          hasAll: missingMainCount === 0, // Only care about main ingredients
          hasAtLeastOneMain, // New: for lightning filtering
          steps: r.instructions,
          description: r.description,
          tags: r.tags || [],
          image_url: r.image_url,
          popularity_score: r.popularity_score || 0 // Add popularity score
        }
      })
      
      // Sort all recipes by readiness + popularity
      const sorted = [...formattedRecipes].sort((a, b) => {
        // 1. Green recipes (hasAll) come first
        if (a.hasAll && !b.hasAll) return -1
        if (!a.hasAll && b.hasAll) return 1
        
        // 2. Within same readiness level, sort by missing count
        if (a.missingMainCount !== b.missingMainCount) {
          return a.missingMainCount - b.missingMainCount
        }
        
        // 3. If same readiness, sort by popularity score (higher = better)
        return (b.popularity_score || 0) - (a.popularity_score || 0)
      })
      console.log(`🍳 Loaded ${sorted.length} recipes (${sorted.filter(r => r.hasAll).length} ready to cook)`)
      setBaseRecipes(sorted)
      
      setMode(MODE.RECIPES)
    } catch (err) {
      console.error('❌ Recipe error:', err)
      alert(`Recipe Error: ${err.message || 'Something went wrong'}. Check your connection!`)
      setMode(MODE.RECIPES)
      setBaseRecipes([])
    } finally {
      setLoading(false)
    }
  }

  let viewRecipes = applyControls(baseRecipes, controlsState)

  // Apply search filter
  if (searchQuery.trim()) {
    const query = searchQuery.toLowerCase()
    viewRecipes = viewRecipes.filter(recipe => 
      recipe.name.toLowerCase().includes(query) ||
      recipe.description?.toLowerCase().includes(query) ||
      recipe.tags?.some(tag => tag.toLowerCase().includes(query)) ||
      recipe.ingredients?.some(ing => ing.toLowerCase().includes(query))
    )
  }

  // Pagination logic
  const totalRecipes = viewRecipes.length
  const totalPages = Math.ceil(totalRecipes / recipesPerPage)
  const startIndex = (currentPage - 1) * recipesPerPage
  const endIndex = startIndex + recipesPerPage
  const paginatedRecipes = viewRecipes.slice(startIndex, endIndex)

  const goToPage = (page) => {
    setCurrentPage(page)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  const selectRecipe = (recipe) => {
    console.log('📖 Selected Recipe:', recipe.name)
    console.log('   All ingredients:', recipe.ingredients)
    console.log('   Main ingredients:', recipe.mainIngredients)
    console.log('   Optional ingredients:', recipe.optionalIngredients)
    
    // Detailed has Main check
    console.log('\n🔍 DETAILED MAIN INGREDIENT STATUS:')
    recipe.mainIngredients.forEach((ing, i) => {
      const status = recipe.hasMain?.[i]
      console.log(`   ${status?.has ? '✓' : '✗'} "${ing}" => has: ${status?.has}, matched: "${status?.matched || 'none'}"`)
    })
    
    console.log('   Has Main:', recipe.hasMain)
    console.log('   Has Optional:', recipe.hasOptional)
    
    setSelectedRecipe(recipe)
    setCompletedSteps([])
    setMode(MODE.COOKING)
    setShowCustomizationChat(false)
    setCustomizedIngredients(null)
    setCustomizedSteps(null)
    setChatMessages([])
    setFlavorProfile(null)
    
    // Fetch flavor profile for this recipe
    fetchFlavorProfile(recipe)
  }
  
  const fetchFlavorProfile = async (recipe) => {
    if (!recipe) return
    setLoadingFlavor(true)
    try {
      const res = await fetch(`${API_BASE}/lab/flavor/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ingredients: recipe.ingredients || [] })
      })
      const data = await res.json()
      if (data.success) {
        setFlavorProfile(data.flavor_profile)
      }
    } catch (err) {
      console.log('Could not load flavor profile:', err)
    } finally {
      setLoadingFlavor(false)
    }
  }
  
  const updateUserFlavorProfile = async (recipeFlavorProfile, interactionType = 'view', recipeId = null) => {
    // If authenticated, use API to track interaction
    if (isAuthenticated && token && recipeId) {
      try {
        const result = await userAPI.logInteraction(token, recipeId, interactionType)
        if (result.updated_flavor_profile) {
          setUserFlavorProfile(result.updated_flavor_profile)
        }
        return
      } catch (err) {
        console.log('API interaction logging failed, using local:', err)
      }
    }
    
    // Fallback to local storage for guests
    if (!recipeFlavorProfile?.normalized_vector) return
    
    const weights = { view: 0.1, like: 0.5, cook: 0.8, shop: 0.3 }
    const weight = weights[interactionType] || 0.1
    const dims = ['sweet', 'salty', 'sour', 'bitter', 'umami', 'spicy', 'fatty', 'aromatic']
    
    setUserFlavorProfile(prev => {
      const updated = { ...prev, totalInteractions: (prev.totalInteractions || 0) + 1 }
      dims.forEach((dim, i) => {
        const flavorVal = recipeFlavorProfile.normalized_vector[i] || 0
        updated[dim] = (prev[dim] || 0) + (flavorVal * weight)
      })
      localStorage.setItem('userFlavorProfile', JSON.stringify(updated))
      return updated
    })
  }
  
  const getFlavorColor = (flavor) => {
    const colors = {
      sweet: '#ff6b9d', salty: '#4fc3f7', sour: '#ffeb3b', bitter: '#8d6e63',
      umami: '#ff7043', spicy: '#f44336', fatty: '#ffb74d', aromatic: '#ab47bc',
    }
    return colors[flavor] || '#9e9e9e'
  }
  
  const handleQuickRemix = async () => {
    if (!remixSwapOut.trim() || !remixSwapIn.trim() || !selectedRecipe) return
    
    setRemixLoading(true)
    try {
      const res = await fetch(`${API_BASE}/lab/remix`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          recipe_id: selectedRecipe.id,
          swap_ingredient: remixSwapOut.trim(),
          new_ingredient: remixSwapIn.trim()
        })
      })
      
      const data = await res.json()
      if (data.success && data.remixed_recipe) {
        // Apply the remixed ingredients
        setCustomizedIngredients(data.remixed_recipe.ingredients)
        setRemixSwapOut('')
        setRemixSwapIn('')
      }
    } catch (err) {
      console.error('Remix failed:', err)
      alert('Failed to remix recipe. Try again.')
    } finally {
      setRemixLoading(false)
    }
  }

  const handleSendCustomization = async () => {
    if (!userInput.trim() || isProcessing) return

    const userMessage = userInput.trim()
    setUserInput('')
    
    setChatMessages(prev => [...prev, { role: 'user', content: userMessage }])
    setIsProcessing(true)

    try {
      // Prepare recipe data for the backend
      const recipeData = {
        id: selectedRecipe.id,
        name: selectedRecipe.name,
        description: selectedRecipe.description || '',
        ingredients: selectedRecipe.ingredients,
        instructions: selectedRecipe.steps,
        time: selectedRecipe.time,
        difficulty: selectedRecipe.level,
        tags: selectedRecipe.tags || []
      }

      console.log('🔧 Sending customization request:', { recipeData, userMessage })
      const response = await chatAPI.customizeRecipe(recipeData, userMessage)
      console.log('✅ Customization response:', response)

      if (response && response.ingredients) {
        setCustomizedIngredients(response.ingredients)
        setCustomizedSteps(response.steps)
        
        setChatMessages(prev => [...prev, {
          role: 'assistant',
          content: response.ai_response || 'Done! I\'ve updated the recipe.'
        }])
      } else {
        setChatMessages(prev => [...prev, {
          role: 'assistant',
          content: response?.ai_response || "I couldn't process that request. Try rephrasing?"
        }])
      }
    } catch (error) {
      console.error('Customization error:', error)
      const errorMessage = error.message || "Oops! Something went wrong. Please try again."
      setChatMessages(prev => [...prev, {
        role: 'assistant',
        content: `Error: ${errorMessage}`
      }])
    } finally {
      setIsProcessing(false)
    }
  }

  const handleRevert = () => {
    setCustomizedIngredients(null)
    setCustomizedSteps(null)
    setShowCustomizationChat(false)
    setChatMessages([])
    setUserInput('')
  }

  const toggleStep = (index) => {
    setCompletedSteps(prev => 
      prev.includes(index) 
        ? prev.filter(i => i !== index)
        : [...prev, index]
    )
  }

  const goHome = () => {
    setMode(MODE.RECIPES)
    setCurrentPage(1)
    setSelectedRecipe(null)
    setCompletedSteps([])
    // Don't reset controlsState - preserve user's filters when going back
  }

  const handleSaveNewRecipe = (newRecipe) => {
    // Add the new custom recipe to the base recipes
    setBaseRecipes(prev => [newRecipe, ...prev])
  }



  return (
    <div className={styles.page}>
      <div className="container">
        
        {/* LOADING */}
        {mode === MODE.LOADING && (
          <div className={styles.loadingView}>
            <div className={styles.avatarCircle + ' ' + styles.cooking}>
              <ChefHat size={48} />
            </div>
            <p>Finding recipes... 🍳</p>
          </div>
        )}

        {/* RECIPES GRID */}
        {mode === MODE.RECIPES && (
          <div className={styles.recipesView}>
            <div className={styles.recipesHeader}>
              <h2>🍳 Recipes</h2>
              
              {/* Search Bar */}
              <div className={styles.searchWrapper}>
                <Search size={18} className={styles.searchIcon} />
                <input
                  type="text"
                  className={styles.searchInput}
                  placeholder="Search recipes..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
                {searchQuery && (
                  <button 
                    className={styles.clearSearch}
                    onClick={() => setSearchQuery('')}
                    aria-label="Clear search"
                  >
                    <X size={18} />
                  </button>
                )}
              </div>
            </div>

            {/* Filter Bar - 2x2 Grid */}
            <div className={styles.filterBar}>
              {/* 2x2 Grid for Buttons */}
              <div className={styles.filterGrid}>
                {/* Top Left: Type of Meal */}
                <select
                  className={styles.dropdownButton}
                  value={controlsState.filters?.mealType || ''}
                  onChange={(e) => {
                        setControlsState(prev => {
                          const n = normalizeControlsState(prev)
                          return {
                            ...n,
                        filters: { ...n.filters, mealType: e.target.value || null },
                          }
                        })
                      }}
                    >
                  <option value="">Type of Meal</option>
                  <option value="breakfast">Breakfast</option>
                  <option value="lunch">Lunch</option>
                  <option value="dinner">Dinner</option>
                  <option value="snack">Snack</option>
                </select>

                {/* Top Right: Only Use Ingredients in Fridge */}
                  <button
                  className={`${styles.ingredientsButton} ${controlsState.filters?.readyOnly ? styles.active : ''}`}
                    onClick={() => {
                      setControlsState(prev => {
                        const n = normalizeControlsState(prev)
                        return { ...n, filters: { ...n.filters, readyOnly: !n.filters.readyOnly } }
                      })
                    }}
                  >
                  ✨ Only Use ingredients in Fridge
                  </button>

                {/* Bottom Left: Prep Time */}
                <select
                  className={styles.dropdownButton}
                  value={controlsState.filters?.maxTimeMinutes || ''}
                  onChange={(e) => {
                    setControlsState(prev => {
                      const n = normalizeControlsState(prev)
                      return { ...n, filters: { ...n.filters, maxTimeMinutes: e.target.value ? parseInt(e.target.value) : null } }
                    })
                  }}
                >
                  <option value="">Prep Time</option>
                  <option value="5">Under 5 minutes</option>
                  <option value="15">Under 15 minutes</option>
                  <option value="30">Under 30 minutes</option>
                  <option value="60">Under 1 hour</option>
                </select>

                {/* Bottom Right: Search Box */}
                <div className={styles.searchBoxCell}>
                  <input
                    type="text"
                    className={styles.searchBox}
                    placeholder="Type any keyword to filter... (pork, vegan, spicy, italian, etc.)"
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && e.target.value.trim()) {
                        const keyword = e.target.value.trim().toLowerCase()
                        // Add keyword if not already in filters
                        if (!keywordFilters.includes(keyword)) {
                          setKeywordFilters([...keywordFilters, keyword])
                        }
                        e.target.value = ''
                      }
                    }}
                  />
                </div>
              </div>
            </div>

            {/* Active Filters Display */}
            {keywordFilters.length > 0 && (
              <div className={styles.activeFilters}>
                <div className={styles.activeFiltersHeader}>
                  <span className={styles.activeFiltersTitle}>Active Filters:</span>
                  <button 
                    className={styles.resetBtn}
                    onClick={() => setKeywordFilters([])}
                  >
                    Reset All
                  </button>
                </div>
                <div className={styles.filterTagsContainer}>
                  {/* Simple keyword filter tags */}
                  {keywordFilters.map((keyword, idx) => (
                    <div key={`keyword-${idx}`} className={styles.filterTag}>
                      <span className={styles.filterTagLabel}>
                        🔍 {keyword}
                      </span>
                      <button
                        className={styles.filterTagRemove}
                        onClick={() => {
                          setKeywordFilters(keywordFilters.filter((_, i) => i !== idx))
                        }}
                        aria-label={`Remove ${keyword} filter`}
                      >
                        <X size={14} />
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {viewRecipes.length === 0 ? (
              <div className={styles.noRecipes}>
                <p>No recipes match your filters</p>
                <button onClick={() => setControlsState(DEFAULT_CONTROLS)}>Reset filters</button>
              </div>
            ) : (
              <>
                {/* Recipe Count and Sort */}
                <div className={styles.recipeHeader}>
                <div className={styles.recipeCount}>
                  <p>🍳 Showing {startIndex + 1}-{Math.min(endIndex, totalRecipes)} of {totalRecipes} recipes</p>
                  </div>
                  
                  {/* Sort Dropdown - Above recipes on the right */}
                  <div className={styles.sortDropdown}>
                    <label>Sort by:</label>
                    <select
                      value={controlsState.sort?.by || 'ranked'}
                      onChange={(e) => {
                        setControlsState(prev => {
                          const n = normalizeControlsState(prev)
                          return { ...n, sort: { ...n.sort, by: e.target.value } }
                        })
                      }}
                    >
                      <option value="ranked">Best Match</option>
                      <option value="time_asc">Fastest</option>
                      <option value="popularity">Most Popular</option>
                    </select>
                  </div>
                </div>
              <div className={styles.recipesGrid}>
                  {paginatedRecipes.map((recipe) => (
                  <div 
                    key={recipe.id}
                    className={`${styles.recipeCard} ${recipe.hasAll ? styles.hasAll : styles.missing}`}
                  >
                    <div className={styles.cardTop}>
                      <span className={styles.time}>
                        <Clock size={14} />
                        {recipe.time}m
                      </span>
                      <span className={styles.level}>{recipe.level}</span>
                      <button
                        className={`${styles.favoriteBtn} ${isFavorite(recipe.id) ? styles.favorited : ''}`}
                        onClick={(e) => {
                          e.stopPropagation()
                          toggleFavorite(recipe)
                        }}
                      >
                        <Heart size={18} fill={isFavorite(recipe.id) ? 'currentColor' : 'none'} />
                      </button>
                    </div>
                    
                    <h3 onClick={() => selectRecipe(recipe)}>{recipe.name}</h3>
                    
                    <div className={styles.cardBottom} onClick={() => selectRecipe(recipe)}>
                      {recipe.hasAll ? (
                        <span className={styles.ready}>✓ Ready to cook</span>
                      ) : (
                        <div className={styles.ingredientStatus}>
                          <span className={styles.needItems}>
                            Main: {recipe.totalMainCount - recipe.missingMainCount}/{recipe.totalMainCount}
                          </span>
                          {recipe.optionalIngredients.length > 0 && (
                            <span className={styles.optionalItems}>
                              + {recipe.optionalIngredients.length} optional
                            </span>
                          )}
                        </div>
                      )}
                      {recipe.usesExpiring && (
                        <span className={styles.expiringTag}>🔥 Uses expiring</span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
              
              {/* Pagination */}
              {totalPages > 1 && (
                <div className={styles.pagination}>
                  <button 
                    className={styles.pageBtn}
                    onClick={() => goToPage(currentPage - 1)}
                    disabled={currentPage === 1}
                  >
                    ← Previous
                  </button>
                  
                  <div className={styles.pageNumbers}>
                    {[...Array(totalPages)].map((_, i) => {
                      const page = i + 1
                      // Show first, last, current, and adjacent pages
                      if (
                        page === 1 || 
                        page === totalPages || 
                        (page >= currentPage - 1 && page <= currentPage + 1)
                      ) {
                        return (
                          <button
                            key={page}
                            className={`${styles.pageNum} ${currentPage === page ? styles.active : ''}`}
                            onClick={() => goToPage(page)}
                          >
                            {page}
                          </button>
                        )
                      } else if (page === currentPage - 2 || page === currentPage + 2) {
                        return <span key={page} className={styles.ellipsis}>...</span>
                      }
                      return null
                    })}
                  </div>
                  
                  <button 
                    className={styles.pageBtn}
                    onClick={() => goToPage(currentPage + 1)}
                    disabled={currentPage === totalPages}
                  >
                    Next →
                  </button>
                </div>
              )}
              </>
            )}
          </div>
        )}

        {/* COOKING MODE */}
        {mode === MODE.COOKING && selectedRecipe && (
          <div className={styles.cookingView}>
            <div className={styles.cookingHeader}>
              <button className={styles.backBtn} onClick={() => setMode(MODE.RECIPES)}>
                <ArrowLeft size={20} />
              </button>
              <div className={styles.cookingInfo}>
                <h2>{selectedRecipe.name}</h2>
                <p>{selectedRecipe.time} min · {selectedRecipe.level}</p>
              </div>
              <button
                className={`${styles.favoriteBtnLarge} ${isFavorite(selectedRecipe.id) ? styles.favorited : ''}`}
                onClick={() => toggleFavorite(selectedRecipe)}
              >
                <Heart size={24} fill={isFavorite(selectedRecipe.id) ? 'currentColor' : 'none'} />
              </button>
            </div>

            {!selectedRecipe.hasAll && (
              <div className={styles.missingAlert}>
                <h4>Missing main ingredients:</h4>
                <ul>
                  {selectedRecipe.mainIngredients
                    .filter((_, i) => !selectedRecipe.hasMain[i]?.has)
                    .map((ing, i) => <li key={i}>{ing}</li>)
                  }
                </ul>
                <p className={styles.missingNote}>
                  Optional/pantry items are usually available and not listed here
                </p>
                <button 
                  className={styles.addToCartBtn}
                  onClick={() => {
                    const missingItems = selectedRecipe.mainIngredients.filter((_, i) => !selectedRecipe.hasMain[i]?.has)
                    addMultipleToCart(missingItems)
                    alert(`Added ${missingItems.length} items to shopping cart!`)
                  }}
                >
                  <ShoppingCart size={18} />
                  Add Missing to Cart
                </button>
              </div>
            )}

            <div className={styles.ingredientsList}>
              <div className={styles.ingredientsHeader}>
                <h4>Ingredients</h4>
                <div className={styles.customizationControls}>
                  <button
                    className={styles.customizeRecipeBtn}
                    onClick={() => {
                      setShowCustomizationChat(!showCustomizationChat)
                      if (!showCustomizationChat && chatMessages.length === 0) {
                        setChatMessages([{
                          role: 'assistant',
                          content: 'Hi! Tell me what you\'d like to change:\n• Make it vegetarian\n• Swap ingredients\n• Adjust portions\n• Change cooking time'
                        }])
                      }
                    }}
                  >
                    ✨ Customize
                  </button>
                  {(customizedIngredients || customizedSteps) && (
                    <button
                      className={styles.revertBtn}
                      onClick={handleRevert}
                    >
                      ↺ Revert
                    </button>
                  )}
                </div>
              </div>
              
              <h4 className={styles.sectionLabel}>
                {customizedIngredients ? 'Ingredients (Customized)' : 'Main Ingredients'}
              </h4>
              {(customizedIngredients || selectedRecipe.mainIngredients).map((ing, i) => {
                // If using customized ingredients, show them without inventory matching
                if (customizedIngredients) {
                  return (
                    <div 
                      key={i} 
                      className={styles.ingredientItem}
                    >
                      <div className={styles.ingredientName}>
                        📝 {ing}
                      </div>
                    </div>
                  )
                }
                
                // Otherwise show original ingredients with inventory matching
                const matchInfo = selectedRecipe.hasMain?.[i]
                const hasIt = matchInfo?.has || false
                
                return (
                  <div 
                    key={i} 
                    className={`${styles.ingredientItem} ${hasIt ? styles.have : styles.need}`}
                  >
                    <div className={styles.ingredientName}>
                      {hasIt ? '✓' : '✗'} {ing}
                    </div>
                    
                    {/* Show ingredient group info */}
                    {matchInfo?.isGroup && (
                      <div className={styles.ingredientGroupInfo}>
                        {matchInfo.method === 'primary' && (
                          <span className={styles.groupPrimary}>
                            🛒 Using bottled {matchInfo.groupName?.replace(/([A-Z])/g, ' $1').toLowerCase()}
                          </span>
                        )}
                        {matchInfo.method === 'components' && (
                          <span className={styles.groupComponents}>
                            👨‍🍳 Making from scratch
                          </span>
                        )}
                      </div>
                    )}
                    
                    {/* Show substitution info */}
                    {matchInfo?.substitute && !matchInfo?.isGroup && (
                      <div className={styles.substitutionInfo}>
                        🔄 Using {matchInfo.matched} instead
                      </div>
                    )}
                    
                    {/* Show missing group info */}
                    {!hasIt && matchInfo?.groupInfo && (
                      <div className={styles.missingGroupInfo}>
                        <div className={styles.groupDescription}>
                          💡 {matchInfo.groupInfo.description}
                        </div>
                        <div className={styles.groupAlternative}>
                          💭 Or get: <strong>{matchInfo.groupInfo.alternative}</strong>
                        </div>
                      </div>
                    )}
                  </div>
                )
              })}
              
              {!customizedIngredients && selectedRecipe.optionalIngredients.length > 0 && (
                <>
                  <h4 className={`${styles.optionalHeader} ${styles.sectionLabel}`}>Optional/Pantry Items</h4>
                  {selectedRecipe.optionalIngredients.map((ing, i) => {
                    const matchInfo = selectedRecipe.hasOptional?.[i]
                    const hasIt = matchInfo?.has || false
                    
                    return (
                      <div 
                        key={i} 
                        className={`${styles.ingredientItem} ${styles.optional} ${hasIt ? styles.have : styles.need}`}
                      >
                        <div className={styles.ingredientName}>
                          {hasIt ? '✓' : '✗'} {ing}
                        </div>
                        
                        {/* Show ingredient group info for optional items too */}
                        {matchInfo?.isGroup && hasIt && (
                          <div className={styles.ingredientGroupInfo}>
                            {matchInfo.method === 'primary' && (
                              <span className={styles.groupPrimary}>
                                🛒 Using bottled {matchInfo.groupName?.replace(/([A-Z])/g, ' $1').toLowerCase()}
                              </span>
                            )}
                            {matchInfo.method === 'components' && (
                              <span className={styles.groupComponents}>
                                👨‍🍳 Making from scratch
                              </span>
                            )}
                          </div>
                        )}
                        
                        {/* Show substitution info for optional items */}
                        {matchInfo?.substitute && !matchInfo?.isGroup && hasIt && (
                          <div className={styles.substitutionInfo}>
                            🔄 Using {matchInfo.matched} instead
                          </div>
                        )}
                      </div>
                    )
                  })}
                </>
              )}
            </div>

            {/* Flavor Profile Section */}
            <div className={styles.flavorSection}>
              <h4 className={styles.sectionLabel}>
                <Palette size={16} /> Flavor Profile
              </h4>
              {loadingFlavor ? (
                <div className={styles.flavorLoading}>Analyzing flavors...</div>
              ) : flavorProfile ? (
                <div className={styles.flavorBars}>
                  {flavorProfile.dimensions?.map((dim, i) => {
                    const val = flavorProfile.normalized_vector?.[i] || 0
                    return (
                      <div key={dim} className={styles.flavorBar}>
                        <span className={styles.flavorLabel}>{dim}</span>
                        <div className={styles.flavorBarContainer}>
                          <div 
                            className={styles.flavorBarFill}
                            style={{ 
                              width: `${val * 100}%`,
                              backgroundColor: getFlavorColor(dim)
                            }}
                          />
                        </div>
                        <span className={styles.flavorValue}>{Math.round(val * 100)}%</span>
                      </div>
                    )
                  })}
                  {flavorProfile.dominant_flavors?.length > 0 && (
                    <p className={styles.flavorDescription}>
                      <strong>Taste:</strong> {flavorProfile.flavor_description}
                    </p>
                  )}
                </div>
              ) : (
                <p className={styles.flavorUnavailable}>Flavor data unavailable</p>
              )}
            </div>

            <div className={styles.stepsSection}>
              <h4>Steps - tap to check off</h4>
              <div className={styles.stepsList}>
                {(customizedSteps || selectedRecipe.steps).map((step, index) => (
                  <div 
                    key={index}
                    className={`${styles.stepItem} ${completedSteps.includes(index) ? styles.done : ''}`}
                    onClick={() => toggleStep(index)}
                  >
                    <div className={styles.stepNum}>
                      {completedSteps.includes(index) ? <Check size={18} /> : index + 1}
                    </div>
                    <p>{step}</p>
                  </div>
                ))}
              </div>
            </div>

            {completedSteps.length === (customizedSteps || selectedRecipe.steps).length && (customizedSteps || selectedRecipe.steps).length > 0 && (
              <div className={styles.doneMessage}>
                <h3>🎉 You did it!</h3>
                <p>Enjoy your meal!</p>
                <button className="btn btn-primary" onClick={goHome}>
                  Cook Something Else
                </button>
              </div>
            )}
          </div>
        )}

        {/* Floating Customization Chat */}
        {showCustomizationChat && selectedRecipe && (
          <div className={styles.floatingChatPanel}>
            <div className={styles.chatHeader}>
              <h3>✨ Customize Recipe</h3>
              <button 
                className={styles.closeChatBtn} 
                onClick={() => setShowCustomizationChat(false)}
              >
                ✕
              </button>
            </div>
            
            {/* Quick Remix Section */}
            <div className={styles.quickRemixSection}>
              <div className={styles.quickRemixHeader}>
                <span>🔄 Quick Remix</span>
                <span className={styles.remixFormula}>v_new = v - old + new</span>
              </div>
              <div className={styles.quickRemixInputs}>
                <input
                  type="text"
                  placeholder="Swap out..."
                  value={remixSwapOut}
                  onChange={(e) => setRemixSwapOut(e.target.value)}
                  list="remix-ingredients-list"
                  className={styles.remixInput}
                />
                <datalist id="remix-ingredients-list">
                  {selectedRecipe.ingredients?.map((ing, i) => {
                    const lastWord = ing.split(' ').slice(-1)[0]
                    return <option key={i} value={lastWord} />
                  })}
                </datalist>
                <span className={styles.remixArrowSmall}>→</span>
                <input
                  type="text"
                  placeholder="Swap in..."
                  value={remixSwapIn}
                  onChange={(e) => setRemixSwapIn(e.target.value)}
                  className={styles.remixInput}
                />
                <button
                  className={styles.remixApplyBtn}
                  onClick={handleQuickRemix}
                  disabled={remixLoading || !remixSwapOut.trim() || !remixSwapIn.trim()}
                >
                  {remixLoading ? '...' : '✓'}
                </button>
              </div>
            </div>
            
            <div className={styles.customizeDivider}>
              <span>or describe changes</span>
            </div>
            
            <div className={styles.chatMessages}>
              {chatMessages.map((msg, i) => (
                <div key={i} className={`${styles.chatMessage} ${styles[msg.role]}`}>
                  {msg.content}
                </div>
              ))}
              {isProcessing && (
                <div className={`${styles.chatMessage} ${styles.assistant}`}>
                  <Loader size={16} className={styles.spinner} /> Processing...
                </div>
              )}
            </div>
            <div className={styles.chatInputContainer}>
              <input
                type="text"
                placeholder="e.g., make it vegetarian"
                value={userInput}
                onChange={(e) => setUserInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault()
                    handleSendCustomization()
                  }
                }}
                disabled={isProcessing}
                className={styles.chatInput}
              />
              <button
                onClick={handleSendCustomization}
                disabled={!userInput.trim() || isProcessing}
                className={styles.sendBtn}
              >
                <Send size={18} />
              </button>
            </div>
          </div>
        )}
        
      </div>
    </div>
  )
}

export default Chef
