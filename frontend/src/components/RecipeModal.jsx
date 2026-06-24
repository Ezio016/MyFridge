import { useState } from 'react'
import { X, Clock, Heart, ChefHat, ArrowLeft, Check, Sparkles } from 'lucide-react'
import { useFavorites } from '../hooks/useFavorites'
import ChefAssistantChat from './ChefAssistantChat'
import styles from './RecipeModal.module.css'

/**
 * Shared recipe detail modal - used in Fridge recommendations & Chef page
 */
function RecipeModal({ isOpen, onClose, recipes = [], title = "Recipes", onCustomizeRecipe }) {
  const { isFavorite, toggleFavorite } = useFavorites()
  const [selectedRecipe, setSelectedRecipe] = useState(null)
  const [completedSteps, setCompletedSteps] = useState([])
  const [showCustomizePrompt, setShowCustomizePrompt] = useState(false)

  const handleClose = () => {
    setSelectedRecipe(null)
    setCompletedSteps([])
    onClose()
  }

  const handleBack = () => {
    setSelectedRecipe(null)
    setCompletedSteps([])
  }

  const toggleStep = (index) => {
    setCompletedSteps(prev => 
      prev.includes(index) 
        ? prev.filter(i => i !== index)
        : [...prev, index]
    )
  }

  if (!isOpen || recipes.length === 0) return null

  // If a recipe is selected, show full cooking view (Chef design)
  if (selectedRecipe) {
    // Categorize ingredients into main vs optional/pantry
    const PANTRY_STAPLES = ['water', 'salt', 'pepper', 'oil', 'sugar', 'flour', 'butter', 'onion', 'garlic']
    const isPantryStaple = (ing) => {
      const lower = ing.toLowerCase()
      return PANTRY_STAPLES.some(s => lower.includes(s))
    }

    const mainIngredients = selectedRecipe.ingredients.filter(ing => !isPantryStaple(ing))
    const optionalIngredients = selectedRecipe.ingredients.filter(ing => isPantryStaple(ing))

    // For demo: assume pantry items are available, main items may be missing
    const hasAll = selectedRecipe.missingAfterAdd === 0
    const hasMain = mainIngredients.map(() => hasAll) // Simplified - in real app would check inventory

    return (
      <div className={styles.overlay} onClick={handleClose}>
        <div className={`${styles.modal} ${styles.cookingView}`} onClick={(e) => e.stopPropagation()}>
          {/* Header - Chef style */}
          <div className={styles.cookingHeader}>
            <button className={styles.backBtn} onClick={handleBack}>
              <ArrowLeft size={20} />
            </button>
            <div className={styles.cookingInfo}>
              <h2>{selectedRecipe.name}</h2>
              <p>{selectedRecipe.time} min · {selectedRecipe.difficulty}</p>
            </div>
            <button
              className={`${styles.favoriteBtnLarge} ${isFavorite(selectedRecipe.id) ? styles.favorited : ''}`}
              onClick={() => toggleFavorite(selectedRecipe)}
            >
              <Heart size={24} fill={isFavorite(selectedRecipe.id) ? 'currentColor' : 'none'} />
            </button>
          </div>

          <div className={styles.cookingContent}>
            {/* Missing Alert */}
            {!hasAll && mainIngredients.length > 0 && (
              <div className={styles.missingAlert}>
                <h4>Missing main ingredients:</h4>
                <ul>
                  {mainIngredients
                    .filter((_, i) => !hasMain[i])
                    .map((ing, i) => <li key={i}>{ing}</li>)
                  }
                </ul>
                <p className={styles.missingNote}>
                  Optional/pantry items are usually available and not listed here
                </p>
              </div>
            )}

            {/* Main Ingredients */}
            {mainIngredients.length > 0 && (
              <div className={styles.ingredientsList}>
                <h4>Main Ingredients</h4>
                {mainIngredients.map((ing, i) => (
                  <div 
                    key={i} 
                    className={`${styles.ingredientItem} ${hasMain[i] ? styles.have : styles.need}`}
                  >
                    {hasMain[i] ? '✓' : '✗'} {ing}
                  </div>
                ))}
              </div>
            )}

            {/* Optional/Pantry Items */}
            {optionalIngredients.length > 0 && (
              <div className={styles.ingredientsList}>
                <h4 className={styles.optionalHeader}>Optional/Pantry Items</h4>
                {optionalIngredients.map((ing, i) => (
                  <div 
                    key={i} 
                    className={`${styles.ingredientItem} ${styles.optional}`}
                  >
                    ✓ {ing}
                  </div>
                ))}
              </div>
            )}

            {/* Steps */}
            {selectedRecipe.instructions && selectedRecipe.instructions.length > 0 && (
              <div className={styles.stepsSection}>
                <h4>Steps - tap to check off</h4>
                <div className={styles.stepsList}>
                  {selectedRecipe.instructions.map((step, index) => (
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
            )}

            {/* Customize Recipe Section */}
            <div className={styles.customizeSection}>
              <button 
                className={styles.customizeBtn}
                onClick={() => setShowCustomizePrompt(!showCustomizePrompt)}
              >
                <Sparkles size={20} />
                Customize this recipe?
              </button>
              {showCustomizePrompt && (
                <div className={styles.customizePrompt}>
                  <p>💡 Customize this recipe to your preferences!</p>
                  <p className={styles.customizeHint}>
                    Try: "Make it vegetarian", "Use chicken instead", "Reduce spice", etc.
                  </p>
                </div>
              )}
            </div>

            {/* Done Message */}
            {completedSteps.length === selectedRecipe.instructions?.length && selectedRecipe.instructions?.length > 0 && (
              <div className={styles.doneMessage}>
                <h3>🎉 You did it!</h3>
                <p>Enjoy your meal!</p>
                <button className={styles.doneBtn} onClick={handleBack}>
                  View More Recipes
                </button>
              </div>
            )}
          </div>

          {/* Recipe Customization Chat */}
          <ChefAssistantChat 
            mode="cooking"
            selectedRecipe={selectedRecipe}
            onCustomizeRecipe={onCustomizeRecipe}
          />
        </div>
      </div>
    )
  }

  return (
    <div className={styles.overlay} onClick={onClose}>
      <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
        <div className={styles.header}>
          <h2>{title}</h2>
          <button className={styles.closeBtn} onClick={onClose}>
            <X size={24} />
          </button>
        </div>

        <div className={styles.recipeList}>
          {recipes.map((recipe, i) => (
            <div 
              key={i} 
              className={styles.recipeCard}
              onClick={() => setSelectedRecipe(recipe)}
            >
              <div className={styles.recipeHeader}>
                <div className={styles.recipeInfo}>
                  <div className={styles.recipeTitleRow}>
                    <h3>{recipe.name}</h3>
                    {recipe.missingAfterAdd !== undefined && (
                      <span className={`${styles.readinessBadge} ${recipe.missingAfterAdd === 0 ? styles.ready : styles.almostReady}`}>
                        {recipe.missingAfterAdd === 0 
                          ? '✓ Ready to cook!' 
                          : `${recipe.missingAfterAdd} more needed`
                        }
                      </span>
                    )}
                  </div>
                  <div className={styles.recipeMeta}>
                    <span>
                      <Clock size={14} />
                      {recipe.time}m
                    </span>
                    <span className={styles.difficulty}>{recipe.difficulty}</span>
                    <span className={styles.ingredientCount}>
                      {recipe.ingredients.length} ingredients
                    </span>
                  </div>
                </div>
                <button
                  className={`${styles.favoriteBtn} ${isFavorite(recipe.id) ? styles.favorited : ''}`}
                  onClick={(e) => {
                    e.stopPropagation()
                    toggleFavorite(recipe)
                  }}
                >
                  <Heart size={20} fill={isFavorite(recipe.id) ? 'currentColor' : 'none'} />
                </button>
              </div>

              {recipe.description && (
                <p className={styles.description}>{recipe.description}</p>
              )}

              <div className={styles.ingredients}>
                <h4>Ingredients:</h4>
                <ul>
                  {recipe.ingredients.slice(0, 8).map((ing, j) => (
                    <li key={j}>{ing}</li>
                  ))}
                  {recipe.ingredients.length > 8 && (
                    <li className={styles.more}>
                      + {recipe.ingredients.length - 8} more
                    </li>
                  )}
                </ul>
              </div>

              {recipe.tags && recipe.tags.length > 0 && (
                <div className={styles.tags}>
                  {recipe.tags.slice(0, 4).map((tag, j) => (
                    <span key={j} className={styles.tag}>{tag}</span>
                  ))}
                </div>
              )}

              <div className={styles.viewHint}>
                Tap to view full recipe →
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default RecipeModal

