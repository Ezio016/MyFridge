import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { ArrowLeft, Mail, Lock, User, Eye, EyeOff } from 'lucide-react'
import styles from './Login.module.css'

export default function Login() {
  const [isRegister, setIsRegister] = useState(false)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [name, setName] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  
  const { login, register } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      if (isRegister) {
        await register(email, password, name || undefined)
      } else {
        await login(email, password)
      }
      navigate('/chef')
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className={styles.container}>
      <Link to="/" className={styles.backLink}>
        <ArrowLeft size={20} />
        Back to Home
      </Link>

      <div className={styles.card}>
        <div className={styles.header}>
          <h1>{isRegister ? 'Create Account' : 'Welcome Back'}</h1>
          <p>
            {isRegister 
              ? 'Start your personalized cooking journey'
              : 'Sign in to access your flavor profile'}
          </p>
        </div>

        <form onSubmit={handleSubmit} className={styles.form}>
          {isRegister && (
            <div className={styles.inputGroup}>
              <label htmlFor="name">
                <User size={18} />
                Name (optional)
              </label>
              <input
                type="text"
                id="name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Your name"
              />
            </div>
          )}

          <div className={styles.inputGroup}>
            <label htmlFor="email">
              <Mail size={18} />
              Email
            </label>
            <input
              type="email"
              id="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              required
            />
          </div>

          <div className={styles.inputGroup}>
            <label htmlFor="password">
              <Lock size={18} />
              Password
            </label>
            <div className={styles.passwordInput}>
              <input
                type={showPassword ? 'text' : 'password'}
                id="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Min 6 characters"
                minLength={6}
                required
              />
              <button
                type="button"
                className={styles.togglePassword}
                onClick={() => setShowPassword(!showPassword)}
              >
                {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>
          </div>

          {error && (
            <div className={styles.error}>
              {error}
            </div>
          )}

          <button
            type="submit"
            className={styles.submitBtn}
            disabled={loading}
          >
            {loading 
              ? 'Please wait...' 
              : (isRegister ? 'Create Account' : 'Sign In')}
          </button>
        </form>

        <div className={styles.footer}>
          <p>
            {isRegister ? 'Already have an account?' : "Don't have an account?"}
            <button
              type="button"
              className={styles.switchBtn}
              onClick={() => {
                setIsRegister(!isRegister)
                setError('')
              }}
            >
              {isRegister ? 'Sign In' : 'Sign Up'}
            </button>
          </p>
        </div>

        <div className={styles.guestSection}>
          <span className={styles.divider}>or</span>
          <button
            type="button"
            className={styles.guestBtn}
            onClick={() => navigate('/chef')}
          >
            Continue as Guest
          </button>
          <p className={styles.guestNote}>
            Your flavor profile won't be saved
          </p>
        </div>
      </div>

      <div className={styles.features}>
        <h3>Why create an account?</h3>
        <ul>
          <li>Save your personalized flavor profile</li>
          <li>Get AI-powered recipe recommendations</li>
          <li>Track your cooking history</li>
          <li>Sync favorites across devices</li>
        </ul>
      </div>
    </div>
  )
}
