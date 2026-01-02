import { useState, useEffect } from 'react'
import { X, Plus, Save, Refrigerator, Snowflake, Package } from 'lucide-react'
import VoiceInput from './VoiceInput'
import styles from './AddItemForm.module.css'

const LOCATIONS = [
  { value: 'fridge', label: 'Fridge', icon: Refrigerator },
  { value: 'freezer', label: 'Freezer', icon: Snowflake },
  { value: 'pantry', label: 'Pantry', icon: Package },
]

const CATEGORIES = [
  { value: 'dairy', label: '🥛 Dairy' },
  { value: 'meat', label: '🥩 Meat' },
  { value: 'seafood', label: '🐟 Seafood' },
  { value: 'vegetable', label: '🥬 Vegetable' },
  { value: 'fruit', label: '🍎 Fruit' },
  { value: 'grain', label: '🍞 Grain' },
  { value: 'beverage', label: '🥤 Beverage' },
  { value: 'condiment', label: '🧂 Condiment' },
  { value: 'snack', label: '🍿 Snack' },
  { value: 'leftover', label: '🍱 Leftover' },
  { value: 'other', label: '📦 Other' },
]

const UNITS = [
  // Count
  { value: 'pieces', label: 'pieces' },
  { value: 'items', label: 'items' },
  { value: 'dozen', label: 'dozen' },
  // Weight
  { value: 'g', label: 'grams (g)' },
  { value: 'kg', label: 'kilograms (kg)' },
  { value: 'oz', label: 'ounces (oz)' },
  { value: 'lb', label: 'pounds (lb)' },
  // Volume
  { value: 'ml', label: 'milliliters (ml)' },
  { value: 'L', label: 'liters (L)' },
  { value: 'cups', label: 'cups' },
  { value: 'tbsp', label: 'tablespoons' },
  { value: 'tsp', label: 'teaspoons' },
  { value: 'fl oz', label: 'fluid ounces' },
  // Containers
  { value: 'packs', label: 'packs' },
  { value: 'boxes', label: 'boxes' },
  { value: 'cans', label: 'cans' },
  { value: 'bottles', label: 'bottles' },
  { value: 'bags', label: 'bags' },
  { value: 'jars', label: 'jars' },
  { value: 'cartons', label: 'cartons' },
  { value: 'bunches', label: 'bunches' },
  { value: 'slices', label: 'slices' },
  { value: 'loaves', label: 'loaves' },
]

function AddItemForm({ onSubmit, onClose, editItem = null }) {
  const isEditing = !!editItem
  
  const [formData, setFormData] = useState({
    name: '',
    quantity: 1,
    unit: 'pieces',
    location: 'fridge',
    category: 'other',
    expiration_date: '',
    notes: '',
  })
  const [loading, setLoading] = useState(false)
  const [useVoice, setUseVoice] = useState(false)

  // Populate form if editing
  useEffect(() => {
    if (editItem) {
      setFormData({
        name: editItem.name || '',
        quantity: editItem.quantity || 1,
        unit: editItem.unit || 'pieces',
        location: editItem.location || 'fridge',
        category: editItem.category || 'other',
        expiration_date: editItem.expiration_date || '',
        notes: editItem.notes || '',
      })
    }
  }, [editItem])

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: name === 'quantity' ? parseFloat(value) || 0 : value,
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!formData.name.trim()) return

    setLoading(true)
    try {
      await onSubmit({
        ...formData,
        expiration_date: formData.expiration_date || null,
        notes: formData.notes || null,
      }, editItem?.id)
      onClose()
    } catch (err) {
      console.error('Failed to save item:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleVoiceItems = async (items) => {
    if (!items || items.length === 0) {
      alert('No items detected. Please try again!')
      return
    }

    setLoading(true)
    try {
      // Add each item parsed from voice
      for (const item of items) {
        await onSubmit(item)
      }
      alert(`✅ Added ${items.length} item(s) to your fridge!`)
      onClose()
    } catch (err) {
      console.error('Failed to add items:', err)
      alert('Failed to add some items. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className={styles.overlay} onClick={onClose}>
      <div className={styles.modal} onClick={e => e.stopPropagation()}>
        <div className={styles.header}>
          <h2>{isEditing ? 'Edit Item' : 'Add Item'}</h2>
          <button className={styles.closeBtn} onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        {!isEditing && (
          <div className={styles.inputMethod}>
            <button
              type="button"
              className={`${styles.methodBtn} ${!useVoice ? styles.active : ''}`}
              onClick={() => setUseVoice(false)}
            >
              ⌨️ Type
            </button>
            <button
              type="button"
              className={`${styles.methodBtn} ${useVoice ? styles.active : ''}`}
              onClick={() => setUseVoice(true)}
            >
              🎤 Voice
            </button>
          </div>
        )}

        {useVoice && !isEditing ? (
          <div className={styles.voiceSection}>
            <VoiceInput onItemsParsed={handleVoiceItems} />
            <p className={styles.voiceHint}>
              💡 Try saying: "I have 2 apples and a carton of milk expiring in 5 days"
            </p>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className={styles.form}>
          <div className={styles.field}>
            <label htmlFor="name">Item Name *</label>
            <input
              type="text"
              id="name"
              name="name"
              value={formData.name}
              onChange={handleChange}
              placeholder="e.g., Milk, Eggs, Chicken..."
              autoFocus={!isEditing}
              required
            />
          </div>

          <div className={styles.row}>
            <div className={styles.field}>
              <label htmlFor="quantity">Quantity</label>
              <input
                type="number"
                id="quantity"
                name="quantity"
                value={formData.quantity}
                onChange={handleChange}
                min="0.1"
                step="0.1"
              />
            </div>
            <div className={styles.field}>
              <label htmlFor="unit">Unit</label>
              <select
                id="unit"
                name="unit"
                value={formData.unit}
                onChange={handleChange}
              >
                {UNITS.map(u => (
                  <option key={u.value} value={u.value}>{u.label}</option>
                ))}
              </select>
            </div>
          </div>

          <div className={styles.field}>
            <label>Storage Location</label>
            <div className={styles.locationPicker}>
              {LOCATIONS.map(loc => (
                <button
                  key={loc.value}
                  type="button"
                  className={`${styles.locationBtn} ${formData.location === loc.value ? styles.active : ''}`}
                  onClick={() => setFormData(prev => ({ ...prev, location: loc.value }))}
                >
                  <loc.icon size={18} />
                  <span>{loc.label}</span>
                </button>
              ))}
            </div>
          </div>

          <div className={styles.field}>
            <label htmlFor="category">Category</label>
            <select
              id="category"
              name="category"
              value={formData.category}
              onChange={handleChange}
            >
              {CATEGORIES.map(cat => (
                <option key={cat.value} value={cat.value}>{cat.label}</option>
              ))}
            </select>
          </div>

          <div className={styles.field}>
            <label htmlFor="expiration_date">Expiration Date</label>
            <input
              type="date"
              id="expiration_date"
              name="expiration_date"
              value={formData.expiration_date}
              onChange={handleChange}
            />
          </div>

          <div className={styles.field}>
            <label htmlFor="notes">Notes (optional)</label>
            <input
              type="text"
              id="notes"
              name="notes"
              value={formData.notes}
              onChange={handleChange}
              placeholder="e.g., Opened, Half-used..."
            />
          </div>

          <div className={styles.actions}>
            <button type="button" className="btn btn-secondary" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {isEditing ? <Save size={18} /> : <Plus size={18} />}
              {loading ? 'Saving...' : (isEditing ? 'Save Changes' : 'Add Item')}
            </button>
          </div>
        </form>
        )}
      </div>
    </div>
  )
}

export default AddItemForm
