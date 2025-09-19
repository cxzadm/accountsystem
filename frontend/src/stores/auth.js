import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'

export const useAuthStore = defineStore('auth', () => {
  // State
  const token = ref(localStorage.getItem('token'))
  const refreshToken = ref(localStorage.getItem('refreshToken'))
  const user = ref(JSON.parse(localStorage.getItem('user') || '{}'))
  const permissions = ref(JSON.parse(localStorage.getItem('permissions') || '[]'))

  // Getters
  const isAuthenticated = computed(() => !!token.value)
  const userRole = computed(() => user.value.role)
  const userCompanies = computed(() => user.value.companies || [])

  // Actions
  const login = async (credentials) => {
    try {
      const response = await api.post('/auth/login', credentials)
      const { access_token, refresh_token, user: userData } = response.data
      
      // Store tokens and user data
      token.value = access_token
      refreshToken.value = refresh_token
      user.value = userData
      permissions.value = userData.permissions || []
      
      // Persist to localStorage
      localStorage.setItem('token', access_token)
      localStorage.setItem('refreshToken', refresh_token)
      localStorage.setItem('user', JSON.stringify(userData))
      localStorage.setItem('permissions', JSON.stringify(userData.permissions || []))
      
      // Set default authorization header
      api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
      
      return { success: true }
    } catch (error) {
      console.error('Login error:', error)
      return { 
        success: false, 
        message: error.response?.data?.detail || 'Error al iniciar sesión' 
      }
    }
  }

  const logout = async () => {
    try {
      if (token.value) {
        await api.post('/auth/logout')
      }
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      // Clear all data
      token.value = null
      refreshToken.value = null
      user.value = {}
      permissions.value = []
      
      // Clear localStorage
      localStorage.removeItem('token')
      localStorage.removeItem('refreshToken')
      localStorage.removeItem('user')
      localStorage.removeItem('permissions')
      
      // Clear authorization header
      delete api.defaults.headers.common['Authorization']
    }
  }

  const refreshAuthToken = async () => {
    try {
      if (!refreshToken.value) {
        throw new Error('No refresh token available')
      }
      
      const response = await api.post('/auth/refresh', {
        refresh_token: refreshToken.value
      })
      
      const { access_token } = response.data
      token.value = access_token
      localStorage.setItem('token', access_token)
      api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
      
      return true
    } catch (error) {
      console.error('Token refresh error:', error)
      await logout()
      return false
    }
  }

  const hasPermission = (permission) => {
    return permissions.value.includes(permission)
  }

  const hasRole = (role) => {
    return userRole.value === role
  }

  const hasAnyRole = (roles) => {
    return roles.includes(userRole.value)
  }

  const canAccessCompany = (companyId) => {
    return userRole.value === 'admin' || userCompanies.value.includes(companyId)
  }

  const getCurrentUser = async () => {
    try {
      const response = await api.get('/auth/me')
      user.value = response.data
      permissions.value = response.data.permissions || []
      
      localStorage.setItem('user', JSON.stringify(response.data))
      localStorage.setItem('permissions', JSON.stringify(response.data.permissions || []))
      
      return response.data
    } catch (error) {
      console.error('Get current user error:', error)
      await logout()
      throw error
    }
  }

  const updateProfile = async (profileData) => {
    try {
      const response = await api.put('/auth/profile', profileData)
      user.value = response.data
      localStorage.setItem('user', JSON.stringify(response.data))
      return response.data
    } catch (error) {
      console.error('Update profile error:', error)
      throw error
    }
  }

  const changePassword = async (passwordData) => {
    try {
      await api.post('/auth/change-password', passwordData)
      return true
    } catch (error) {
      console.error('Change password error:', error)
      throw error
    }
  }

  // Initialize auth state
  const initAuth = () => {
    if (token.value) {
      api.defaults.headers.common['Authorization'] = `Bearer ${token.value}`
    }
  }

  return {
    // State
    token,
    refreshToken,
    user,
    permissions,
    
    // Getters
    isAuthenticated,
    userRole,
    userCompanies,
    
    // Actions
    login,
    logout,
    refreshAuthToken,
    hasPermission,
    hasRole,
    hasAnyRole,
    canAccessCompany,
    getCurrentUser,
    updateProfile,
    changePassword,
    initAuth
  }
})
