import { useState, useEffect } from 'react'
import { Plus, Refrigerator, AlertTriangle, Sparkles, ShoppingCart, Search, X } from 'lucide-react'
import { inventoryAPI, recipeAPI } from '../api/client'
import InventoryList from '../components/InventoryList'
import AddItemForm from '../components/AddItemForm'
import RecipeModal from '../components/RecipeModal'
import { addToCart } from '../utils/cartUtils'
import styles from './Fridge.module.css'

function Fridge() {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [showForm, setShowForm] = useState(false)
  const [editingItem, setEditingItem] = useState(null)
  const [categoryFilter, setCategoryFilter] = useState('all')
  const [searchQuery, setSearchQuery] = useState('')
  const [recommendations, setRecommendations] = useState([])
  const [allRecommendations, setAllRecommendations] = useState([]) // Store all recommendations
  const [recPage, setRecPage] = useState(0) // Which set of recommendations to show
  const [loadingRecs, setLoadingRecs] = useState(false)
  const [selectedRecIngredient, setSelectedRecIngredient] = useState(null)
  const [showRecommendations, setShowRecommendations] = useState(false)

  const fetchItems = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await inventoryAPI.getAll()
      setItems(data)
    } catch (err) {
      setError('Cannot connect to server')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchItems()
    // Don't calculate recommendations yet - wait for items to load
  }, [])

  useEffect(() => {
    if (items.length > 0) {
      calculateRecommendations()
    }
  }, [items])

  const calculateRecommendations = async () => {
    setLoadingRecs(true)
    try {
      const response = await recipeAPI.getAll()
      const allRecipes = response.recipes || []
      
      // Get current inventory names (lowercase for matching)
      const currentIngredients = items.map(i => i.name.toLowerCase())
      console.log('🧊 Smart Shopping - Current inventory:', currentIngredients)
      
      // Comprehensive staple categorization
      const CORE_STAPLES = ['egg', 'flour', 'butter', 'milk', 'oil', 'salt', 'sugar', 'rice', 'pasta']
      const PROTEIN_STAPLES = ['chicken', 'beef', 'pork', 'fish', 'tofu', 'beans', 'lentils']
      const VEGETABLE_STAPLES = ['tomato', 'potato', 'onion', 'garlic', 'carrot', 'bell pepper', 'celery']
      const CONDIMENT_STAPLES = ['soy sauce', 'vinegar', 'ketchup', 'mustard', 'mayonnaise']
      const SPICE_STAPLES = ['pepper', 'paprika', 'cumin', 'oregano', 'basil', 'cinnamon']
      const DAIRY_STAPLES = ['cheese', 'yogurt', 'cream']
      const GRAIN_STAPLES = ['bread', 'tortilla', 'noodles']
      
      // Specialty items that are alternatives or niche (NOT staples)
      const SPECIALTY_ITEMS = [
        'daikon', 'bok choy', 'napa cabbage', 'chinese cabbage',
        'mirin', 'sake', 'fish sauce', 'oyster sauce',
        'gochujang', 'miso', 'tahini', 'harissa',
        'star anise', 'sichuan pepper', 'cardamom', 'saffron',
        'truffle', 'caviar', 'foie gras',
        'quinoa', 'bulgur', 'farro', 'couscous',
        'kale', 'arugula', 'radicchio', 'endive'
      ]
      
      const isStaple = (ing) => {
        const lower = ing.toLowerCase()
        return [
          ...CORE_STAPLES, ...PROTEIN_STAPLES, ...VEGETABLE_STAPLES,
          ...CONDIMENT_STAPLES, ...SPICE_STAPLES, ...DAIRY_STAPLES, ...GRAIN_STAPLES
        ].some(s => lower.includes(s))
      }
      
      const isSpecialty = (ing) => {
        const lower = ing.toLowerCase()
        return SPECIALTY_ITEMS.some(s => lower.includes(s))
      }
      
      const isCoreStaple = (ing) => {
        const lower = ing.toLowerCase()
        return CORE_STAPLES.some(s => lower.includes(s))
      }
      
      // Helper: Smart ingredient matching
      const hasIngredient = (ing) => {
        const ingLower = ing.toLowerCase()
        return currentIngredients.some(curr => {
          const currLower = curr.toLowerCase()
          
          // Direct substring match (handles "eggs" in "2 large eggs")
          if (ingLower.includes(currLower) || currLower.includes(ingLower)) {
            return true
          }
          
          // Word-by-word matching for singular/plural (egg vs eggs)
          const ingWords = ingLower.split(/\s+/)
          const currWords = currLower.split(/\s+/)
          
          for (const ingWord of ingWords) {
            for (const currWord of currWords) {
              // Skip very short words (numbers, prepositions)
              if (ingWord.length < 3 || currWord.length < 3) continue
              
              // Check if words match or are very similar (singular/plural)
              if (ingWord === currWord || 
                  ingWord.startsWith(currWord) || 
                  currWord.startsWith(ingWord) ||
                  ingWord + 's' === currWord ||
                  currWord + 's' === ingWord) {
                return true
              }
            }
          }
          
          return false
        })
      }
      
      // Helper: Extract clean ingredient name from recipe text
      const extractIngredientName = (ingredientText) => {
        let cleaned = ingredientText.toLowerCase().trim()
        
        // Remove ALL leading numbers, fractions, and measurements (more aggressive)
        // Handles: "4 cup", "1/2 cup", "2.5 tablespoons", "1 1/2 cups"
        cleaned = cleaned.replace(/^[\d\s\/\.\-]+/g, '') // Remove numbers, spaces, fractions at start
        cleaned = cleaned.replace(/^(a |an |the )/g, '') // "a pinch" -> "pinch"
        cleaned = cleaned.replace(/\(.*?\)/g, '') // Remove parentheses
        
        // Remove measurement units (more comprehensive)
        const units = [
          'tablespoon', 'tablespoons', 'tbsp', 'tbs',
          'teaspoon', 'teaspoons', 'tsp',
          'cup', 'cups', 'c',
          'ml', 'milliliter', 'milliliters', 'millilitre', 'millilitres',
          'l', 'liter', 'liters', 'litre', 'litres',
          'oz', 'ounce', 'ounces',
          'lb', 'lbs', 'pound', 'pounds',
          'g', 'gram', 'grams',
          'kg', 'kilogram', 'kilograms',
          'pinch', 'dash', 'can', 'jar', 'package', 'box', 'bottle', 'piece', 'pieces',
          'clove', 'cloves', 'slice', 'slices', 'sprig', 'sprigs'
        ]
        
        // Try to match and remove units at the beginning
        for (const unit of units) {
          // Match unit at start (case insensitive, with optional 's', followed by space)
          const regex = new RegExp(`^${unit}s?\\s+`, 'i')
          cleaned = cleaned.replace(regex, '')
        }
        
        // Remove descriptive phrases (to, for, as, with, etc.)
        cleaned = cleaned.replace(/\s+(to|for|as|with|on|in|of)\s+.*/g, '')
        cleaned = cleaned.replace(/,.*$/g, '') // Remove everything after comma
        
        // Normalize oils to just "oil"
        if (cleaned.includes('oil')) {
          cleaned = cleaned.replace(/(sunflower|olive|vegetable|canola|coconut|sesame|peanut|avocado)\s+oil/g, 'oil')
          // Also catch "oil" by itself
          if (cleaned === 'oil') {
            cleaned = 'oil'
          }
        }
        
        // Normalize vinegars
        if (cleaned.includes('vinegar')) {
          cleaned = cleaned.replace(/(white|red|balsamic|apple cider|rice)\s+vinegar/g, 'vinegar')
        }
        
        // Final cleanup: remove any remaining leading/trailing spaces and numbers
        cleaned = cleaned.trim()
        cleaned = cleaned.replace(/^[\d\s\/\.\-]+/, '') // One more pass to catch stragglers
        cleaned = cleaned.trim()
        
        // Capitalize first letter
        if (cleaned.length > 0) {
          return cleaned.charAt(0).toUpperCase() + cleaned.slice(1)
        }
        
        return ingredientText // Fallback to original if cleaning failed
      }
      
      // For each recipe, calculate how "ready" it is (how many ingredients missing)
      const recipeReadiness = allRecipes.map(recipe => {
        const recipeIngredients = (recipe.ingredients || []).map(ing => ing.toLowerCase())
        const missing = recipeIngredients.filter(ing => !hasIngredient(ing))
        const missingCount = missing.length
        const totalCount = recipeIngredients.length
        
        return {
          recipe,
          missing,
          missingCount,
          totalCount,
          readiness: 1 - (missingCount / totalCount) // 0 = not ready, 1 = fully ready
        }
      })
      
      // Count impact of each missing ingredient
      const ingredientImpact = {}
      
      console.log('📊 Smart Shopping - Sample recipe analysis:')
      recipeReadiness.slice(0, 3).forEach(({ recipe, missing, missingCount }) => {
        console.log(`  ${recipe.name}: ${missingCount} missing out of ${recipe.ingredients?.length || 0}`)
        if (missing.length > 0) {
          console.log(`    Missing: ${missing.slice(0, 3).join(', ')}${missing.length > 3 ? '...' : ''}`)
        }
      })
      
      recipeReadiness.forEach(({ recipe, missing, missingCount, readiness }) => {
        // Only consider recipes that are "close" (missing 1-3 ingredients)
        if (missingCount === 0 || missingCount > 3) return
        
        missing.forEach(missingIng => {
          // Extract clean ingredient name
          const cleanName = extractIngredientName(missingIng)
          
          // Debug: log first few extractions
          if (Object.keys(ingredientImpact).length < 5) {
            console.log(`  📝 Extracted: "${missingIng}" → "${cleanName}"`)
          }
          
          // Use clean name as key to group similar ingredients
          if (!ingredientImpact[cleanName]) {
            const staple = isStaple(cleanName)
            const specialty = isSpecialty(cleanName)
            const core = isCoreStaple(cleanName)
            
            // Determine tier
            let tier = 'specialty' // Default
            if (core) tier = 'core_staple'
            else if (staple) tier = 'staple'
            else if (!specialty) tier = 'common'
            
            ingredientImpact[cleanName] = {
              totalUnlocks: 0,
              readyToMakeCount: 0,
              almostReadyCount: 0,
              recipes: [],
              isStaple: staple,
              isSpecialty: specialty,
              isCoreStaple: core,
              tier: tier
            }
          }
          
          const data = ingredientImpact[cleanName]
          data.totalUnlocks++
          
          // Track breakdown by distance
          if (!data.breakdown) {
            data.breakdown = { oneAway: 0, twoAway: 0, threeAway: 0 }
          }
          
          // HIGH PRIORITY: If adding this ingredient makes recipe READY (was only missing this 1 item)
          if (missingCount === 1) {
            data.readyToMakeCount++
            data.breakdown.oneAway++
          }
          // MEDIUM PRIORITY: If adding this brings recipe to "1 away" (was missing 2)
          else if (missingCount === 2) {
            data.almostReadyCount++
            data.breakdown.twoAway++
          }
          // LOW PRIORITY: If adding this brings recipe to "2 away" (was missing 3)
          else if (missingCount === 3) {
            data.breakdown.threeAway++
          }
          
          data.recipes.push({
            name: recipe.name,
            id: recipe.id,
            time: recipe.total_time || recipe.cook_time + recipe.prep_time,
            ingredients: recipe.ingredients,
            instructions: recipe.instructions,
            difficulty: recipe.difficulty || 'easy',
            description: recipe.description,
            tags: recipe.tags || [],
            popularity_score: recipe.popularity_score || 0,
            missingAfterAdd: missingCount - 1 // How many ingredients missing AFTER adding this one
          })
        })
      })
      
      console.log('🔍 Smart Shopping - Top missing ingredients:', 
        Object.keys(ingredientImpact).slice(0, 10).join(', '))
      
      // Sort with tiered priority system
      const sortedRecommendations = Object.entries(ingredientImpact)
        .sort((a, b) => {
          const [ingA, dataA] = a
          const [ingB, dataB] = b
          
          // Tier priority: core_staple > staple > common > specialty
          const tierPriority = { core_staple: 4, staple: 3, common: 2, specialty: 1 }
          const tierA = tierPriority[dataA.tier] || 0
          const tierB = tierPriority[dataB.tier] || 0
          
          // For staples: prioritize volume (total unlocks) over immediacy
          if (dataA.tier !== 'specialty' && dataB.tier !== 'specialty') {
            // 1. Core staples always win
            if (tierA !== tierB) return tierB - tierA
            
            // 2. For staples, prioritize by total volume of dishes unlocked
            if (dataA.totalUnlocks !== dataB.totalUnlocks) {
              return dataB.totalUnlocks - dataA.totalUnlocks
            }
            
            // 3. Then by immediate readiness
            if (dataA.readyToMakeCount !== dataB.readyToMakeCount) {
              return dataB.readyToMakeCount - dataA.readyToMakeCount
            }
          }
          
          // For specialty items: only show if they immediately complete recipes
          if (dataA.tier === 'specialty' || dataB.tier === 'specialty') {
            // Prioritize non-specialty over specialty
            if (tierA !== tierB) return tierB - tierA
            
            // For specialty, prioritize immediate completion
            if (dataA.readyToMakeCount !== dataB.readyToMakeCount) {
              return dataB.readyToMakeCount - dataA.readyToMakeCount
            }
          }
          
          // Final tiebreaker: total unlocks
          return dataB.totalUnlocks - dataA.totalUnlocks
        })
      
      // Separate into tiers
      const coreStapleRecs = sortedRecommendations
        .filter(([_, data]) => data.tier === 'core_staple')
        .slice(0, 3)
      const stapleRecs = sortedRecommendations
        .filter(([_, data]) => data.tier === 'staple')
        .slice(0, 5)
      const specialtyRecs = sortedRecommendations
        .filter(([_, data]) => data.tier === 'specialty' && data.readyToMakeCount > 0)
        .slice(0, 3)
      
      // Create multiple pages of recommendations
      const page1 = [...coreStapleRecs, ...stapleRecs].slice(0, 5) // Essentials
      const page2 = [...stapleRecs.slice(3), ...sortedRecommendations.filter(([_, d]) => d.tier === 'common')].slice(0, 5) // More staples
      const page3 = specialtyRecs.length > 0 ? specialtyRecs.slice(0, 5) : sortedRecommendations.slice(5, 10) // Specialty/alternatives
      
      const allPages = [page1, page2, page3].filter(p => p.length > 0)
      
      setAllRecommendations(allPages)
      setRecPage(0) // Start with first page
      
      // Format current page for display
      const formatRecs = (pageItems) => pageItems.map(([ingredient, data]) => ({
          ingredient,
          unlocks: data.totalUnlocks,
          readyToMake: data.readyToMakeCount,
          almostReady: data.almostReadyCount,
          isStaple: data.isStaple,
          isSpecialty: data.isSpecialty,
          isCoreStaple: data.isCoreStaple,
          tier: data.tier,
          breakdown: data.breakdown || { oneAway: 0, twoAway: 0, threeAway: 0 },
          recipes: data.recipes
            .sort((a, b) => {
              if (a.missingAfterAdd !== b.missingAfterAdd) {
                return a.missingAfterAdd - b.missingAfterAdd
              }
              if (a.ingredients.length !== b.ingredients.length) {
                return a.ingredients.length - b.ingredients.length
              }
              return (b.popularity_score || 0) - (a.popularity_score || 0)
            })
        }))
      
      setRecommendations(formatRecs(allPages[0] || []))
    } catch (err) {
      console.error('Failed to calculate recommendations:', err)
    } finally {
      setLoadingRecs(false)
    }
  }

  const handleAddItem = async (itemData) => {
    const newItem = await inventoryAPI.create(itemData)
    setItems(prev => [newItem, ...prev])
  }

  const handleEditItem = async (itemData, itemId) => {
    const updatedItem = await inventoryAPI.update(itemId, itemData)
    setItems(prev => prev.map(item => 
      item.id === itemId ? updatedItem : item
    ))
  }

  const handleSaveItem = async (itemData, itemId) => {
    if (itemId) {
      await handleEditItem(itemData, itemId)
    } else {
      await handleAddItem(itemData)
    }
  }

  const handleDeleteItem = async (id) => {
    await inventoryAPI.delete(id)
    setItems(prev => prev.filter(item => item.id !== id))
  }

  const openAddForm = () => {
    setEditingItem(null)
    setShowForm(true)
  }

  const openEditForm = (item) => {
    setEditingItem(item)
    setShowForm(true)
  }

  const closeForm = () => {
    setShowForm(false)
    setEditingItem(null)
  }

  // Count items by status
  const expiringCount = items.filter(i => i.expiry_status === 'expiring_soon').length
  const expiredCount = items.filter(i => i.expiry_status === 'expired').length

  // Filter items by category and search query
  const filteredItems = items.filter(item => {
    // Category filter
    const categoryMatch = categoryFilter === 'all' || item.category === categoryFilter
    
    // Search filter
    const searchMatch = searchQuery === '' || 
      item.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.category.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.location.toLowerCase().includes(searchQuery.toLowerCase())
    
    return categoryMatch && searchMatch
  })

  return (
    <div className={styles.page}>
      <div className="container">
        <header className={styles.header}>
          <div className={styles.iconWrap}>
            <Refrigerator size={28} />
          </div>
          <div>
            <h1>My Fridge</h1>
            <p>
              {items.length} items
              {expiringCount > 0 && <span className={styles.warning}> · {expiringCount} expiring</span>}
              {expiredCount > 0 && <span className={styles.danger}> · {expiredCount} expired</span>}
            </p>
          </div>
        </header>

        {error && (
          <div className={styles.errorBanner}>
            <AlertTriangle size={18} />
            <span>{error}</span>
          </div>
        )}

        {/* Ingredient Recommendations - Collapsible */}
        {recommendations.length > 0 && (
          <div className={styles.recommendations}>
            <button 
              className={styles.recToggle}
              onClick={() => setShowRecommendations(!showRecommendations)}
            >
              <div className={styles.recToggleLeft}>
                <Sparkles size={20} />
                <span>Smart Shopping</span>
                <span className={styles.recCount}>
                  {recommendations.length} suggestions
                  {allRecommendations.length > 1 && (
                    <span style={{ opacity: 0.7, marginLeft: '4px' }}>
                      · Page {recPage + 1}/{allRecommendations.length}
                    </span>
                  )}
                </span>
              </div>
              <span className={styles.recToggleIcon}>
                {showRecommendations ? '▼' : '▶'}
              </span>
            </button>

            {showRecommendations && (
              <>
                {allRecommendations.length > 1 && (
                  <div className={styles.recPagination}>
                    <button
                      className={styles.recPageBtn}
                      onClick={() => {
                        const newPage = (recPage - 1 + allRecommendations.length) % allRecommendations.length
                        setRecPage(newPage)
                        const formatRecs = (pageItems) => pageItems.map(([ingredient, data]) => ({
                          ingredient,
                          unlocks: data.totalUnlocks,
                          readyToMake: data.readyToMakeCount,
                          almostReady: data.almostReadyCount,
                          isStaple: data.isStaple,
                          isSpecialty: data.isSpecialty,
                          isCoreStaple: data.isCoreStaple,
                          tier: data.tier,
                          breakdown: data.breakdown || { oneAway: 0, twoAway: 0, threeAway: 0 },
                          recipes: data.recipes.sort((a, b) => {
                            if (a.missingAfterAdd !== b.missingAfterAdd) return a.missingAfterAdd - b.missingAfterAdd
                            if (a.ingredients.length !== b.ingredients.length) return a.ingredients.length - b.ingredients.length
                            return (b.popularity_score || 0) - (a.popularity_score || 0)
                          })
                        }))
                        setRecommendations(formatRecs(allRecommendations[newPage]))
                      }}
                      disabled={allRecommendations.length <= 1}
                    >
                      ← Previous
                    </button>
                    <span className={styles.recPageInfo}>
                      {recPage === 0 && '🌟 Essential Staples'}
                      {recPage === 1 && '🥘 More Staples & Common Items'}
                      {recPage === 2 && '✨ Specialty & Alternatives'}
                    </span>
                    <button
                      className={styles.recPageBtn}
                      onClick={() => {
                        const newPage = (recPage + 1) % allRecommendations.length
                        setRecPage(newPage)
                        const formatRecs = (pageItems) => pageItems.map(([ingredient, data]) => ({
                          ingredient,
                          unlocks: data.totalUnlocks,
                          readyToMake: data.readyToMakeCount,
                          almostReady: data.almostReadyCount,
                          isStaple: data.isStaple,
                          isSpecialty: data.isSpecialty,
                          isCoreStaple: data.isCoreStaple,
                          tier: data.tier,
                          breakdown: data.breakdown || { oneAway: 0, twoAway: 0, threeAway: 0 },
                          recipes: data.recipes.sort((a, b) => {
                            if (a.missingAfterAdd !== b.missingAfterAdd) return a.missingAfterAdd - b.missingAfterAdd
                            if (a.ingredients.length !== b.ingredients.length) return a.ingredients.length - b.ingredients.length
                            return (b.popularity_score || 0) - (a.popularity_score || 0)
                          })
                        }))
                        setRecommendations(formatRecs(allRecommendations[newPage]))
                      }}
                      disabled={allRecommendations.length <= 1}
                    >
                      Next →
                    </button>
                  </div>
                )}
                <div className={styles.recList}>
                {recommendations.map((rec, i) => (
                  <div
                    key={i}
                    className={styles.recItem}
                  >
                    <button
                      className={styles.recItemContent}
                      onClick={() => setSelectedRecIngredient(rec)}
                    >
                      <div className={styles.recInfo}>
                        <strong>
                          {rec.ingredient}
                          {rec.isCoreStaple && <span className={styles.coreTag}>🌟 Essential</span>}
                          {rec.isStaple && !rec.isCoreStaple && <span className={styles.stapleTag}>⭐ Staple</span>}
                          {rec.isSpecialty && <span className={styles.specialtyTag}>✨ Specialty</span>}
                        </strong>
                      </div>
                      <div className={styles.recBreakdown}>
                        <span className={styles.volumeInfo}>
                          Unlocks <strong>{rec.unlocks} {rec.unlocks === 1 ? 'recipe' : 'recipes'}</strong>
                        </span>
                      </div>
                      <div className={styles.recBreakdown}>
                        {rec.breakdown.oneAway > 0 && (
                          <span className={styles.breakdownItem}>
                            {rec.breakdown.oneAway === 1 
                              ? <><strong>1 recipe</strong> is 1 ingredient away</>
                              : <><strong>{rec.breakdown.oneAway} recipes</strong> are 1 ingredient away</>
                            }
                          </span>
                        )}
                        {rec.breakdown.twoAway > 0 && (
                          <span className={styles.breakdownItem}>
                            {rec.breakdown.twoAway === 1 
                              ? <><strong>1 recipe</strong> is 2 ingredients away</>
                              : <><strong>{rec.breakdown.twoAway} recipes</strong> are 2 ingredients away</>
                            }
                          </span>
                        )}
                        {rec.breakdown.threeAway > 0 && (
                          <span className={styles.breakdownItem}>
                            {rec.breakdown.threeAway === 1 
                              ? <><strong>1 recipe</strong> is 3 ingredients away</>
                              : <><strong>{rec.breakdown.threeAway} recipes</strong> are 3 ingredients away</>
                            }
                          </span>
                        )}
                      </div>
                      <span className={styles.viewBtn}>View all →</span>
                    </button>
                    <button 
                      className={styles.addToCartBtn}
                      onClick={(e) => {
                        e.stopPropagation();
                        addToCart(rec.ingredient, 1);
                        // Show brief confirmation
                        const btn = e.currentTarget;
                        btn.style.background = 'var(--fresh)';
                        setTimeout(() => {
                          btn.style.background = '';
                        }, 500);
                      }}
                      title="Add to shopping cart"
                    >
                      <ShoppingCart size={18} />
                    </button>
                  </div>
                ))}
                </div>
              </>
            )}
          </div>
        )}

        <div className={styles.controls}>
          {/* Search Bar */}
          <div className={styles.searchWrapper}>
            <Search size={18} className={styles.searchIcon} />
            <input
              type="text"
              className={styles.searchInput}
              placeholder="Search items..."
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

          <button 
            className={styles.addButton}
            onClick={openAddForm}
          >
            <Plus size={20} />
            <span>Add Item</span>
          </button>

          <select 
            className={styles.categoryFilter}
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
          >
            <option value="all">All Categories</option>
            <option value="dairy">🥛 Dairy</option>
            <option value="meat">🥩 Meat</option>
            <option value="seafood">🐟 Seafood</option>
            <option value="vegetable">🥬 Vegetable</option>
            <option value="fruit">🍎 Fruit</option>
            <option value="grain">🌾 Grain</option>
            <option value="beverage">🥤 Beverage</option>
            <option value="condiment">🧂 Condiment</option>
            <option value="snack">🍪 Snack</option>
            <option value="leftover">🍱 Leftover</option>
            <option value="other">📦 Other</option>
          </select>
        </div>

        <InventoryList 
          items={filteredItems} 
          onDelete={handleDeleteItem}
          onEdit={openEditForm}
          loading={loading}
        />
      </div>

      {showForm && (
        <AddItemForm 
          onSubmit={handleSaveItem}
          onClose={closeForm}
          editItem={editingItem}
        />
      )}

      {/* Recipe Modal for ingredient recommendations */}
      <RecipeModal
        isOpen={!!selectedRecIngredient}
        onClose={() => setSelectedRecIngredient(null)}
        recipes={selectedRecIngredient?.recipes || []}
        title={
          selectedRecIngredient
            ? `${selectedRecIngredient.ingredient} · ${selectedRecIngredient.recipes.length} Recipes`
            : "Recipes"
        }
      />
    </div>
  )
}

export default Fridge
