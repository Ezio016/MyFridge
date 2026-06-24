/**
 * Cart utility functions
 * Manages shopping cart with quantity support and no duplicates
 */

// Get cart from localStorage
export const getCart = () => {
  try {
    const saved = localStorage.getItem('cartItems')
    return saved ? JSON.parse(saved) : []
  } catch (e) {
    console.error('Error loading cart:', e)
    return []
  }
}

// Save cart to localStorage
export const saveCart = (items) => {
  try {
    localStorage.setItem('cartItems', JSON.stringify(items))
  } catch (e) {
    console.error('Error saving cart:', e)
  }
}

// Add item to cart (merges quantity if exists)
export const addToCart = (itemName, quantity = 1) => {
  const cart = getCart()
  const normalizedName = itemName.trim().toLowerCase()
  
  // Check if item already exists (case-insensitive)
  const existingIndex = cart.findIndex(
    item => item.name.toLowerCase() === normalizedName
  )
  
  if (existingIndex !== -1) {
    // Item exists - add to quantity
    cart[existingIndex].quantity = (cart[existingIndex].quantity || 1) + quantity
  } else {
    // New item
    cart.push({
      id: Date.now() + Math.random(), // Unique ID
      name: itemName.trim(),
      quantity: quantity,
      checked: false
    })
  }
  
  saveCart(cart)
  return cart
}

// Add multiple items to cart
export const addMultipleToCart = (items) => {
  let cart = getCart()
  
  items.forEach(item => {
    const itemName = typeof item === 'string' ? item : item.name
    const quantity = typeof item === 'object' ? (item.quantity || 1) : 1
    const normalizedName = itemName.trim().toLowerCase()
    
    // Check if item already exists
    const existingIndex = cart.findIndex(
      cartItem => cartItem.name.toLowerCase() === normalizedName
    )
    
    if (existingIndex !== -1) {
      // Add to existing quantity
      cart[existingIndex].quantity = (cart[existingIndex].quantity || 1) + quantity
    } else {
      // Add new item
      cart.push({
        id: Date.now() + Math.random() + Math.random(),
        name: itemName.trim(),
        quantity: quantity,
        checked: false
      })
    }
  })
  
  saveCart(cart)
  return cart
}

// Remove item from cart
export const removeFromCart = (itemId) => {
  const cart = getCart()
  const filtered = cart.filter(item => item.id !== itemId)
  saveCart(filtered)
  return filtered
}

// Update item quantity
export const updateQuantity = (itemId, newQuantity) => {
  const cart = getCart()
  const updated = cart.map(item => 
    item.id === itemId ? { ...item, quantity: Math.max(1, newQuantity) } : item
  )
  saveCart(updated)
  return updated
}

// Toggle checked status
export const toggleChecked = (itemId) => {
  const cart = getCart()
  const updated = cart.map(item =>
    item.id === itemId ? { ...item, checked: !item.checked } : item
  )
  saveCart(updated)
  return updated
}

// Clear all items
export const clearCart = () => {
  saveCart([])
  return []
}

// Clear checked items
export const clearCheckedItems = () => {
  const cart = getCart()
  const filtered = cart.filter(item => !item.checked)
  saveCart(filtered)
  return filtered
}

