import { useState, useEffect, useRef } from 'react'
import { X, Plus, Save, Refrigerator, Snowflake, Package, ChevronDown } from 'lucide-react'
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
  
  // Autocomplete state
  const defaultUnit = UNITS.find(u => u.value === 'pieces')
  const [unitSearch, setUnitSearch] = useState(defaultUnit?.label || '')
  const [showUnitDropdown, setShowUnitDropdown] = useState(false)
  const [filteredUnits, setFilteredUnits] = useState(UNITS)
  const [selectedUnitIndex, setSelectedUnitIndex] = useState(0)
  const unitInputRef = useRef(null)
  const unitDropdownRef = useRef(null)

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
      // Set unit search to show current unit label
      const currentUnit = UNITS.find(u => u.value === (editItem.unit || 'pieces'))
      setUnitSearch(currentUnit?.label || '')
    }
  }, [editItem])

  // Filter units based on search
  useEffect(() => {
    if (unitSearch.trim()) {
      const query = unitSearch.toLowerCase()
      const filtered = UNITS.filter(unit => 
        unit.label.toLowerCase().includes(query) ||
        unit.value.toLowerCase().includes(query)
      )
      setFilteredUnits(filtered)
      setSelectedUnitIndex(0)
    } else {
      setFilteredUnits(UNITS)
      setSelectedUnitIndex(0)
    }
  }, [unitSearch])

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (unitDropdownRef.current && !unitDropdownRef.current.contains(e.target) &&
          unitInputRef.current && !unitInputRef.current.contains(e.target)) {
        setShowUnitDropdown(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

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
    console.log('Submitting items:', items)
    
    if (!items || items.length === 0) {
      alert('❌ No items to add!')
      return
    }

    setLoading(true)
    try {
      // Add each item parsed from voice
      for (const item of items) {
        await onSubmit(item)
      }
      alert(`✅ Success! Added ${items.length} item(s) to your fridge!`)
      onClose()
    } catch (err) {
      console.error('Failed to add items:', err)
      alert('❌ Failed to add some items. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  // Handle unit search input
  const handleUnitSearchChange = (e) => {
    setUnitSearch(e.target.value)
    setShowUnitDropdown(true)
  }

  // Handle unit selection
  const handleUnitSelect = (unit) => {
    setFormData(prev => ({ ...prev, unit: unit.value }))
    setUnitSearch(unit.label)
    setShowUnitDropdown(false)
    setSelectedUnitIndex(0)
  }

  // Handle keyboard navigation in unit dropdown
  const handleUnitKeyDown = (e) => {
    if (!showUnitDropdown) {
      if (e.key === 'ArrowDown' || e.key === 'Enter') {
        setShowUnitDropdown(true)
        e.preventDefault()
      }
      return
    }

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault()
        setSelectedUnitIndex(prev => 
          prev < filteredUnits.length - 1 ? prev + 1 : prev
        )
        break
      case 'ArrowUp':
        e.preventDefault()
        setSelectedUnitIndex(prev => prev > 0 ? prev - 1 : prev)
        break
      case 'Enter':
        e.preventDefault()
        if (filteredUnits[selectedUnitIndex]) {
          handleUnitSelect(filteredUnits[selectedUnitIndex])
        }
        break
      case 'Escape':
        setShowUnitDropdown(false)
        break
      default:
        break
    }
  }

  // Scroll selected item into view
  useEffect(() => {
    if (showUnitDropdown && unitDropdownRef.current) {
      const selectedElement = unitDropdownRef.current.querySelector(`.${styles.selected}`)
      if (selectedElement) {
        selectedElement.scrollIntoView({ block: 'nearest', behavior: 'smooth' })
      }
    }
  }, [selectedUnitIndex, showUnitDropdown])

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
              <div className={styles.autocompleteWrapper}>
                <input
                  ref={unitInputRef}
                  type="text"
                id="unit"
                  className={styles.autocompleteInput}
                  value={unitSearch}
                  onChange={handleUnitSearchChange}
                  onFocus={() => setShowUnitDropdown(true)}
                  onKeyDown={handleUnitKeyDown}
                  placeholder="Type to search units..."
                  autoComplete="off"
                />
                <ChevronDown 
                  size={16} 
                  className={styles.dropdownIcon}
                  onClick={() => setShowUnitDropdown(!showUnitDropdown)}
                />
                {showUnitDropdown && (
                  <div ref={unitDropdownRef} className={styles.autocompleteDropdown}>
                    {filteredUnits.length > 0 ? (
                      filteredUnits.map((unit, index) => (
                        <div
                          key={unit.value}
                          className={`${styles.autocompleteOption} ${
                            index === selectedUnitIndex ? styles.selected : ''
                          } ${formData.unit === unit.value ? styles.active : ''}`}
                          onClick={() => handleUnitSelect(unit)}
                          onMouseEnter={() => setSelectedUnitIndex(index)}
                        >
                          {unit.label}
                        </div>
                      ))
                    ) : (
                      <div className={styles.autocompleteEmpty}>
                        No units found
                      </div>
                    )}
                  </div>
                )}
              </div>
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
