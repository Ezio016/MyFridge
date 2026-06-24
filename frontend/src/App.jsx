import { useState } from 'react'
import { Routes, Route } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import Layout from './components/Layout'
import Landing from './pages/Landing'
import Fridge from './pages/Fridge'
import Chef from './pages/Chef'
import YummyTok from './pages/YummyTok'
import Cart from './pages/Cart'
import Profile from './pages/Profile'
import RecipeLab from './pages/RecipeLab'
import Login from './pages/Login'

function App() {
  // Global state for saved recipes (in production, use context or state management)
  const [savedRecipes, setSavedRecipes] = useState([])
  const [likedRecipes, setLikedRecipes] = useState([]) // IDs of liked recipes

  const saveRecipe = (recipe) => {
    setSavedRecipes(prev => {
      if (prev.find(r => r.id === recipe.id)) return prev
      return [...prev, recipe]
    })
  }

  const unsaveRecipe = (recipeId) => {
    setSavedRecipes(prev => prev.filter(r => r.id !== recipeId))
  }

  const likeRecipe = (recipeId) => {
    setLikedRecipes(prev => [...prev, recipeId])
  }

  const dislikeRecipe = (recipeId) => {
    // Could track dislikes for algorithm, for now just skip
  }

  return (
    <AuthProvider>
      <Layout>
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/login" element={<Login />} />
          <Route path="/fridge" element={<Fridge />} />
          <Route path="/chef" element={<Chef />} />
          <Route 
            path="/yummytok" 
            element={
              <YummyTok 
                onSave={saveRecipe}
                onLike={likeRecipe}
                onDislike={dislikeRecipe}
                savedRecipes={savedRecipes}
                likedRecipes={likedRecipes}
              />
            } 
          />
          <Route path="/cart" element={<Cart />} />
          <Route path="/profile" element={<Profile />} />
          <Route path="/lab" element={<RecipeLab />} />
        </Routes>
      </Layout>
    </AuthProvider>
  )
}

export default App
