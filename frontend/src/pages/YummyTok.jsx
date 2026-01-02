import { useState, useEffect } from 'react'
import { ThumbsUp, ThumbsDown, Bookmark, BookmarkCheck, ChevronUp, ChevronDown, Clock, Sparkles } from 'lucide-react'
import { chatAPI } from '../api/client'
import styles from './YummyTok.module.css'

// Sample recipes for demo (in production, fetch from database/API)
const SAMPLE_RECIPES = [
  {
    id: 'yt1',
    name: 'Creamy Garlic Pasta',
    time: 20,
    level: 'easy',
    image: '🍝',
    ingredients: ['pasta', 'garlic', 'cream', 'parmesan', 'butter'],
    steps: ['Boil pasta', 'Sauté garlic in butter', 'Add cream and parmesan', 'Toss with pasta', 'Serve hot'],
    source: 'YummyTok Community',
  },
  {
    id: 'yt2',
    name: 'Avocado Toast Deluxe',
    time: 5,
    level: 'easy',
    image: '🥑',
    ingredients: ['bread', 'avocado', 'eggs', 'chili flakes', 'lime'],
    steps: ['Toast bread', 'Mash avocado with lime', 'Fry egg sunny side up', 'Spread avocado on toast', 'Top with egg and chili'],
    source: 'Healthy Eats Blog',
  },
  {
    id: 'yt3',
    name: 'Teriyaki Chicken Bowl',
    time: 25,
    level: 'medium',
    image: '🍗',
    ingredients: ['chicken', 'rice', 'soy sauce', 'honey', 'broccoli'],
    steps: ['Cook rice', 'Slice chicken', 'Make teriyaki sauce', 'Stir fry chicken', 'Assemble bowl'],
    source: 'Asian Fusion Kitchen',
  },
  {
    id: 'yt4',
    name: 'Berry Smoothie Bowl',
    time: 5,
    level: 'easy',
    image: '🫐',
    ingredients: ['frozen berries', 'banana', 'yogurt', 'granola', 'honey'],
    steps: ['Blend berries with banana', 'Add yogurt', 'Pour into bowl', 'Top with granola', 'Drizzle honey'],
    source: 'Morning Boost',
  },
  {
    id: 'yt5',
    name: 'Spicy Ramen',
    time: 15,
    level: 'easy',
    image: '🍜',
    ingredients: ['ramen noodles', 'egg', 'green onion', 'chili paste', 'sesame oil'],
    steps: ['Boil noodles', 'Soft boil egg', 'Mix chili paste with broth', 'Assemble ramen', 'Top with egg and onion'],
    source: 'Late Night Eats',
  },
  {
    id: 'yt6',
    name: 'Mediterranean Wrap',
    time: 10,
    level: 'easy',
    image: '🌯',
    ingredients: ['tortilla', 'hummus', 'cucumber', 'tomato', 'feta'],
    steps: ['Spread hummus on tortilla', 'Chop veggies', 'Add feta', 'Roll tightly', 'Slice in half'],
    source: 'Quick Lunch Ideas',
  },
  {
    id: 'yt7',
    name: 'Banana Pancakes',
    time: 15,
    level: 'easy',
    image: '🥞',
    ingredients: ['banana', 'eggs', 'oats', 'cinnamon', 'maple syrup'],
    steps: ['Mash banana', 'Mix with eggs and oats', 'Add cinnamon', 'Cook on pan', 'Serve with syrup'],
    source: 'Breakfast Club',
  },
  {
    id: 'yt8',
    name: 'Caprese Salad',
    time: 5,
    level: 'easy',
    image: '🍅',
    ingredients: ['tomatoes', 'mozzarella', 'basil', 'olive oil', 'balsamic'],
    steps: ['Slice tomatoes', 'Slice mozzarella', 'Layer with basil', 'Drizzle oil and balsamic', 'Season with salt'],
    source: 'Italian Classics',
  },
]

function YummyTok({ onSave, onLike, onDislike, savedRecipes, likedRecipes }) {
  const [currentIndex, setCurrentIndex] = useState(0)
  const [recipes, setRecipes] = useState(SAMPLE_RECIPES)
  const [showDetails, setShowDetails] = useState(false)

  const currentRecipe = recipes[currentIndex]
  const isSaved = savedRecipes?.some(r => r.id === currentRecipe?.id)
  const isLiked = likedRecipes?.includes(currentRecipe?.id)

  const goNext = () => {
    if (currentIndex < recipes.length - 1) {
      setCurrentIndex(prev => prev + 1)
      setShowDetails(false)
    }
  }

  const goPrev = () => {
    if (currentIndex > 0) {
      setCurrentIndex(prev => prev - 1)
      setShowDetails(false)
    }
  }

  const handleLike = () => {
    if (currentRecipe && !isLiked) {
      onLike(currentRecipe.id)
    }
    goNext()
  }

  const handleDislike = () => {
    if (currentRecipe) {
      onDislike(currentRecipe.id)
    }
    goNext()
  }

  const handleSave = () => {
    if (currentRecipe) {
      onSave(currentRecipe)
    }
  }

  // Handle keyboard/swipe
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'ArrowUp') goPrev()
      if (e.key === 'ArrowDown') goNext()
      if (e.key === 'ArrowLeft') handleDislike()
      if (e.key === 'ArrowRight') handleLike()
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [currentIndex])

  if (!currentRecipe) {
    return (
      <div className={styles.page}>
        <div className={styles.empty}>
          <Sparkles size={48} />
          <h2>No more recipes!</h2>
          <p>Check back later for more</p>
        </div>
      </div>
    )
  }

  return (
    <div className={styles.page}>
      {/* Recipe Card */}
      <div className={styles.card} onClick={() => setShowDetails(!showDetails)}>
        <div className={styles.cardBackground}>
          <span className={styles.emoji}>{currentRecipe.image}</span>
        </div>
        
        <div className={styles.cardContent}>
          <div className={styles.source}>{currentRecipe.source}</div>
          <h2 className={styles.title}>{currentRecipe.name}</h2>
          <div className={styles.meta}>
            <span><Clock size={14} /> {currentRecipe.time} min</span>
            <span className={styles.level}>{currentRecipe.level}</span>
          </div>
          
          {showDetails && (
            <div className={styles.details}>
              <h4>Ingredients</h4>
              <p>{currentRecipe.ingredients.join(', ')}</p>
              <h4>Steps</h4>
              <ol>
                {currentRecipe.steps.map((step, i) => (
                  <li key={i}>{step}</li>
                ))}
              </ol>
            </div>
          )}
          
          <p className={styles.tapHint}>
            {showDetails ? 'Tap to hide' : 'Tap for details'}
          </p>
        </div>
      </div>

      {/* Navigation arrows */}
      <button 
        className={`${styles.navBtn} ${styles.up}`}
        onClick={goPrev}
        disabled={currentIndex === 0}
      >
        <ChevronUp size={28} />
      </button>
      <button 
        className={`${styles.navBtn} ${styles.down}`}
        onClick={goNext}
        disabled={currentIndex === recipes.length - 1}
      >
        <ChevronDown size={28} />
      </button>

      {/* Action buttons */}
      <div className={styles.actions}>
        <button 
          className={`${styles.actionBtn} ${styles.dislike}`}
          onClick={handleDislike}
        >
          <ThumbsDown size={24} />
        </button>
        
        <button 
          className={`${styles.actionBtn} ${styles.save} ${isSaved ? styles.saved : ''}`}
          onClick={handleSave}
        >
          {isSaved ? <BookmarkCheck size={24} /> : <Bookmark size={24} />}
        </button>
        
        <button 
          className={`${styles.actionBtn} ${styles.like} ${isLiked ? styles.liked : ''}`}
          onClick={handleLike}
        >
          <ThumbsUp size={24} />
        </button>
      </div>

      {/* Progress indicator */}
      <div className={styles.progress}>
        {currentIndex + 1} / {recipes.length}
      </div>
    </div>
  )
}

export default YummyTok

