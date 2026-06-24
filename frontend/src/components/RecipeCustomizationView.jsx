import { useState, useEffect } from 'react'
import { ArrowLeft, Save, Loader, Send, X } from 'lucide-react'
import { chatAPI } from '../api/client'
import styles from './RecipeCustomizationView.module.css'

/**
 * Recipe Customization View
 * - Editable title
 * - AI chat interface for modifications
 * - Preview modified recipe
 * - Save as new recipe
 */
function RecipeCustomizationView({ recipe, onBack, onSaveNewRecipe }) {
  const [customTitle, setCustomTitle] = useState(recipe.name)
  const [chatMessages, setChatMessages] = useState([
    {
      role: 'assistant',
      content: `Hi! I'm here to help you customize "${recipe.name}". What would you like to change?\n\nYou can ask me to:\n• Make it vegetarian or vegan\n• Swap ingredients (e.g., "use chicken instead of beef")\n• Adjust cooking time\n• Change spice level\n• Remove allergens\n• Add more vegetables\n\nWhat would you like to do?`
    }
  ])
  const [userInput, setUserInput] = useState('')
  const [isProcessing, setIsProcessing] = useState(false)
  const [modifiedRecipe, setModifiedRecipe] = useState(null)
  const [isSaving, setIsSaving] = useState(false)

  const handleSendMessage = async () => {
    if (!userInput.trim() || isProcessing) return

    const userMessage = userInput.trim()
    setUserInput('')
    
    // Add user message to chat
    setChatMessages(prev => [...prev, { role: 'user', content: userMessage }])
    setIsProcessing(true)

    try {
      // Call customization API
      const response = await chatAPI.customizeRecipe({
        recipe_id: recipe.id,
        recipe_name: recipe.name,
        original_ingredients: recipe.ingredients,
        original_instructions: recipe.steps,
        modification_request: userMessage
      })

      if (response.success && response.modified_recipe) {
        // Update modified recipe
        setModifiedRecipe(response.modified_recipe)
        
        // Add AI response
        setChatMessages(prev => [...prev, {
          role: 'assistant',
          content: response.message || `Great! I've customized the recipe based on your request. You can see the changes below. If you'd like to make more adjustments, just let me know! When you're happy with it, click "Save as New Recipe".`
        }])
      } else {
        setChatMessages(prev => [...prev, {
          role: 'assistant',
          content: response.message || "I'm sorry, I couldn't process that request. Could you try rephrasing it?"
        }])
      }
    } catch (error) {
      console.error('Customization error:', error)
      setChatMessages(prev => [...prev, {
        role: 'assistant',
        content: "Oops! Something went wrong. Please try again."
      }])
    } finally {
      setIsProcessing(false)
    }
  }

  const handleSaveNewRecipe = async () => {
    if (!modifiedRecipe) {
      alert('⚠️ Please customize the recipe first before saving!')
      return
    }

    setIsSaving(true)
    try {
      const newRecipe = {
        ...recipe,
        id: `custom_${Date.now()}`,
        name: customTitle,
        ingredients: modifiedRecipe.ingredients || recipe.ingredients,
        steps: modifiedRecipe.instructions || recipe.steps,
        description: modifiedRecipe.description || recipe.description,
        isCustom: true,
        originalRecipeId: recipe.id,
        createdAt: new Date().toISOString()
      }

      // Save to localStorage (custom recipes)
      const savedRecipes = JSON.parse(localStorage.getItem('customRecipes') || '[]')
      savedRecipes.push(newRecipe)
      localStorage.setItem('customRecipes', JSON.stringify(savedRecipes))

      // Callback to parent
      if (onSaveNewRecipe) {
        onSaveNewRecipe(newRecipe)
      }

      alert('✅ Recipe saved successfully!')
      onBack()
    } catch (error) {
      console.error('Save error:', error)
      alert('❌ Failed to save recipe. Please try again.')
    } finally {
      setIsSaving(false)
    }
  }

  const displayRecipe = modifiedRecipe || {
    ingredients: recipe.ingredients,
    instructions: recipe.steps,
    description: recipe.description
  }

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <button className={styles.backBtn} onClick={onBack}>
          <ArrowLeft size={20} />
        </button>
        <input
          type="text"
          className={styles.titleInput}
          value={customTitle}
          onChange={(e) => setCustomTitle(e.target.value)}
          placeholder="Recipe name..."
        />
        <button
          className={styles.saveBtn}
          onClick={handleSaveNewRecipe}
          disabled={isSaving || !modifiedRecipe}
        >
          {isSaving ? (
            <Loader size={18} className={styles.spinner} />
          ) : (
            <Save size={18} />
          )}
          Save as New
        </button>
      </div>

      <div className={styles.mainContent}>
        {/* Original Recipe Card Display */}
        <div className={styles.recipeCard}>
          <div className={styles.recipeHeader}>
            <div className={styles.recipeTitleSection}>
              <h2>{recipe.name}</h2>
              <div className={styles.recipeInfo}>
                <span>⏱️ {recipe.time} min</span>
                <span>📊 {recipe.level || 'Medium'}</span>
              </div>
            </div>
            {modifiedRecipe && (
              <span className={styles.modifiedBadge}>✨ Modified</span>
            )}
          </div>

          <div className={styles.section}>
            <h4>Description</h4>
            <p className={styles.description}>
              {displayRecipe.description || recipe.description}
            </p>
          </div>

          <div className={styles.section}>
            <h4>Ingredients</h4>
            <ul className={styles.ingredientsList}>
              {displayRecipe.ingredients.map((ing, i) => {
                const originalIng = recipe.ingredients[i]
                const isModified = modifiedRecipe && originalIng && ing !== originalIng
                
                return (
                  <li key={i} className={isModified ? styles.modified : ''}>
                    {isModified && (
                      <span className={styles.original}>
                        <s>{originalIng}</s> →
                      </span>
                    )}
                    <span className={isModified ? styles.new : ''}>{ing}</span>
                  </li>
                )
              })}
            </ul>
          </div>

          <div className={styles.section}>
            <h4>Instructions</h4>
            <ol className={styles.stepsList}>
              {displayRecipe.instructions.map((step, i) => {
                const originalStep = recipe.steps[i]
                const isModified = modifiedRecipe && originalStep && step !== originalStep
                
                return (
                  <li key={i} className={isModified ? styles.modified : ''}>
                    {isModified && (
                      <div className={styles.original}>
                        <s>{originalStep}</s>
                      </div>
                    )}
                    <div className={isModified ? styles.new : ''}>{step}</div>
                  </li>
                )
              })}
            </ol>
          </div>
        </div>
      </div>

      {/* Floating AI Chat Panel */}
      <div className={styles.floatingChatPanel}>
          <div className={styles.chatHeader}>
            <h3>💬 AI Customization Assistant</h3>
          </div>

          <div className={styles.chatMessages}>
            {chatMessages.map((msg, i) => (
              <div
                key={i}
                className={`${styles.message} ${styles[msg.role]}`}
              >
                <div className={styles.messageContent}>
                  {msg.content}
                </div>
              </div>
            ))}
            {isProcessing && (
              <div className={`${styles.message} ${styles.assistant}`}>
                <div className={styles.messageContent}>
                  <Loader size={16} className={styles.spinner} />
                  <span>Thinking...</span>
                </div>
              </div>
            )}
          </div>

          <div className={styles.chatInput}>
            <input
              type="text"
              placeholder="Tell me what you'd like to change..."
              value={userInput}
              onChange={(e) => setUserInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault()
                  handleSendMessage()
                }
              }}
              disabled={isProcessing}
            />
            <button
              onClick={handleSendMessage}
              disabled={!userInput.trim() || isProcessing}
              className={styles.sendBtn}
            >
              <Send size={18} />
            </button>
          </div>
        </div>
    </div>
  )
}

export default RecipeCustomizationView

