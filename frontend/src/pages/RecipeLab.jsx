import { useState, useEffect } from 'react'
import { ArrowLeft, Shuffle, Combine, RefreshCw, Sparkles, FlaskConical, ChevronDown, Save, Check } from 'lucide-react'
import { API_BASE } from '../api/config'
import styles from './RecipeLab.module.css'


export default function RecipeLab() {
  const [recipes, setRecipes] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  
  // Fusion state
  const [recipeA, setRecipeA] = useState(null)
  const [recipeB, setRecipeB] = useState(null)
  const [fusionRatio, setFusionRatio] = useState(0.5)
  const [fusedRecipe, setFusedRecipe] = useState(null)
  
  // Random state
  const [randomProtein, setRandomProtein] = useState('')
  const [randomRecipe, setRandomRecipe] = useState(null)
  
  // Remix state
  const [remixRecipe, setRemixRecipe] = useState(null)
  const [swapIngredient, setSwapIngredient] = useState('')
  const [newIngredient, setNewIngredient] = useState('')
  const [remixedRecipe, setRemixedRecipe] = useState(null)
  
  // Saved generated recipes
  const [savedRecipes, setSavedRecipes] = useState(() => {
    const saved = localStorage.getItem('creativeRecipes')
    return saved ? JSON.parse(saved) : []
  })
  const [justSaved, setJustSaved] = useState(null)
  
  // Active tab
  const [activeTab, setActiveTab] = useState('fusion')
  
  // Load recipes on mount
  useEffect(() => {
    loadRecipes()
  }, [])
  
  const loadRecipes = async () => {
    try {
      const res = await fetch(`${API_BASE}/recipes/`)
      const data = await res.json()
      setRecipes(data.recipes || data || [])
    } catch (err) {
      console.error('Failed to load recipes:', err)
    }
  }
  
  const saveCreativeRecipe = (recipe) => {
    const newRecipe = {
      ...recipe,
      id: `creative_${Date.now()}`,
      savedAt: new Date().toISOString(),
      isCreative: true
    }
    
    const updated = [...savedRecipes, newRecipe]
    setSavedRecipes(updated)
    localStorage.setItem('creativeRecipes', JSON.stringify(updated))
    
    // Show saved feedback
    setJustSaved(newRecipe.id)
    setTimeout(() => setJustSaved(null), 2000)
    
    return newRecipe
  }
  
  const handleFusion = async () => {
    if (!recipeA || !recipeB) {
      setError('Please select two recipes to fuse')
      return
    }
    
    setLoading(true)
    setError(null)
    
    try {
      const res = await fetch(`${API_BASE}/lab/fuse`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          recipe_a_id: recipeA.id,
          recipe_b_id: recipeB.id,
          ratio: fusionRatio
        })
      })
      
      const data = await res.json()
      if (data.success) {
        setFusedRecipe(data.fused_recipe)
      } else {
        setError(data.detail || 'Fusion failed')
      }
    } catch (err) {
      setError('Failed to fuse recipes')
    } finally {
      setLoading(false)
    }
  }
  
  const handleRandom = async () => {
    setLoading(true)
    setError(null)
    
    try {
      const res = await fetch(`${API_BASE}/lab/random`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          protein: randomProtein || null,
          difficulty: 'easy'
        })
      })
      
      const data = await res.json()
      if (data.success) {
        setRandomRecipe(data.recipe)
      } else {
        setError(data.detail || 'Generation failed')
      }
    } catch (err) {
      setError('Failed to generate recipe')
    } finally {
      setLoading(false)
    }
  }
  
  const handleRemix = async () => {
    if (!remixRecipe || !swapIngredient || !newIngredient) {
      setError('Please select a recipe and both ingredients')
      return
    }
    
    setLoading(true)
    setError(null)
    
    try {
      const res = await fetch(`${API_BASE}/lab/remix`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          recipe_id: remixRecipe.id,
          swap_ingredient: swapIngredient,
          new_ingredient: newIngredient
        })
      })
      
      const data = await res.json()
      if (data.success) {
        setRemixedRecipe(data.remixed_recipe)
      } else {
        setError(data.detail || 'Remix failed')
      }
    } catch (err) {
      setError('Failed to remix recipe')
    } finally {
      setLoading(false)
    }
  }
  
  
  const RecipeCard = ({ recipe, title }) => {
    const isSaved = savedRecipes.some(r => r.name === recipe.name)
    const wasJustSaved = justSaved && savedRecipes.find(r => r.id === justSaved)?.name === recipe.name
    
    return (
      <div className={styles.resultCard}>
        <div className={styles.resultHeader}>
          <div>
            <h3>{title}</h3>
            <h4>{recipe.name}</h4>
          </div>
          <button
            className={`${styles.saveRecipeBtn} ${isSaved ? styles.saved : ''}`}
            onClick={() => !isSaved && saveCreativeRecipe(recipe)}
            disabled={isSaved}
          >
            {wasJustSaved ? (
              <><Check size={16} /> Saved!</>
            ) : isSaved ? (
              <><Check size={16} /> Saved</>
            ) : (
              <><Save size={16} /> Save Recipe</>
            )}
          </button>
        </div>
        <p className={styles.description}>{recipe.description}</p>
        
        <div className={styles.ingredients}>
          <strong>Ingredients:</strong>
          <ul>
            {recipe.ingredients?.slice(0, 8).map((ing, i) => (
              <li key={i}>{ing}</li>
            ))}
            {recipe.ingredients?.length > 8 && (
              <li className={styles.more}>+{recipe.ingredients.length - 8} more...</li>
            )}
          </ul>
        </div>
        
        {recipe.instructions && (
          <div className={styles.instructions}>
            <strong>Instructions:</strong>
            <ol>
              {recipe.instructions.slice(0, 4).map((step, i) => (
                <li key={i}>{step}</li>
              ))}
            </ol>
          </div>
        )}
        
        <div className={styles.meta}>
          <span>⏱️ {recipe.total_time || 30} min</span>
          <span>🍽️ {recipe.servings || 4} servings</span>
          <span>📊 {recipe.difficulty || 'medium'}</span>
        </div>
      </div>
    )
  }
  
  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <a href="/" className={styles.backLink}>
          <ArrowLeft size={20} />
          Back to App
        </a>
        <h1>
          <FlaskConical size={32} />
          Creative Meals
        </h1>
        <p className={styles.subtitle}>
          Combine, generate, and remix recipes using AI-powered creativity
        </p>
      </header>
      
      {error && (
        <div className={styles.error}>
          {error}
          <button onClick={() => setError(null)}>×</button>
        </div>
      )}
      
      <div className={styles.tabs}>
        <button 
          className={`${styles.tab} ${activeTab === 'fusion' ? styles.active : ''}`}
          onClick={() => setActiveTab('fusion')}
        >
          <Combine size={18} />
          Fusion
        </button>
        <button 
          className={`${styles.tab} ${activeTab === 'random' ? styles.active : ''}`}
          onClick={() => setActiveTab('random')}
        >
          <Shuffle size={18} />
          Random
        </button>
        <button 
          className={`${styles.tab} ${activeTab === 'remix' ? styles.active : ''}`}
          onClick={() => setActiveTab('remix')}
        >
          <RefreshCw size={18} />
          Remix
        </button>
        <button 
          className={`${styles.tab} ${activeTab === 'saved' ? styles.active : ''}`}
          onClick={() => setActiveTab('saved')}
        >
          <Save size={18} />
          Saved {savedRecipes.length > 0 && `(${savedRecipes.length})`}
        </button>
      </div>
      
      <div className={styles.content}>
        {/* FUSION TAB */}
        {activeTab === 'fusion' && (
          <div className={styles.panel}>
            <div className={styles.formula}>
              <code>Recipe_Fusion = α × Recipe_A + (1-α) × Recipe_B</code>
            </div>
            
            <div className={styles.fusionInputs}>
              <div className={styles.recipeSelect}>
                <label>Recipe A</label>
                <select 
                  value={recipeA?.id || ''} 
                  onChange={(e) => setRecipeA(recipes.find(r => String(r.id) === e.target.value))}
                >
                  <option value="">Select recipe...</option>
                  {recipes.map(r => (
                    <option key={r.id} value={r.id}>{r.name}</option>
                  ))}
                </select>
              </div>
              
              <div className={styles.ratioSlider}>
                <label>Blend Ratio: {Math.round(fusionRatio * 100)}% A / {Math.round((1-fusionRatio) * 100)}% B</label>
                <input 
                  type="range" 
                  min="0" 
                  max="1" 
                  step="0.1"
                  value={fusionRatio}
                  onChange={(e) => setFusionRatio(parseFloat(e.target.value))}
                />
              </div>
              
              <div className={styles.recipeSelect}>
                <label>Recipe B</label>
                <select 
                  value={recipeB?.id || ''} 
                  onChange={(e) => setRecipeB(recipes.find(r => String(r.id) === e.target.value))}
                >
                  <option value="">Select recipe...</option>
                  {recipes.map(r => (
                    <option key={r.id} value={r.id}>{r.name}</option>
                  ))}
                </select>
              </div>
            </div>
            
            <button 
              className={styles.actionBtn}
              onClick={handleFusion}
              disabled={loading || !recipeA || !recipeB}
            >
              {loading ? 'Fusing...' : (
                <>
                  <Sparkles size={18} />
                  Fuse Recipes
                </>
              )}
            </button>
            
            {fusedRecipe && (
              <RecipeCard recipe={fusedRecipe} title="🧬 Fusion Result" />
            )}
          </div>
        )}
        
        {/* RANDOM TAB */}
        {activeTab === 'random' && (
          <div className={styles.panel}>
            <div className={styles.formula}>
              <code>Recipe_Random = sample(ingredient_space) × method_matrix</code>
            </div>
            
            <div className={styles.randomInputs}>
              <div className={styles.inputGroup}>
                <label>Protein Preference (optional)</label>
                <select 
                  value={randomProtein} 
                  onChange={(e) => setRandomProtein(e.target.value)}
                >
                  <option value="">Any protein</option>
                  <option value="chicken">Chicken</option>
                  <option value="beef">Beef</option>
                  <option value="pork">Pork</option>
                  <option value="fish">Fish</option>
                  <option value="tofu">Tofu</option>
                  <option value="eggs">Eggs</option>
                </select>
              </div>
            </div>
            
            <button 
              className={styles.actionBtn}
              onClick={handleRandom}
              disabled={loading}
            >
              {loading ? 'Generating...' : (
                <>
                  <Shuffle size={18} />
                  Generate Random Recipe
                </>
              )}
            </button>
            
            {randomRecipe && (
              <RecipeCard recipe={randomRecipe} title="🎲 Random Recipe" />
            )}
          </div>
        )}
        
        {/* REMIX TAB */}
        {activeTab === 'remix' && (
          <div className={styles.panel}>
            <div className={styles.formula}>
              <code>Recipe_New = Recipe - old_ingredient + new_ingredient</code>
            </div>
            
            <div className={styles.remixInputs}>
              <div className={styles.recipeSelect}>
                <label>Base Recipe</label>
                <select 
                  value={remixRecipe?.id || ''} 
                  onChange={(e) => {
                    const recipe = recipes.find(r => String(r.id) === e.target.value)
                    setRemixRecipe(recipe)
                    setSwapIngredient('')
                  }}
                >
                  <option value="">Select recipe...</option>
                  {recipes.map(r => (
                    <option key={r.id} value={r.id}>{r.name}</option>
                  ))}
                </select>
              </div>
              
              {remixRecipe && (
                <div className={styles.swapInputs}>
                  <div className={styles.inputGroup}>
                    <label>Swap Out</label>
                    <input 
                      type="text"
                      placeholder="e.g., chicken"
                      value={swapIngredient}
                      onChange={(e) => setSwapIngredient(e.target.value)}
                      list="current-ingredients"
                    />
                    <datalist id="current-ingredients">
                      {remixRecipe.ingredients?.map((ing, i) => (
                        <option key={i} value={ing.split(' ').slice(-1)[0]} />
                      ))}
                    </datalist>
                  </div>
                  
                  <span className={styles.arrow}>→</span>
                  
                  <div className={styles.inputGroup}>
                    <label>Swap In</label>
                    <input 
                      type="text"
                      placeholder="e.g., tofu"
                      value={newIngredient}
                      onChange={(e) => setNewIngredient(e.target.value)}
                    />
                  </div>
                </div>
              )}
            </div>
            
            <button 
              className={styles.actionBtn}
              onClick={handleRemix}
              disabled={loading || !remixRecipe || !swapIngredient || !newIngredient}
            >
              {loading ? 'Remixing...' : (
                <>
                  <RefreshCw size={18} />
                  Remix Recipe
                </>
              )}
            </button>
            
            {remixedRecipe && (
              <RecipeCard recipe={remixedRecipe} title="🔄 Remixed Recipe" />
            )}
          </div>
        )}
        
        {/* SAVED TAB */}
        {activeTab === 'saved' && (
          <div className={styles.panel}>
            <div className={styles.formula}>
              <code>Your_Recipes = ∑ creative_experiments</code>
            </div>
            
            {savedRecipes.length === 0 ? (
              <div className={styles.emptyState}>
                <Sparkles size={48} className={styles.emptyIcon} />
                <p>No saved creative recipes yet!</p>
                <p className={styles.emptyHint}>
                  Create recipes using Fusion, Random, or Remix, then click "Save Recipe" to keep them here.
                </p>
              </div>
            ) : (
              <div className={styles.savedRecipesList}>
                {savedRecipes.map((recipe) => (
                  <div key={recipe.id} className={styles.savedRecipeCard}>
                    <div className={styles.savedRecipeHeader}>
                      <h4>{recipe.name}</h4>
                      <button
                        className={styles.deleteRecipeBtn}
                        onClick={() => {
                          const updated = savedRecipes.filter(r => r.id !== recipe.id)
                          setSavedRecipes(updated)
                          localStorage.setItem('creativeRecipes', JSON.stringify(updated))
                        }}
                      >
                        ✕
                      </button>
                    </div>
                    <p className={styles.savedRecipeDesc}>{recipe.description}</p>
                    <div className={styles.savedRecipeMeta}>
                      <span>⏱️ {recipe.total_time || 30} min</span>
                      <span>📅 {new Date(recipe.savedAt).toLocaleDateString()}</span>
                    </div>
                    <div className={styles.savedRecipeIngredients}>
                      {recipe.ingredients?.slice(0, 5).map((ing, i) => (
                        <span key={i} className={styles.ingredientPill}>{ing.split(' ').slice(-1)[0]}</span>
                      ))}
                      {recipe.ingredients?.length > 5 && (
                        <span className={styles.ingredientPill}>+{recipe.ingredients.length - 5}</span>
                      )}
                    </div>
                    <button
                      className={styles.reuseTemplateBtn}
                      onClick={() => {
                        // Go to remix with this as the base recipe
                        setRemixRecipe(recipe)
                        setActiveTab('remix')
                      }}
                    >
                      <RefreshCw size={14} /> Use as Template
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
      
      <footer className={styles.footer}>
        <p>
          <strong>How it works:</strong> Each recipe is represented as a vector in ingredient space. 
          Fusion adds vectors, random samples from the space, and remix performs vector arithmetic.
        </p>
      </footer>
    </div>
  )
}
