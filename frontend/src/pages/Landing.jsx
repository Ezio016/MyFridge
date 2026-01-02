import { Refrigerator, ChefHat, Video, ShoppingCart } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import styles from './Landing.module.css'

function Landing() {
  const navigate = useNavigate()

  const features = [
    {
      icon: Refrigerator,
      title: 'My Fridge',
      description: 'Manage your inventory with voice input',
      color: '#3b82f6',
      path: '/fridge',
      emoji: '🧊'
    },
    {
      icon: ChefHat,
      title: 'AI Chef',
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
    }
  ]

  return (
    <div className={styles.page}>
      <div className={styles.hero}>
        <div className={styles.logo}>
          <span className={styles.logoEmoji}>🧊</span>
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

