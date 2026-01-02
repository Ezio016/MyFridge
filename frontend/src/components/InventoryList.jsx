import { Trash2, Pencil, Refrigerator, Snowflake, Package } from 'lucide-react'
import styles from './InventoryList.module.css'

const LOCATION_ICONS = {
  fridge: Refrigerator,
  freezer: Snowflake,
  pantry: Package,
}

const CATEGORY_EMOJIS = {
  dairy: '🥛',
  meat: '🥩',
  seafood: '🐟',
  vegetable: '🥬',
  fruit: '🍎',
  grain: '🍞',
  beverage: '🥤',
  condiment: '🧂',
  snack: '🍿',
  leftover: '🍱',
  other: '📦',
}

function InventoryList({ items, onDelete, onEdit, loading }) {
  if (loading) {
    return (
      <div className={styles.loading}>
        <div className={styles.spinner}></div>
        <p>Loading...</p>
      </div>
    )
  }

  if (!items || items.length === 0) {
    return (
      <div className={styles.empty}>
        <Refrigerator size={48} />
        <h3>Fridge is empty!</h3>
        <p>Tap + to add items</p>
      </div>
    )
  }

  // Sort: expired first, then expiring soon, then fresh
  const sortedItems = [...items].sort((a, b) => {
    const order = { expired: 0, expiring_soon: 1, fresh: 2, unknown: 3 }
    return (order[a.expiry_status] || 3) - (order[b.expiry_status] || 3)
  })

  return (
    <div className={styles.grid}>
      {sortedItems.map((item, idx) => (
        <ItemCard 
          key={item.id} 
          item={item} 
          onDelete={onDelete}
          onEdit={onEdit}
          style={{ animationDelay: `${idx * 0.05}s` }}
        />
      ))}
    </div>
  )
}

function ItemCard({ item, onDelete, onEdit, style }) {
  const LocationIcon = LOCATION_ICONS[item.location] || Package
  const emoji = CATEGORY_EMOJIS[item.category] || '📦'
  
  const getStatusClass = () => {
    if (item.expiry_status === 'expired') return styles.expired
    if (item.expiry_status === 'expiring_soon') return styles.expiring
    return ''
  }

  const getStatusText = () => {
    if (item.expiry_status === 'expired') return 'Expired'
    if (item.expiry_status === 'expiring_soon') {
      const days = item.days_until_expiry
      return days === 0 ? 'Today!' : days === 1 ? '1 day' : `${days} days`
    }
    if (item.days_until_expiry !== null) {
      return `${item.days_until_expiry}d`
    }
    return null
  }

  const handleCardClick = (e) => {
    // Don't trigger edit if clicking delete button
    if (e.target.closest(`.${styles.deleteBtn}`)) return
    onEdit(item)
  }

  return (
    <div 
      className={`${styles.card} ${getStatusClass()}`} 
      style={style}
      onClick={handleCardClick}
    >
      <div className={styles.cardTop}>
        <span className={styles.emoji}>{emoji}</span>
        <div className={styles.actions}>
          <div className={styles.location}>
            <LocationIcon size={14} />
          </div>
        </div>
      </div>
      
      <h4 className={styles.name}>{item.name}</h4>
      <p className={styles.qty}>{item.quantity} {item.unit}</p>
      
      <div className={styles.cardBottom}>
        {getStatusText() && (
          <span className={`${styles.status} ${getStatusClass()}`}>
            {getStatusText()}
          </span>
        )}
        <div className={styles.cardActions}>
          <button 
            className={styles.editBtn}
            onClick={(e) => { e.stopPropagation(); onEdit(item); }}
            title="Edit item"
          >
            <Pencil size={14} />
          </button>
          <button 
            className={styles.deleteBtn}
            onClick={(e) => { e.stopPropagation(); onDelete(item.id); }}
            title="Delete item"
          >
            <Trash2 size={14} />
          </button>
        </div>
      </div>
    </div>
  )
}

export default InventoryList
