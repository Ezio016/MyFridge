import { useState, useEffect } from 'react'

const STORAGE_KEY = 'myfridge_favorites'

/**
 * Hook to manage favorite recipes using localStorage
 */
export function useFavorites() {
  const [favorites, setFavorites] = useState([])

  // Load favorites from localStorage on mount
  useEffect(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY)
      if (stored) {
        setFavorites(JSON.parse(stored))
      }
    } catch (err) {
      console.error('Failed to load favorites:', err)
    }
  }, [])

  // Save favorites to localStorage whenever they change
  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(favorites))
    } catch (err) {
      console.error('Failed to save favorites:', err)
    }
  }, [favorites])

  const isFavorite = (recipeId) => {
    return favorites.some(f => f.id === recipeId)
  }

  const addFavorite = (recipe) => {
    setFavorites(prev => {
      // Avoid duplicates
      if (prev.some(f => f.id === recipe.id)) {
        return prev
      }
      return [...prev, recipe]
    })
  }

  const removeFavorite = (recipeId) => {
    setFavorites(prev => prev.filter(f => f.id !== recipeId))
  }

  const toggleFavorite = (recipe) => {
    if (isFavorite(recipe.id)) {
      removeFavorite(recipe.id)
    } else {
      addFavorite(recipe)
    }
  }

  return {
    favorites,
    isFavorite,
    addFavorite,
    removeFavorite,
    toggleFavorite,
  }
}

