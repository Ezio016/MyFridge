/**
 * API client for MyFridge backend
 */

const API_BASE = 'https://myfridge-di8a.onrender.com/api';

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
   * Send a message to AI Chef
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

