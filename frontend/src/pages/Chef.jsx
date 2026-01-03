import { useState, useEffect } from 'react'
import { ChefHat, Clock, Compass, Flame, ArrowLeft, Check, Filter } from 'lucide-react'
import { inventoryAPI, chatAPI, recipeAPI } from '../api/client'
import styles from './Chef.module.css'

const MODE = {
  HOME: 'home',
  LOADING: 'loading',
  RECIPES: 'recipes',
  COOKING: 'cooking',
}

function Chef() {
  const [mode, setMode] = useState(MODE.HOME)
  const [inventory, setInventory] = useState([])
  const [recipes, setRecipes] = useState([])
  const [allRecipes, setAllRecipes] = useState([]) // For explore mode
  const [currentPage, setCurrentPage] = useState(1)
  const [recipesPerPage] = useState(12) // Show 12 recipes per page
  const [filterExpiring, setFilterExpiring] = useState(false)
  const [selectedRecipe, setSelectedRecipe] = useState(null)
  const [completedSteps, setCompletedSteps] = useState([])
  const [loading, setLoading] = useState(false)
  const [recipeType, setRecipeType] = useState('quick') // 'quick' or 'explore'

  useEffect(() => {
    loadInventory()
  }, [])

  const loadInventory = async () => {
    try {
      const items = await inventoryAPI.getAll()
      setInventory(items)
    } catch (err) {
      console.error('Failed to load inventory:', err)
    }
  }

  const expiringItems = inventory.filter(i => i.expiry_status === 'expiring_soon')
  const expiringCount = expiringItems.length

  const loadRecipes = async (type) => {
    setRecipeType(type)
    setMode(MODE.LOADING)
    setLoading(true)
    setFilterExpiring(false)
    setCurrentPage(1) // Reset to first page

    try {
      console.log(`🍳 Loading ${type} recipes from database...`)
      
      let response
      if (type === 'lightning') {
        // Get ALL quick recipes (under 15 min) for lightning mode
        response = await recipeAPI.getQuick(15, 100) // Get up to 100 quick recipes
      } else {
        // Get ALL recipes for exploration
        response = await recipeAPI.getAll()
      }
      
      if (!response || !response.recipes || response.recipes.length === 0) {
        throw new Error('No recipes found in database')
      }
      
      console.log(`✅ Got ${response.recipes.length} recipes from database`)
      
      // Transform database recipes to match our UI format
      const formattedRecipes = response.recipes.map((r, idx) => {
        // Check which ingredients user has
        const inventoryNames = inventory.map(i => i.name.toLowerCase())
        const pantryStaples = ['salt', 'pepper', 'oil', 'olive oil', 'vegetable oil',  'butter', 'water', 'sugar', 'flour']
        
        const hasIngredient = r.ingredients.map(ing => {
          const ingLower = ing.toLowerCase()
          // Assume they have pantry staples
          if (pantryStaples.some(staple => ingLower.includes(staple))) {
            return true
          }
          // Check if in fridge
          return inventoryNames.some(inv => 
            ingLower.includes(inv) || inv.includes(ingLower.split(' ')[0])
          )
        })
        
        // Separate main vs optional ingredients
        const isOptional = r.ingredients.map(ing => {
          const ingLower = ing.toLowerCase()
          // These are optional/common ingredients people usually have
          return pantryStaples.some(staple => ingLower.includes(staple)) ||
                 ingLower.includes('salt') || ingLower.includes('pepper') ||
                 ingLower.includes('water') || ingLower.includes('oil')
        })
        
        const mainIngredients = r.ingredients.filter((_, i) => !isOptional[i])
        const optionalIngredients = r.ingredients.filter((_, i) => isOptional[i])
        
        const hasMain = mainIngredients.map(ing => {
          const ingLower = ing.toLowerCase()
          return inventoryNames.some(inv => 
            ingLower.includes(inv) || inv.includes(ingLower.split(' ')[0])
          )
        })
        
        const hasOptional = optionalIngredients.map(() => true) // Assume they have optional items
        
        const missingMainCount = hasMain.filter(h => !h).length
        const totalMainCount = mainIngredients.length
        const missingCount = hasIngredient.filter(h => !h).length
        
        const hasAtLeastOneMain = hasMain.some(h => h) // Has at least 1 main ingredient
        
        return {
          id: r.id || `recipe_${idx}`,
          name: r.name,
          time: r.total_time || r.cook_time + r.prep_time,
          level: r.difficulty || 'easy',
          usesExpiring: false, // Could enhance this later
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
          image_url: r.image_url
        }
      })
      
      // Filter and sort based on mode
      if (type === 'lightning') {
        // Lightning: Only show recipes with at least 1 main ingredient match
        const filtered = formattedRecipes.filter(r => r.hasAtLeastOneMain)
        console.log(`⚡ Lightning filtered: ${filtered.length} recipes with your ingredients`)
        setAllRecipes(filtered)
        setRecipes(filtered) // Show all filtered recipes
      } else {
        // Explore: Show ALL recipes, sorted by hasAll (green first)
        const sorted = [...formattedRecipes].sort((a, b) => {
          // Green recipes (hasAll) come first
          if (a.hasAll && !b.hasAll) return -1
          if (!a.hasAll && b.hasAll) return 1
          // Then sort by missing count (fewer missing = higher priority)
          return a.missingMainCount - b.missingMainCount
        })
        console.log(`🧭 Explore: ${sorted.length} recipes (${sorted.filter(r => r.hasAll).length} ready to cook)`)
        setAllRecipes(sorted)
        setRecipes(sorted) // Will be paginated in render
      }
      
      setMode(MODE.RECIPES)
    } catch (err) {
      console.error('❌ Chef error:', err)
      alert(`Chef Error: ${err.message || 'Something went wrong'}. Check your connection!`)
      setMode(MODE.HOME)
    } finally {
      setLoading(false)
    }
  }

  const buildPrompt = (type) => {
    const inventoryList = inventory.map(i => i.name).join(', ')
    const expiringList = expiringItems.map(i => i.name).join(', ')
    
    let prompt = `MY FRIDGE HAS: ${inventoryList || 'not much'}

`
    
    if (expiringList) {
      prompt += `EXPIRING SOON: ${expiringList}

`
    }

    if (type === 'lightning') {
      prompt += `Give me 5 SUPER FAST recipes (UNDER 5 MINUTES, no cooking required or microwave only).

Examples: toast, sandwiches, smoothies, overnight oats, wraps, salads, yogurt bowls, quick snacks.
Must include at least 2 of my main ingredients. Be creative and diverse!`
    } else {
      prompt += `Give me 5 recipes that take 15-45 minutes. More substantial meals with real cooking.

Examples: pasta dishes, stir fry, rice bowls, grilled items, soups, baked dishes, curries.
Must include at least 2 of my main ingredients. Mix of what I can make and what needs extra items. Be creative!`
    }
    
    prompt += `

FORMAT each recipe EXACTLY like this (repeat for each recipe):
---RECIPE---
NAME: Recipe Name Here
TIME: 10
LEVEL: easy
USES_EXPIRING: no
INGREDIENTS: ingredient1, ingredient2, ingredient3
STEPS:
1. First step
2. Second step
3. Third step
---END---

RULES:
- Start each recipe with ---RECIPE--- on its own line
- End each recipe with ---END--- on its own line
- TIME is just the number (no "minutes")
- LEVEL is just: easy, medium, or hard
- STEPS numbered 1-5 max, restart numbering for each recipe
- Maximum 5 ingredients per recipe`

    return prompt
  }

  const parseRecipes = (response) => {
    // Handle various formats: ---RECIPE---, ---RECIPE 1---, etc.
    const recipeBlocks = response.split(/---RECIPE[^-]*---/i).filter(b => b.includes('NAME:'))
    
    return recipeBlocks.map((block, idx) => {
      const nameMatch = block.match(/NAME:\s*(.+)/i)
      const timeMatch = block.match(/TIME:\s*(\d+)/i)
      const levelMatch = block.match(/LEVEL:\s*(\w+)/i)
      const expiringMatch = block.match(/USES_EXPIRING:\s*(\w+)/i)
      const ingredientsMatch = block.match(/INGREDIENTS:\s*(.+)/i)
      // Stop at ---END--- or next ---RECIPE or end of block
      const stepsMatch = block.match(/STEPS:\s*([\s\S]*?)(?:---END---|---RECIPE|$)/i)
      
      const ingredients = ingredientsMatch 
        ? ingredientsMatch[1].split(',').map(i => i.trim()).filter(Boolean)
        : []
      
      const steps = stepsMatch
        ? stepsMatch[1].split(/\d+\.\s*/).filter(s => s.trim()).map(s => s.trim())
        : []

      // Check which ingredients we have (stricter matching)
      const inventoryNames = inventory.map(i => i.name.toLowerCase().trim())
      
      // Common pantry staples that everyone has - don't count as missing
      const pantryStaples = ['salt', 'pepper', 'oil', 'olive oil', 'vegetable oil', 'cooking oil', 
        'water', 'butter', 'sugar', 'flour', 'garlic', 'onion', 'soy sauce', 'vinegar']
      
      const hasIngredient = ingredients.map(ing => {
        const ingLower = ing.toLowerCase().trim()
        
        // Skip pantry staples - assume they have them
        if (pantryStaples.some(staple => ingLower.includes(staple) || staple.includes(ingLower))) {
          return true
        }
        
        // Check for exact match or close match (word boundaries)
        return inventoryNames.some(inv => {
          // Exact match
          if (inv === ingLower) return true
          // Ingredient contains inventory item as whole word (e.g., "chicken" in "chicken breast")
          const invWords = inv.split(/\s+/)
          const ingWords = ingLower.split(/\s+/)
          // Check if any main word matches
          return invWords.some(w => ingWords.includes(w) && w.length > 2) ||
                 ingWords.some(w => invWords.includes(w) && w.length > 2)
        })
      })
      
      const missingCount = hasIngredient.filter(h => !h).length
      const usesExpiring = expiringMatch ? expiringMatch[1].toLowerCase() === 'yes' : false

      return {
        id: idx,
        name: nameMatch ? nameMatch[1].trim() : `Recipe ${idx + 1}`,
        time: timeMatch ? parseInt(timeMatch[1]) : 20,
        level: levelMatch ? levelMatch[1].toLowerCase() : 'easy',
        usesExpiring,
        ingredients,
        hasIngredient,
        missingCount,
        hasAll: missingCount === 0,
        steps,
      }
    })
  }

  const filteredRecipes = filterExpiring 
    ? recipes.filter(r => r.usesExpiring)
    : recipes

  // Pagination logic (only for explore mode)
  const totalRecipes = filteredRecipes.length
  const totalPages = Math.ceil(totalRecipes / recipesPerPage)
  const startIndex = (currentPage - 1) * recipesPerPage
  const endIndex = startIndex + recipesPerPage
  const paginatedRecipes = recipeType === 'explore' 
    ? filteredRecipes.slice(startIndex, endIndex)
    : filteredRecipes // Lightning shows all (already filtered)

  const goToPage = (page) => {
    setCurrentPage(page)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  const selectRecipe = (recipe) => {
    setSelectedRecipe(recipe)
    setCompletedSteps([])
    setMode(MODE.COOKING)
  }

  const toggleStep = (index) => {
    setCompletedSteps(prev => 
      prev.includes(index) 
        ? prev.filter(i => i !== index)
        : [...prev, index]
    )
  }

  const goHome = () => {
    setMode(MODE.HOME)
    setRecipes([])
    setAllRecipes([])
    setCurrentPage(1)
    setSelectedRecipe(null)
    setCompletedSteps([])
    setFilterExpiring(false)
  }

  return (
    <div className={styles.page}>
      <div className="container">
        
        {/* HOME - Two Buttons */}
        {mode === MODE.HOME && (
          <div className={styles.homeView}>
            <div className={styles.chefAvatar}>
              <div className={styles.avatarCircle}>
                <ChefHat size={48} />
              </div>
              <p className={styles.greeting}>What are we cooking?</p>
            </div>
            
            <div className={styles.mainButtons}>
              <button 
                className={styles.bigBtn}
                onClick={() => loadRecipes('lightning')}
              >
                <Flame size={32} />
                <span>Lightning</span>
                <small>Under 5 min</small>
              </button>
              
              <button 
                className={styles.bigBtn}
                onClick={() => loadRecipes('explore')}
              >
                <Compass size={32} />
                <span>Explore</span>
                <small>15+ min</small>
              </button>
            </div>
          </div>
        )}

        {/* LOADING */}
        {mode === MODE.LOADING && (
          <div className={styles.loadingView}>
            <div className={styles.avatarCircle + ' ' + styles.cooking}>
              <ChefHat size={48} />
            </div>
            <p>Chef is finding recipes... 🍳</p>
          </div>
        )}

        {/* RECIPES GRID */}
        {mode === MODE.RECIPES && (
          <div className={styles.recipesView}>
            <div className={styles.recipesHeader}>
              <button className={styles.backBtn} onClick={goHome}>
                <ArrowLeft size={20} />
              </button>
              <h2>{recipeType === 'lightning' ? '⚡ Lightning' : '🍳 Explore'}</h2>
              
              <button 
                className={`${styles.filterBtn} ${filterExpiring ? styles.active : ''}`}
                onClick={() => setFilterExpiring(!filterExpiring)}
                disabled={expiringCount === 0}
              >
                <Filter size={18} />
                <span>Expiring</span>
                {expiringCount > 0 && <span className={styles.badge}>{expiringCount}</span>}
              </button>
            </div>

            {filteredRecipes.length === 0 ? (
              <div className={styles.noRecipes}>
                <p>{recipeType === 'lightning' ? 'No recipes with your ingredients. Try adding items to your fridge!' : 'No recipes match the filter'}</p>
                <button onClick={() => setFilterExpiring(false)}>Show all</button>
              </div>
            ) : (
              <>
                <div className={styles.recipeCount}>
                  {recipeType === 'lightning' ? (
                    <p>⚡ {filteredRecipes.length} quick recipes with your ingredients</p>
                  ) : (
                    <p>🧭 Showing {startIndex + 1}-{Math.min(endIndex, totalRecipes)} of {totalRecipes} recipes</p>
                  )}
                </div>
                <div className={styles.recipesGrid}>
                  {paginatedRecipes.map((recipe) => (
                  <div 
                    key={recipe.id}
                    className={`${styles.recipeCard} ${recipe.hasAll ? styles.hasAll : styles.missing}`}
                    onClick={() => selectRecipe(recipe)}
                  >
                    <div className={styles.cardTop}>
                      <span className={styles.time}>
                        <Clock size={14} />
                        {recipe.time}m
                      </span>
                      <span className={styles.level}>{recipe.level}</span>
                    </div>
                    
                    <h3>{recipe.name}</h3>
                    
                    <div className={styles.cardBottom}>
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
              
              {/* Pagination for Explore mode */}
              {recipeType === 'explore' && totalPages > 1 && (
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
              <div>
                <h2>{selectedRecipe.name}</h2>
                <p>{selectedRecipe.time} min · {selectedRecipe.level}</p>
              </div>
            </div>

            {!selectedRecipe.hasAll && (
              <div className={styles.missingAlert}>
                <h4>Missing main ingredients:</h4>
                <ul>
                  {selectedRecipe.mainIngredients
                    .filter((_, i) => !selectedRecipe.hasMain[i])
                    .map((ing, i) => <li key={i}>{ing}</li>)
                  }
                </ul>
                <p className={styles.missingNote}>
                  Optional/pantry items are usually available and not listed here
                </p>
              </div>
            )}

            <div className={styles.ingredientsList}>
              <h4>Main Ingredients</h4>
              {selectedRecipe.mainIngredients.map((ing, i) => (
                <div 
                  key={i} 
                  className={`${styles.ingredientItem} ${selectedRecipe.hasMain[i] ? styles.have : styles.need}`}
                >
                  {selectedRecipe.hasMain[i] ? '✓' : '✗'} {ing}
                </div>
              ))}
              
              {selectedRecipe.optionalIngredients.length > 0 && (
                <>
                  <h4 className={styles.optionalHeader}>Optional/Pantry Items</h4>
                  {selectedRecipe.optionalIngredients.map((ing, i) => (
                    <div 
                      key={i} 
                      className={`${styles.ingredientItem} ${styles.optional}`}
                    >
                      ✓ {ing}
                    </div>
                  ))}
                </>
              )}
            </div>

            <div className={styles.stepsSection}>
              <h4>Steps - tap to check off</h4>
              <div className={styles.stepsList}>
                {selectedRecipe.steps.map((step, index) => (
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

            {completedSteps.length === selectedRecipe.steps.length && selectedRecipe.steps.length > 0 && (
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
        
      </div>
    </div>
  )
}

export default Chef
