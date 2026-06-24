import { useState } from 'react'
import { X, Send, Loader, Save } from 'lucide-react'
import { chatAPI } from '../api/client'
import styles from './FloatingCustomizationChat.module.css'

/**
 * Floating Customization Chat - Overlay on top of recipe view
 */
function FloatingCustomizationChat({ recipe, onClose, onSaveNewRecipe }) {
  const [customTitle, setCustomTitle] = useState(`${recipe.name} (Custom)`)
  const [chatMessages, setChatMessages] = useState([
    {
      role: 'assistant',
      content: `Hi! I'm here to help you customize "${recipe.name}". What would you like to change?\n\nYou can ask me to:\n• Make it vegetarian or vegan\n• Swap ingredients\n• Adjust cooking time\n• Change spice level\n• Remove allergens\n• Add more vegetables\n\nWhat would you like to do?`
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
    
    setChatMessages(prev => [...prev, { role: 'user', content: userMessage }])
    setIsProcessing(true)

    try {
      const response = await chatAPI.customizeRecipe({
        recipe_id: recipe.id,
        recipe_name: recipe.name,
        original_ingredients: recipe.ingredients,
        original_instructions: recipe.steps,
        modification_request: userMessage
      })

      if (response.success && response.modified_recipe) {
        setModifiedRecipe(response.modified_recipe)
        
        setChatMessages(prev => [...prev, {
          role: 'assistant',
          content: response.message || `Great! I've customized the recipe. When you're happy with it, click "Save as New Recipe".`
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

      const savedRecipes = JSON.parse(localStorage.getItem('customRecipes') || '[]')
      savedRecipes.push(newRecipe)
      localStorage.setItem('customRecipes', JSON.stringify(savedRecipes))

      if (onSaveNewRecipe) {
        onSaveNewRecipe(newRecipe)
      }

      alert('✅ Recipe saved successfully!')
      onClose()
    } catch (error) {
      console.error('Save error:', error)
      alert('❌ Failed to save recipe. Please try again.')
    } finally {
      setIsSaving(false)
    }
  }

  return (
    <>
      {/* Backdrop */}
      <div className={styles.backdrop} onClick={onClose} />
      
      {/* Floating Chat */}
      <div className={styles.floatingChat}>
        <div className={styles.header}>
          <div className={styles.headerContent}>
            <h3>💬 Customize Recipe</h3>
            <input
              type="text"
              className={styles.titleInput}
              value={customTitle}
              onChange={(e) => setCustomTitle(e.target.value)}
              placeholder="Custom recipe name..."
            />
          </div>
          <button className={styles.closeBtn} onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        <div className={styles.messages}>
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

        <div className={styles.inputArea}>
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

        <div className={styles.footer}>
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
            Save as New Recipe
          </button>
        </div>
      </div>
    </>
  )
}

export default FloatingCustomizationChat

