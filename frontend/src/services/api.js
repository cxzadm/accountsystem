import axios from 'axios'
import { config } from '../../config.js'

// Decide baseURL: use reverse-proxy path in production (served via Nginx),
// and direct backend URL during Vite dev server
const isViteDev = typeof window !== 'undefined' && (
  window.location.port === '5173' || window.location.hostname === 'localhost'
)

const apiBaseURL = isViteDev ? `${config.API_BASE_URL}/api` : '/api'

// Create axios instance
const api = axios.create({
  baseURL: apiBaseURL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Get token from localStorage directly
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response
  },
  async (error) => {
    // Solo cerrar sesión automáticamente en 401 (token inválido/expirado)
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('refreshToken')
      localStorage.removeItem('user')
      localStorage.removeItem('permissions')
      window.location.href = '/login'
    }
    // Para 403 (forbidden) solo propagamos el error para que la UI lo maneje
    return Promise.reject(error)
  }
)

export default api
