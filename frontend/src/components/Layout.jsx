import { NavLink } from 'react-router-dom'
import { Refrigerator, ChefHat, ShoppingCart, Sparkles, User } from 'lucide-react'
import styles from './Layout.module.css'

function Layout({ children }) {
  return (
    <div className={styles.layout}>
      {/* Profile button - top right */}
      <NavLink to="/profile" className={styles.profileBtn}>
        <User size={20} />
      </NavLink>
      
      <main className={styles.main}>
        {children}
      </main>
      
      <nav className={styles.bottomNav}>
        <NavLink 
          to="/" 
          className={({ isActive }) => 
            `${styles.navItem} ${isActive ? styles.active : ''}`
          }
        >
          <Refrigerator size={22} />
          <span>Fridge</span>
        </NavLink>
        
        <NavLink 
          to="/chef" 
          className={({ isActive }) => 
            `${styles.navItem} ${isActive ? styles.active : ''}`
          }
        >
          <ChefHat size={22} />
          <span>Chef</span>
        </NavLink>
        
        <NavLink 
          to="/yummytok" 
          className={({ isActive }) => 
            `${styles.navItem} ${styles.yummyNav} ${isActive ? styles.active : ''}`
          }
        >
          <div className={styles.yummyIcon}>
            <Sparkles size={24} />
          </div>
          <span>YummyTok</span>
        </NavLink>
        
        <NavLink 
          to="/cart" 
          className={({ isActive }) => 
            `${styles.navItem} ${isActive ? styles.active : ''}`
          }
        >
          <ShoppingCart size={22} />
          <span>Cart</span>
        </NavLink>
      </nav>
    </div>
  )
}

export default Layout
