import { Package, ChefHat, Video, ShoppingCart, FlaskConical, LogIn, User } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import styles from './Landing.module.css'

function Landing() {
  const navigate = useNavigate()
  const { user, isAuthenticated, logout } = useAuth()

  const features = [
    {
      icon: Package,
      title: 'Inventory',
      description: 'Manage your inventory with voice input',
      color: '#3b82f6',
      path: '/fridge',
      emoji: '📦'
    },
    {
      icon: ChefHat,
      title: 'Explore Recipes',
      description: 'Get personalized recipes & cooking guides',
      color: '#e87f4a',
      path: '/chef',
      emoji: '👨‍🍳'
    },
    {
      icon: Video,
      title: 'YummyTok',
      description: 'Swipe through recipe videos',
      color: '#8b5cf6',
      path: '/yummytok',
      emoji: '🎬'
    },
    {
      icon: ShoppingCart,
      title: 'Shopping',
      description: 'Plan your grocery trips',
      color: '#22c55e',
      path: '/cart',
      emoji: '🛒'
    },
    {
      icon: FlaskConical,
      title: 'Creative Meals',
      description: 'Fuse, remix & generate recipes',
      color: '#e91e63',
      path: '/lab',
      emoji: '✨'
    }
  ]

  return (
    <div className={styles.page}>
      <div className={styles.authHeader}>
        {isAuthenticated ? (
          <div className={styles.userMenu}>
            <span className={styles.userName}>
              <User size={16} />
              {user?.name || user?.email?.split('@')[0]}
            </span>
            <button onClick={logout} className={styles.authBtn}>
              Sign Out
            </button>
          </div>
        ) : (
          <button onClick={() => navigate('/login')} className={styles.authBtn}>
            <LogIn size={16} />
            Sign In
          </button>
        )}
      </div>
      
      <div className={styles.hero}>
        <div className={styles.logo}>
          <img className={styles.logoIcon} src="/fridge.svg" alt="" aria-hidden="true" />
          <h1>MyFridge</h1>
        </div>
        <p className={styles.tagline}>
          Your AI-powered kitchen companion
        </p>
      </div>

      <div className={styles.grid}>
        {features.map((feature) => (
          <button
            key={feature.path}
            className={styles.featureCard}
            onClick={() => navigate(feature.path)}
            style={{ '--feature-color': feature.color }}
          >
            <div className={styles.cardIcon}>
              <span className={styles.cardEmoji}>{feature.emoji}</span>
            </div>
            <h2>{feature.title}</h2>
            <p>{feature.description}</p>
            <div className={styles.cardArrow}>→</div>
          </button>
        ))}
      </div>

      <footer className={styles.footer}>
        <p>Made with ❤️ for students who want to cook smarter</p>
      </footer>
    </div>
  )
}

export default Landing

