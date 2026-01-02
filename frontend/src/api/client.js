/**
 * API client for MyFridge backend
 */

const API_BASE = '/api';

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
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || `HTTP ${response.status}`);
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

// ============ Health API ============

export const healthAPI = {
  /**
   * Check if API is healthy
   */
  check: () => fetchAPI('/health'),
};

