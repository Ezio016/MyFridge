import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { ArrowLeft, Heart, Clock, ShoppingCart, Trash2, ChefHat, User } from 'lucide-react'
import { useFavorites } from '../hooks/useFavorites'
import styles from './Profile.module.css'

function Profile() {
  const navigate = useNavigate()
  const [selectedRecipe, setSelectedRecipe] = useState(null)
  const { favorites, toggleFavorite } = useFavorites()

  const addToCart = (recipe) => {
    // Get all ingredients from the recipe
    const allIngredients = [
      ...(recipe.mainIngredients || []),
      ...(recipe.optionalIngredients || [])
    ]
    
    // Save to localStorage first
    const existing = JSON.parse(localStorage.getItem('cartItems') || '[]')
    const newItems = allIngredients.map(ing => ({
      id: Date.now() + Math.random(),
      name: ing,
      checked: false
    }))
    const updated = [...existing, ...newItems]
    localStorage.setItem('cartItems', JSON.stringify(updated))
    
    // Show feedback and navigate
    alert(`Added ${allIngredients.length} ingredients to cart!`)
    
    // Small delay to ensure localStorage is synced before navigation
    setTimeout(() => {
      navigate('/cart')
    }, 50)
  }

  return (
    <div className={styles.page}>
      <div className="container">
        <header className={styles.header}>
          <div className={styles.profileIcon}>
            <User size={32} />
          </div>
          <div>
            <h1>My Profile</h1>
            <p>{favorites.length} favorite recipes</p>
          </div>
        </header>

        {favorites.length === 0 ? (
          <div className={styles.empty}>
            <Heart size={48} />
            <h3>No favorite recipes yet</h3>
            <p>Go to Chef and favorite recipes you love!</p>
            <button className="btn btn-primary" onClick={() => navigate('/chef')}>
              Browse Recipes
            </button>
          </div>
        ) : (
          <div className={styles.recipesList}>
            {favorites.map(recipe => (
              <div key={recipe.id} className={styles.recipeCard}>
                <div className={styles.cardHeader}>
                  <span className={styles.emoji}>{recipe.image || '🍽️'}</span>
                  <div className={styles.cardInfo}>
                    <h3>{recipe.name}</h3>
                    <div className={styles.meta}>
                      <span><Clock size={14} /> {recipe.time} min</span>
                      <span>{recipe.level}</span>
                    </div>
                  </div>
                  <button 
                    className={styles.removeBtn}
                    onClick={() => toggleFavorite(recipe)}
                    title="Remove from favorites"
                  >
                    <Heart size={18} fill="currentColor" />
                  </button>
                </div>

                <div className={styles.cardBody}>
                  <div className={styles.ingredients}>
                    <strong>Main Ingredients:</strong> {recipe.mainIngredients?.join(', ') || 'N/A'}
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
                    onClick={() => addToCart(recipe)}
                  >
                    <ShoppingCart size={16} />
                    Add to Cart
                  </button>
                  <button 
                    className={styles.cookBtn}
                    onClick={() => navigate('/chef')}
                  >
                    <ChefHat size={16} />
                    Cook Now
                  </button>
                </div>

                {selectedRecipe?.id === recipe.id && recipe.steps && (
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

