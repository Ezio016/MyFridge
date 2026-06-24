import { useState, useEffect } from 'react'
import { useLocation } from 'react-router-dom'
import { ShoppingCart, Plus, Trash2, Check, Minus } from 'lucide-react'
import { getCart, addToCart, removeFromCart, toggleChecked, clearCart, clearCheckedItems, updateQuantity } from '../utils/cartUtils'
import styles from './Cart.module.css'

function Cart() {
  const location = useLocation()
  const [items, setItems] = useState([])
  const [newItem, setNewItem] = useState('')

  // Load cart from localStorage
  const loadCart = () => {
    setItems(getCart())
  }

  // Load on mount and when navigating to this page
  useEffect(() => {
    loadCart()
  }, [location.pathname])

  const addItem = (e) => {
    e.preventDefault()
    if (!newItem.trim()) return
    
    addToCart(newItem.trim(), 1)
    setNewItem('')
    loadCart()
  }

  const toggleItem = (id) => {
    toggleChecked(id)
    loadCart()
  }

  const removeItem = (id) => {
    removeFromCart(id)
    loadCart()
  }

  const changeQuantity = (id, delta) => {
    const item = items.find(i => i.id === id)
    if (item) {
      const newQty = Math.max(1, (item.quantity || 1) + delta)
      updateQuantity(id, newQty)
      loadCart()
    }
  }

  const clearChecked = () => {
    clearCheckedItems()
    loadCart()
  }

  const clearAll = () => {
    if (confirm('Clear all items?')) {
      clearCart()
      loadCart()
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
                  
                  <div className={styles.quantityControls}>
                    <button 
                      className={styles.qtyBtn}
                      onClick={() => changeQuantity(item.id, -1)}
                    >
                      <Minus size={14} />
                    </button>
                    <span className={styles.quantity}>{item.quantity || 1}</span>
                    <button 
                      className={styles.qtyBtn}
                      onClick={() => changeQuantity(item.id, 1)}
                    >
                      <Plus size={14} />
                    </button>
                  </div>
                  
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
                      <span className={styles.itemName}>
                        {item.name} {item.quantity > 1 && `(x${item.quantity})`}
                      </span>
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
