import { useState, useEffect, useCallback } from 'react'
import { useLocation } from 'react-router-dom'
import { ShoppingCart, Plus, Trash2, Check } from 'lucide-react'
import styles from './Cart.module.css'

// Helper to get cart from localStorage
const getCartFromStorage = () => {
  try {
    const saved = localStorage.getItem('cartItems')
    return saved ? JSON.parse(saved) : []
  } catch (e) {
    return []
  }
}

function Cart() {
  const location = useLocation()
  const [items, setItems] = useState([])
  const [newItem, setNewItem] = useState('')
  const [isLoaded, setIsLoaded] = useState(false)

  // Load from localStorage on every navigation to this page
  useEffect(() => {
    const loaded = getCartFromStorage()
    setItems(loaded)
    setIsLoaded(true)
  }, [location.pathname])

  // Save to localStorage whenever items change (only after initial load)
  useEffect(() => {
    if (isLoaded) {
      localStorage.setItem('cartItems', JSON.stringify(items))
    }
  }, [items, isLoaded])

  const addItem = (e) => {
    e.preventDefault()
    if (!newItem.trim()) return
    
    setItems(prev => [...prev, { id: Date.now(), name: newItem.trim(), checked: false }])
    setNewItem('')
  }

  const toggleItem = (id) => {
    setItems(prev => prev.map(item => 
      item.id === id ? { ...item, checked: !item.checked } : item
    ))
  }

  const removeItem = (id) => {
    setItems(prev => prev.filter(item => item.id !== id))
  }

  const clearChecked = () => {
    setItems(prev => prev.filter(item => !item.checked))
  }

  const clearAll = () => {
    if (confirm('Clear all items?')) {
      setItems([])
    }
  }

  const uncheckedCount = items.filter(i => !i.checked).length
  const checkedCount = items.filter(i => i.checked).length

  return (
    <div className={styles.page}>
      <div className="container">
        <header className={styles.header}>
          <div className={styles.iconWrap}>
            <ShoppingCart size={28} />
          </div>
          <div>
            <h1>Shopping Cart</h1>
            <p>{uncheckedCount} items to buy</p>
          </div>
          {items.length > 0 && (
            <button className={styles.clearAllBtn} onClick={clearAll}>
              Clear All
            </button>
          )}
        </header>

        <form onSubmit={addItem} className={styles.addForm}>
          <input
            type="text"
            value={newItem}
            onChange={(e) => setNewItem(e.target.value)}
            placeholder="Add item to cart..."
          />
          <button type="submit" className={styles.addBtn}>
            <Plus size={24} />
          </button>
        </form>

        {items.length === 0 ? (
          <div className={styles.empty}>
            <ShoppingCart size={48} />
            <p>Your cart is empty</p>
            <span>Add items you need to buy!</span>
          </div>
        ) : (
          <>
            <div className={styles.list}>
              {items.filter(i => !i.checked).map(item => (
                <div key={item.id} className={styles.item}>
                  <button 
                    className={styles.checkbox}
                    onClick={() => toggleItem(item.id)}
                  >
                    <div className={styles.checkCircle} />
                  </button>
                  <span className={styles.itemName}>{item.name}</span>
                  <button 
                    className={styles.deleteBtn}
                    onClick={() => removeItem(item.id)}
                  >
                    <Trash2 size={18} />
                  </button>
                </div>
              ))}
            </div>

            {checkedCount > 0 && (
              <div className={styles.checkedSection}>
                <div className={styles.checkedHeader}>
                  <span>Bought ({checkedCount})</span>
                  <button onClick={clearChecked}>Clear bought</button>
                </div>
                <div className={styles.list}>
                  {items.filter(i => i.checked).map(item => (
                    <div key={item.id} className={`${styles.item} ${styles.checked}`}>
                      <button 
                        className={styles.checkbox}
                        onClick={() => toggleItem(item.id)}
                      >
                        <div className={styles.checkCircle}>
                          <Check size={14} />
                        </div>
                      </button>
                      <span className={styles.itemName}>{item.name}</span>
                      <button 
                        className={styles.deleteBtn}
                        onClick={() => removeItem(item.id)}
                      >
                        <Trash2 size={18} />
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}

export default Cart
