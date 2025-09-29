import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/services/api'
import { useAuthStore } from '@/stores/auth'

export const useCompanyStore = defineStore('company', () => {
  // State
  const companies = ref([])
  const currentCompany = ref(null)
  const loading = ref(false)
  const accountsChanged = ref(0) // Contador para notificar cambios en cuentas

  // Actions
  const fetchCompanies = async (params = {}) => {
    const authStore = useAuthStore()
    
    // Verificar si el usuario está autenticado
    if (!authStore.isAuthenticated) {
      console.warn('User not authenticated, skipping companies fetch')
      return []
    }
    
    loading.value = true
    try {
      const response = await api.get('/companies', { params })
      companies.value = response.data
      return response.data
    } catch (error) {
      console.error('Error fetching companies:', error)
      // Solo cerrar sesión en 401; en 403 no cerrar sesión, solo informar
      if (error.response?.status === 401) {
        authStore.logout()
      }
      throw error
    } finally {
      loading.value = false
    }
  }

  const getCompany = async (id) => {
    loading.value = true
    try {
      const response = await api.get(`/companies/${id}`)
      return response.data
    } catch (error) {
      console.error('Error fetching company:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const createCompany = async (companyData) => {
    loading.value = true
    try {
      const response = await api.post('/companies', companyData)
      companies.value.push(response.data)
      return response.data
    } catch (error) {
      console.error('Error creating company:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const updateCompany = async (id, companyData) => {
    loading.value = true
    try {
      const response = await api.put(`/companies/${id}`, companyData)
      const index = companies.value.findIndex(c => c.id === id)
      if (index !== -1) {
        companies.value[index] = response.data
      }
      return response.data
    } catch (error) {
      console.error('Error updating company:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const deleteCompany = async (id) => {
    loading.value = true
    try {
      await api.delete(`/companies/${id}`)
      companies.value = companies.value.filter(c => c.id !== id)
      return true
    } catch (error) {
      console.error('Error deleting company:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const setCurrentCompany = (company) => {
    currentCompany.value = company
    localStorage.setItem('currentCompany', JSON.stringify(company))
  }

  const getCurrentCompany = () => {
    if (!currentCompany.value) {
      const stored = localStorage.getItem('currentCompany')
      if (stored) {
        currentCompany.value = JSON.parse(stored)
      }
    }
    return currentCompany.value
  }

  const notifyAccountsChanged = () => {
    accountsChanged.value++
  }

  return {
    // State
    companies,
    currentCompany,
    loading,
    accountsChanged,
    
    // Actions
    fetchCompanies,
    getCompany,
    createCompany,
    updateCompany,
    deleteCompany,
    setCurrentCompany,
    getCurrentCompany,
    notifyAccountsChanged
  }
})
