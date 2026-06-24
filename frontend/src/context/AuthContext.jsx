import { createContext, useContext, useState, useEffect } from 'react'

const API_BASE = import.meta.env.VITE_API_URL || 
  (import.meta.env.DEV ? 'http://localhost:8000' : 'https://myfridge-di8a.onrender.com')

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [token, setToken] = useState(() => localStorage.getItem('auth_token'))
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (token) {
      verifyToken()
    } else {
      setLoading(false)
    }
  }, [])

  const verifyToken = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/auth/me`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (res.ok) {
        const userData = await res.json()
        setUser(userData)
      } else {
        logout()
      }
    } catch (err) {
      console.error('Token verification failed:', err)
      logout()
    } finally {
      setLoading(false)
    }
  }

  const login = async (email, password) => {
    const res = await fetch(`${API_BASE}/api/auth/login/json`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    })

    if (!res.ok) {
      const error = await res.json()
      throw new Error(error.detail || 'Login failed')
    }

    const data = await res.json()
    setToken(data.access_token)
    setUser(data.user)
    localStorage.setItem('auth_token', data.access_token)
    return data
  }

  const register = async (email, password, name) => {
    const res = await fetch(`${API_BASE}/api/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password, name })
    })

    if (!res.ok) {
      const error = await res.json()
      throw new Error(error.detail || 'Registration failed')
    }

    const data = await res.json()
    setToken(data.access_token)
    setUser(data.user)
    localStorage.setItem('auth_token', data.access_token)
    return data
  }

  const logout = () => {
    setToken(null)
    setUser(null)
    localStorage.removeItem('auth_token')
  }

  const authFetch = async (endpoint, options = {}) => {
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers,
    }
    
    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }

    const res = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers,
    })

    if (res.status === 401) {
      logout()
      throw new Error('Session expired')
    }

    return res
  }

  const value = {
    user,
    token,
    loading,
    isAuthenticated: !!user,
    login,
    register,
    logout,
    authFetch,
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export default AuthContext
