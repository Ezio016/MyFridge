/**
 * API client for MyFridge backend
 */

// Use localhost for development, production URL for deployed version
const API_BASE = import.meta.env.VITE_API_URL || 
  (import.meta.env.DEV ? 'http://localhost:8000/api' : 'https://myfridge-di8a.onrender.com/api');

/**
 * Generic fetch wrapper with error handling
 */
async function fetchAPI(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  try {
    const response = await fetch(url, config);
    
    if (!response.ok) {
      let errorMessage = `HTTP ${response.status}`;
      try {
        const errorData = await response.json();
        console.error('API Error Response:', errorData);
        
        // Extract error message from various formats
        if (errorData.detail) {
          if (typeof errorData.detail === 'string') {
            errorMessage = errorData.detail;
          } else if (Array.isArray(errorData.detail)) {
            // FastAPI validation errors
            errorMessage = errorData.detail.map(e => `${e.loc?.join('.')}: ${e.msg}`).join(', ');
          } else {
            errorMessage = JSON.stringify(errorData.detail);
          }
        } else if (errorData.message) {
          errorMessage = errorData.message;
        } else if (errorData.error) {
          errorMessage = errorData.error;
        }
      } catch (e) {
        console.error('Could not parse error response:', e);
      }
      throw new Error(errorMessage);
    }
    
    // Handle 204 No Content
    if (response.status === 204) {
      return null;
    }
    
    return await response.json();
  } catch (error) {
    console.error(`API Error [${endpoint}]:`, error);
    throw error;
  }
}

// ============ Inventory API ============

export const inventoryAPI = {
  /**
   * Get all fridge items
   */
  getAll: () => fetchAPI('/inventory/'),

  /**
   * Get a single item by ID
   */
  getById: (id) => fetchAPI(`/inventory/${id}`),

  /**
   * Create a new item
   */
  create: (item) => fetchAPI('/inventory/', {
    method: 'POST',
    body: JSON.stringify(item),
  }),

  /**
   * Update an existing item
   */
  update: (id, updates) => fetchAPI(`/inventory/${id}`, {
    method: 'PUT',
    body: JSON.stringify(updates),
  }),

  /**
   * Delete an item
   */
  delete: (id) => fetchAPI(`/inventory/${id}`, {
    method: 'DELETE',
  }),

  /**
   * Get items expiring soon
   */
  getExpiring: (days = 3) => fetchAPI(`/inventory/expiring?days=${days}`),

  /**
   * Get expired items
   */
  getExpired: () => fetchAPI('/inventory/expired'),

  /**
   * Search items by name
   */
  search: (query) => fetchAPI(`/inventory/search?q=${encodeURIComponent(query)}`),

  /**
   * Get inventory summary
   */
  getSummary: () => fetchAPI('/inventory/summary'),

  /**
   * Parse voice input to items
   */
  parseVoice: (text) => fetchAPI('/inventory/parse-voice', {
    method: 'POST',
    body: JSON.stringify({ text }),
  }),
};

// ============ Chat API ============

export const chatAPI = {
  /**
   * Send a message to the recipe assistant
   */
  send: (message) => fetchAPI('/chat/', {
    method: 'POST',
    body: JSON.stringify({ message }),
  }),

  /**
   * Get meal plan for today
   */
  getMealPlan: () => fetchAPI('/chat/meal-plan'),

  /**
   * Get a quick recipe suggestion
   */
  getQuickRecipe: (mealType = 'any') => 
    fetchAPI(`/chat/quick-recipe?meal_type=${mealType}`),

  /**
   * Chef controls assistant: returns structured actions to update filter/sort/customization UI state
   */
  controls: (message, state = {}, facets = {}) => fetchAPI('/chat/controls', {
    method: 'POST',
    body: JSON.stringify({ message, state, facets }),
  }),

  /**
   * Customize a recipe based on modification request
   */
  customizeRecipe: (recipe, modificationRequest) => fetchAPI('/chat/customize-recipe', {
    method: 'POST',
    body: JSON.stringify({ recipe, modification_request: modificationRequest }),
  }),
};

// ============ Recipe API ============

export const recipeAPI = {
  /**
   * Get all recipes
   */
  getAll: () => fetchAPI('/recipes/'),

  /**
   * Get a recipe by ID
   */
  getById: (id) => fetchAPI(`/recipes/${id}`),

  /**
   * Get random recipes for exploration
   */
  getRandom: (count = 5) => fetchAPI(`/recipes/random?count=${count}`),

  /**
   * Get quick recipes (under specified time)
   */
  getQuick: (maxTime = 15, limit = 10) => 
    fetchAPI(`/recipes/quick?max_time=${maxTime}&limit=${limit}`),

  /**
   * Search recipes with filters
   */
  search: (filters) => fetchAPI('/recipes/search', {
    method: 'POST',
    body: JSON.stringify(filters),
  }),

  /**
   * Find recipes by ingredients
   */
  byIngredients: (ingredients, limit = 10) => fetchAPI('/recipes/by-ingredients', {
    method: 'POST',
    body: JSON.stringify({ ingredients, limit }),
  }),

  /**
   * Get recipes by tag
   */
  byTag: (tag, limit = 10) => fetchAPI(`/recipes/tags/${tag}?limit=${limit}`),
};

// ============ Health API ============

export const healthAPI = {
  /**
   * Check if API is healthy
   */
  check: () => fetchAPI('/health'),
};

// ============ Auth API ============

export const authAPI = {
  /**
   * Register a new user
   */
  register: (email, password, name) => fetchAPI('/auth/register', {
    method: 'POST',
    body: JSON.stringify({ email, password, name }),
  }),

  /**
   * Login with email and password
   */
  login: (email, password) => fetchAPI('/auth/login/json', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  }),

  /**
   * Get current user info
   */
  me: (token) => fetchAPI('/auth/me', {
    headers: { 'Authorization': `Bearer ${token}` },
  }),

  /**
   * Verify token
   */
  verify: (token) => fetchAPI('/auth/verify', {
    headers: { 'Authorization': `Bearer ${token}` },
  }),
};

// ============ User API ============

export const userAPI = {
  /**
   * Get user flavor profile
   */
  getFlavorProfile: (token) => fetchAPI('/user/flavor-profile', {
    headers: { 'Authorization': `Bearer ${token}` },
  }),

  /**
   * Log recipe interaction
   */
  logInteraction: (token, recipeId, interactionType) => fetchAPI('/user/interact', {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}` },
    body: JSON.stringify({ recipe_id: recipeId, interaction_type: interactionType }),
  }),

  /**
   * Get favorites
   */
  getFavorites: (token) => fetchAPI('/user/favorites', {
    headers: { 'Authorization': `Bearer ${token}` },
  }),

  /**
   * Add to favorites
   */
  addFavorite: (token, recipeId) => fetchAPI(`/user/favorites/${recipeId}`, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}` },
  }),

  /**
   * Remove from favorites
   */
  removeFavorite: (token, recipeId) => fetchAPI(`/user/favorites/${recipeId}`, {
    method: 'DELETE',
    headers: { 'Authorization': `Bearer ${token}` },
  }),

  /**
   * Get personalized recommendations
   */
  getRecommendations: (token, options = {}) => fetchAPI('/user/recommendations', {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}` },
    body: JSON.stringify(options),
  }),
};

