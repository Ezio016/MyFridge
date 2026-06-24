import { NavLink } from 'react-router-dom'
import { Package, ChefHat, ShoppingCart, Sparkles, Settings, Home } from 'lucide-react'
import styles from './Layout.module.css'

function Layout({ children }) {
  return (
    <div className={styles.layout}>
      {/* Settings/Profile button - top right */}
      <NavLink to="/profile" className={styles.profileBtn} title="Profile & Settings">
        <Settings size={20} />
      </NavLink>
      
      <main className={styles.main}>
        {children}
      </main>
      
      <nav className={styles.bottomNav}>
        <NavLink 
          to="/fridge" 
          className={({ isActive }) => 
            `${styles.navItem} ${isActive ? styles.active : ''}`
          }
        >
          <Package size={22} />
          <span>Inventory</span>
        </NavLink>
        
        <NavLink 
          to="/chef" 
          className={({ isActive }) => 
            `${styles.navItem} ${isActive ? styles.active : ''}`
          }
        >
          <ChefHat size={22} />
          <span>Explore Recipes</span>
        </NavLink>
        
        {/* Big Home Button in Center */}
        <NavLink 
          to="/" 
          className={({ isActive }) => 
            `${styles.navItem} ${styles.homeNav} ${isActive ? styles.active : ''}`
          }
        >
          <div className={styles.homeIcon}>
            <Home size={28} />
          </div>
          <span>Home</span>
        </NavLink>
        
        <NavLink 
          to="/yummytok" 
          className={({ isActive }) => 
            `${styles.navItem} ${isActive ? styles.active : ''}`
          }
        >
          <Sparkles size={22} />
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
