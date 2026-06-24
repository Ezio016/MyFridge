const PROD_API_ORIGIN = 'https://myfridge-di8a.onrender.com'

const trimTrailingSlashes = (value) => value.replace(/\/+$/, '')

const normalizeApiOrigin = (value) => {
  const trimmed = trimTrailingSlashes(value)
  return trimmed.endsWith('/api') ? trimmed.slice(0, -4) : trimmed
}

const configuredApiUrl = import.meta.env.VITE_API_URL

export const API_ORIGIN = configuredApiUrl
  ? normalizeApiOrigin(configuredApiUrl)
  : (import.meta.env.DEV ? '' : PROD_API_ORIGIN)

export const API_BASE = `${API_ORIGIN}/api`
