import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ArrowLeft, Bookmark, Clock, ShoppingCart, Trash2, ChefHat } from 'lucide-react'
import styles from './Profile.module.css'

function Profile({ savedRecipes, onUnsave }) {
  const navigate = useNavigate()
  const [selectedRecipe, setSelectedRecipe] = useState(null)

  const addToCart = (ingredients) => {
    // Save to localStorage first
    const existing = JSON.parse(localStorage.getItem('cartItems') || '[]')
    const newItems = ingredients.map(ing => ({
      id: Date.now() + Math.random(),
      name: ing,
      checked: false
    }))
    const updated = [...existing, ...newItems]
    localStorage.setItem('cartItems', JSON.stringify(updated))
    
    // Show feedback and navigate
    alert(`Added ${ingredients.length} ingredients to cart!`)
    
    // Small delay to ensure localStorage is synced before navigation
    setTimeout(() => {
      navigate('/cart')
    }, 50)
  }

  return (
    <div className={styles.page}>
      <div className="container">
        <header className={styles.header}>
          <button className={styles.backBtn} onClick={() => navigate(-1)}>
            <ArrowLeft size={20} />
          </button>
          <div>
            <h1>My Profile</h1>
            <p>{savedRecipes.length} saved recipes</p>
          </div>
        </header>

        {savedRecipes.length === 0 ? (
          <div className={styles.empty}>
            <Bookmark size={48} />
            <h3>No saved recipes yet</h3>
            <p>Go to YummyTok and save recipes you like!</p>
            <button className="btn btn-primary" onClick={() => navigate('/yummytok')}>
              Explore YummyTok
            </button>
          </div>
        ) : (
          <div className={styles.recipesList}>
            {savedRecipes.map(recipe => (
              <div key={recipe.id} className={styles.recipeCard}>
                <div className={styles.cardHeader}>
                  <span className={styles.emoji}>{recipe.image}</span>
                  <div className={styles.cardInfo}>
                    <h3>{recipe.name}</h3>
                    <div className={styles.meta}>
                      <span><Clock size={14} /> {recipe.time} min</span>
                      <span>{recipe.level}</span>
                    </div>
                  </div>
                  <button 
                    className={styles.removeBtn}
                    onClick={() => onUnsave(recipe.id)}
                  >
                    <Trash2 size={18} />
                  </button>
                </div>

                <div className={styles.cardBody}>
                  <div className={styles.ingredients}>
                    <strong>Ingredients:</strong> {recipe.ingredients.join(', ')}
                  </div>
                </div>

                <div className={styles.cardActions}>
                  <button 
                    className={styles.detailsBtn}
                    onClick={() => setSelectedRecipe(selectedRecipe?.id === recipe.id ? null : recipe)}
                  >
                    {selectedRecipe?.id === recipe.id ? 'Hide Steps' : 'View Steps'}
                  </button>
                  <button 
                    className={styles.cartBtn}
                    onClick={() => addToCart(recipe.ingredients)}
                  >
                    <ShoppingCart size={16} />
                    Add to Cart
                  </button>
                </div>

                {selectedRecipe?.id === recipe.id && (
                  <div className={styles.steps}>
                    <h4>Steps:</h4>
                    <ol>
                      {recipe.steps.map((step, i) => (
                        <li key={i}>{step}</li>
                      ))}
                    </ol>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default Profile

