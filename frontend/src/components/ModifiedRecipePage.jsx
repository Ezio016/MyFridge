import { useState } from 'react'
import { ArrowLeft, Check, Heart, Loader } from 'lucide-react'
import { useFavorites } from '../hooks/useFavorites'
import styles from './ModifiedRecipePage.module.css'

/**
 * Full-page view for a modified recipe showing original vs modified ingredients/steps
 */
function ModifiedRecipePage({ 
  originalRecipe, 
  modificationRequest, 
  modifiedData, 
  onBack,
  loading = false 
}) {
  const { isFavorite, toggleFavorite } = useFavorites()
  const [completedSteps, setCompletedSteps] = useState([])

  const toggleStep = (index) => {
    setCompletedSteps(prev => 
      prev.includes(index) 
        ? prev.filter(i => i !== index)
        : [...prev, index]
    )
  }

  if (loading) {
    return (
      <div className={styles.page}>
        <div className={styles.loadingView}>
          <Loader size={48} className={styles.spinner} />
          <p>Customizing your recipe... 🍳</p>
        </div>
      </div>
    )
  }

  if (!modifiedData) {
    return (
      <div className={styles.page}>
        <div className={styles.errorView}>
          <p>Unable to load modified recipe</p>
          <button onClick={onBack} className={styles.backButton}>Go Back</button>
        </div>
      </div>
    )
  }

  // Generate modified title based on the modification
  const getModifiedTitle = () => {
    if (modifiedData.modifiedTitle) {
      return modifiedData.modifiedTitle
    }
    // Default: prepend "Modified" to original name
    return `Modified ${originalRecipe.name}`
  }

  const modifiedTitle = getModifiedTitle()

  // Track which ingredients and steps were changed
  const modifiedIngredients = modifiedData.ingredients || originalRecipe.ingredients
  const modifiedSteps = modifiedData.steps || originalRecipe.steps || originalRecipe.instructions
  const changes = modifiedData.changes || {}

  return (
    <div className={styles.page}>
      <div className={styles.container}>
        {/* Header */}
        <div className={styles.header}>
          <button className={styles.backBtn} onClick={onBack}>
            <ArrowLeft size={20} />
          </button>
          <div className={styles.headerInfo}>
            <h1>{modifiedTitle}</h1>
            <p className={styles.originalNote}>
              Based on: {originalRecipe.name}
            </p>
            <p className={styles.modificationNote}>
              📝 Modification: {modificationRequest}
            </p>
            <div className={styles.meta}>
              <span>⏱️ {modifiedData.time || originalRecipe.time} min</span>
              <span>👨‍🍳 {modifiedData.difficulty || originalRecipe.level}</span>
            </div>
          </div>
          <button
            className={`${styles.favoriteBtnLarge} ${isFavorite(originalRecipe.id) ? styles.favorited : ''}`}
            onClick={() => toggleFavorite(originalRecipe)}
          >
            <Heart size={24} fill={isFavorite(originalRecipe.id) ? 'currentColor' : 'none'} />
          </button>
        </div>

        {/* AI Response Section */}
        {modifiedData.aiResponse && (
          <div className={styles.aiResponse}>
            <h3>💡 Chef's Notes</h3>
            <p>{modifiedData.aiResponse}</p>
          </div>
        )}

        {/* Ingredients Section with Strikethrough */}
        <div className={styles.section}>
          <h2>🧺 Ingredients</h2>
          <div className={styles.ingredientsList}>
            {modifiedIngredients.map((ing, i) => {
              const change = changes.ingredients?.[i]
              const originalIng = originalRecipe.ingredients[i]
              
              return (
                <div key={i} className={styles.ingredientItem}>
                  {change?.type === 'replaced' ? (
                    <>
                      <span className={styles.strikethrough}>{originalIng}</span>
                      <span className={styles.arrow}>→</span>
                      <span className={styles.replacement}>{ing}</span>
                    </>
                  ) : change?.type === 'removed' ? (
                    <span className={styles.strikethrough}>{originalIng}</span>
                  ) : change?.type === 'added' ? (
                    <span className={styles.addition}>+ {ing}</span>
                  ) : (
                    <span>{ing}</span>
                  )}
                </div>
              )
            })}
          </div>
        </div>

        {/* Steps Section with Strikethrough */}
        <div className={styles.section}>
          <h2>👨‍🍳 Instructions</h2>
          <p className={styles.stepHint}>Tap to check off as you complete each step</p>
          <div className={styles.stepsList}>
            {modifiedSteps.map((step, index) => {
              const change = changes.steps?.[index]
              const originalStep = originalRecipe.steps?.[index] || originalRecipe.instructions?.[index]
              
              return (
                <div 
                  key={index}
                  className={`${styles.stepItem} ${completedSteps.includes(index) ? styles.done : ''}`}
                  onClick={() => toggleStep(index)}
                >
                  <div className={styles.stepNum}>
                    {completedSteps.includes(index) ? <Check size={18} /> : index + 1}
                  </div>
                  <div className={styles.stepContent}>
                    {change?.type === 'modified' ? (
                      <>
                        <p className={styles.strikethrough}>{originalStep}</p>
                        <p className={styles.replacement}>→ {step}</p>
                      </>
                    ) : change?.type === 'added' ? (
                      <p className={styles.addition}>+ {step}</p>
                    ) : (
                      <p>{step}</p>
                    )}
                  </div>
                </div>
              )
            })}
          </div>
        </div>

        {/* Done Message */}
        {completedSteps.length === modifiedSteps.length && modifiedSteps.length > 0 && (
          <div className={styles.doneMessage}>
            <h3>🎉 You did it!</h3>
            <p>Enjoy your customized meal!</p>
            <button className={styles.doneBtn} onClick={onBack}>
              Back to Recipes
            </button>
          </div>
        )}
      </div>
    </div>
  )
}

export default ModifiedRecipePage

