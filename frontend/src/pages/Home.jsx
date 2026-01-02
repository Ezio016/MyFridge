import { useState, useEffect } from 'react'
import { Plus, Refrigerator, AlertTriangle } from 'lucide-react'
import { inventoryAPI } from '../api/client'
import InventoryList from '../components/InventoryList'
import AddItemForm from '../components/AddItemForm'
import styles from './Home.module.css'

function Home() {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [showForm, setShowForm] = useState(false)
  const [editingItem, setEditingItem] = useState(null)

  const fetchItems = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await inventoryAPI.getAll()
      setItems(data)
    } catch (err) {
      setError('Cannot connect to server')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchItems()
  }, [])

  const handleAddItem = async (itemData) => {
    const newItem = await inventoryAPI.create(itemData)
    setItems(prev => [newItem, ...prev])
  }

  const handleEditItem = async (itemData, itemId) => {
    const updatedItem = await inventoryAPI.update(itemId, itemData)
    setItems(prev => prev.map(item => 
      item.id === itemId ? updatedItem : item
    ))
  }

  const handleSaveItem = async (itemData, itemId) => {
    if (itemId) {
      await handleEditItem(itemData, itemId)
    } else {
      await handleAddItem(itemData)
    }
  }

  const handleDeleteItem = async (id) => {
    await inventoryAPI.delete(id)
    setItems(prev => prev.filter(item => item.id !== id))
  }

  const openAddForm = () => {
    setEditingItem(null)
    setShowForm(true)
  }

  const openEditForm = (item) => {
    setEditingItem(item)
    setShowForm(true)
  }

  const closeForm = () => {
    setShowForm(false)
    setEditingItem(null)
  }

  // Count items by status
  const expiringCount = items.filter(i => i.expiry_status === 'expiring_soon').length
  const expiredCount = items.filter(i => i.expiry_status === 'expired').length

  return (
    <div className={styles.page}>
      <div className="container">
        <header className={styles.header}>
          <div className={styles.iconWrap}>
            <Refrigerator size={28} />
          </div>
          <div>
            <h1>My Fridge</h1>
            <p>
              {items.length} items
              {expiringCount > 0 && <span className={styles.warning}> · {expiringCount} expiring</span>}
              {expiredCount > 0 && <span className={styles.danger}> · {expiredCount} expired</span>}
            </p>
          </div>
        </header>

        {error && (
          <div className={styles.errorBanner}>
            <AlertTriangle size={18} />
            <span>{error}</span>
          </div>
        )}

        <button 
          className={styles.addButton}
          onClick={openAddForm}
        >
          <Plus size={24} />
          <span>Add Item</span>
        </button>

        <InventoryList 
          items={items} 
          onDelete={handleDeleteItem}
          onEdit={openEditForm}
          loading={loading}
        />
      </div>

      {showForm && (
        <AddItemForm 
          onSubmit={handleSaveItem}
          onClose={closeForm}
          editItem={editingItem}
        />
      )}
    </div>
  )
}

export default Home
