import { useState } from 'react'
import { MessageCircle, X, Send, ChefHat, Loader } from 'lucide-react'
import { chatAPI } from '../api/client'
import styles from './ChefAssistantChat.module.css'

/**
 * Chef Assistant Chat - Ask AI for help
 * - Browsing mode: Filter and narrow down recipe options
 * - Cooking mode: Modify the selected recipe
 */
function ChefAssistantChat({ 
  mode = 'browsing', 
  selectedRecipe, 
  disabled = false, 
  onCustomizeRecipe,
  controlsState,
  onControlsUpdate,
  facets 
}) {
  const [isOpen, setIsOpen] = useState(false)
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)

  // Quick suggestions based on mode
  const browsingQuickActions = [
    { label: '⚡ Quick (under 20m)', prompt: 'Show me recipes under 20 minutes' },
    { label: '✨ Ready to cook', prompt: 'Show only recipes I can make right now' },
    { label: '🥬 Vegetarian', prompt: 'Show me vegetarian recipes' },
    { label: '🔥 Most popular', prompt: 'Sort by most popular' },
    { label: '⏱️ Fastest first', prompt: 'Sort by fastest to make' },
    { label: '🔄 Reset filters', prompt: 'Reset all filters' },
  ]

  const cookingQuickActions = [
    { label: '🥬 Make vegetarian', prompt: 'How can I make this recipe vegetarian?' },
    { label: '🌱 Make vegan', prompt: 'How can I make this recipe vegan?' },
    { label: '🍗 Substitute protein', prompt: 'What protein can I substitute in this recipe?' },
    { label: '📏 Half the recipe', prompt: 'How do I halve this recipe?' },
    { label: '🌶️ Make it spicier', prompt: 'How can I make this recipe spicier?' },
    { label: '🚫 Less salt', prompt: 'How can I reduce sodium in this recipe?' },
  ]

  const quickActions = mode === 'cooking' ? cookingQuickActions : browsingQuickActions

  const sendMessage = async (text) => {
    if (!text.trim() || loading) return

    const userMsg = { role: 'user', content: text }
    setMessages(prev => [...prev, userMsg])
    setInput('')
    setLoading(true)

    try {
      if (mode === 'cooking' && selectedRecipe && onCustomizeRecipe) {
        // Cooking mode: Customize the recipe
        setMessages(prev => [...prev, { 
          role: 'assistant', 
          content: "🍳 Let me customize that recipe for you..." 
        }])
        
        // Trigger the customization flow
        await onCustomizeRecipe(selectedRecipe, text)
        
        // Close the chat after triggering customization
        setIsOpen(false)
        setMessages([]) // Reset for next time
      } else {
        // Browsing mode: Apply filters/sorts dynamically
        console.log('🔍 Sending to controls API:', { text, controlsState, facets })
      
        const response = await chatAPI.controls(text, controlsState || {}, facets || {})
        
        console.log('✅ Controls API response:', response)
        
        // Show AI's response message
      setMessages(prev => [...prev, { 
        role: 'assistant', 
          content: response.assistant_message || "✅ Updated your filters!"
      }])
        
        // Apply the new state to update recipes display
        if (onControlsUpdate && response.new_state) {
          onControlsUpdate(response.new_state)
        }
      }
    } catch (err) {
      console.error('❌ Chat error:', err)
      console.error('Error details:', err.message, err.stack)
      
      let errorMsg = "Oops! Something went wrong. "
      
      // Provide more helpful error messages
      if (err.message?.includes('fetch')) {
        errorMsg += "Could not connect to server. Is the backend running?"
      } else if (err.message?.includes('JSON')) {
        errorMsg += "Invalid response from server."
      } else if (err.message) {
        errorMsg += err.message
      } else {
        errorMsg += "Please try again."
      }
      
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: errorMsg
      }])
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    sendMessage(input)
  }

  const handleQuickAction = (prompt) => {
    sendMessage(prompt)
  }

  if (disabled) return null

  const title = mode === 'cooking' ? 'Customize Recipe' : 'Help finding your favorite recipe'
  const placeholder = mode === 'cooking' 
    ? 'Ask to customize recipe...' 
    : 'E.g., "quick Italian dishes", "vegetarian under 30 min"'
  const welcomeMsg = mode === 'cooking'
    ? '👋 Let me help customize this recipe!'
    : '👋 Tell me what you\'re looking for and I\'ll filter the recipes for you!'

  return (
    <div className={styles.container}>
      {/* Floating Action Button */}
      <button 
        className={`${styles.fab} ${isOpen ? styles.fabOpen : ''}`}
        onClick={() => setIsOpen(!isOpen)}
        aria-label={isOpen ? 'Close chat' : 'Open assistant'}
      >
        {isOpen ? <X size={24} /> : <MessageCircle size={24} />}
      </button>

      {/* Chat Panel */}
      {isOpen && (
        <div className={styles.panel}>
          <div className={styles.header}>
            <ChefHat size={20} />
            <span>{title}</span>
          </div>

          {/* Messages */}
          <div className={styles.messages}>
            {messages.length === 0 ? (
              <div className={styles.welcome}>
                <p>{welcomeMsg}</p>
                <div className={styles.quickMods}>
                  {quickActions.map((action, i) => (
                    <button
                      key={i}
                      className={styles.quickBtn}
                      onClick={() => handleQuickAction(action.prompt)}
                    >
                      {action.label}
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              messages.map((msg, i) => (
                <div 
                  key={i} 
                  className={`${styles.message} ${msg.role === 'user' ? styles.user : styles.assistant}`}
                >
                  {msg.content}
                </div>
              ))
            )}
            {loading && (
              <div className={`${styles.message} ${styles.assistant}`}>
                <Loader size={16} className={styles.spinner} />
                Thinking...
              </div>
            )}
          </div>

          {/* Input */}
          <form className={styles.inputArea} onSubmit={handleSubmit}>
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={placeholder}
              disabled={loading}
            />
            <button type="submit" disabled={!input.trim() || loading}>
              <Send size={18} />
            </button>
          </form>
        </div>
      )}
    </div>
  )
}

export default ChefAssistantChat
