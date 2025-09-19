<template>
  <nav class="navbar navbar-expand-lg navbar-dark bg-primary fixed-top">
    <div class="container-fluid">
      <!-- Toggle button -->
      <button 
        class="btn btn-outline-light me-3" 
        @click="toggleSidebar"
        type="button"
      >
        <i class="fas fa-bars"></i>
      </button>

      <!-- Brand -->
      <router-link class="navbar-brand" to="/">
        <i class="fas fa-calculator me-2"></i>
        Sistema Contable  Accescont Ecuador
      </router-link>

      <!-- Company selector -->
      <div class="navbar-nav me-auto">
        <div class="nav-item dropdown" v-if="currentCompany">
          <a 
            class="nav-link dropdown-toggle" 
            href="#" 
            role="button" 
            data-bs-toggle="dropdown"
          >
            <i class="fas fa-building me-1"></i>
            {{ currentCompany.name }}
          </a>
          <ul class="dropdown-menu">
            <li v-for="company in companies" :key="company.id">
              <a 
                class="dropdown-item" 
                href="#" 
                @click="selectCompany(company)"
              >
                {{ company.name }}
              </a>
            </li>
          </ul>
        </div>
      </div>

      <!-- User menu -->
      <div class="navbar-nav">
        <div class="nav-item dropdown">
          <a 
            class="nav-link dropdown-toggle d-flex align-items-center" 
            href="#" 
            role="button" 
            data-bs-toggle="dropdown"
          >
            <i class="fas fa-user-circle me-2"></i>
            {{ user.first_name }} {{ user.last_name }}
            <span class="badge bg-secondary ms-2">{{ user.role }}</span>
          </a>
          <ul class="dropdown-menu dropdown-menu-end">
            <li>
              <router-link class="dropdown-item" to="/profile">
                <i class="fas fa-user me-2"></i>
                Perfil
              </router-link>
            </li>
            <li>
              <router-link class="dropdown-item" to="/settings">
                <i class="fas fa-cog me-2"></i>
                Configuración
              </router-link>
            </li>
            <li><hr class="dropdown-divider"></li>
            <li>
              <a class="dropdown-item" href="#" @click="logout">
                <i class="fas fa-sign-out-alt me-2"></i>
                Cerrar Sesión
              </a>
            </li>
          </ul>
        </div>
      </div>
    </div>
  </nav>
</template>

<script>
import { computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useCompanyStore } from '@/stores/company'
import { useToast } from 'vue-toastification'

export default {
  name: 'Navbar',
  setup() {
    const authStore = useAuthStore()
    const companyStore = useCompanyStore()
    const toast = useToast()

    const user = computed(() => authStore.user)
    const companies = computed(() => companyStore.companies)
    const currentCompany = computed(() => companyStore.currentCompany)

    const toggleSidebar = () => {
      // Toggle sidebar functionality
      document.body.classList.toggle('sidebar-toggled')
    }

    const selectCompany = async (company) => {
      try {
        companyStore.setCurrentCompany(company)
        toast.success(`Empresa cambiada a: ${company.name}`)
        // Reload current page to update data
        window.location.reload()
      } catch (error) {
        toast.error('Error al cambiar empresa')
      }
    }

    const logout = async () => {
      try {
        await authStore.logout()
        toast.success('Sesión cerrada exitosamente')
      } catch (error) {
        toast.error('Error al cerrar sesión')
      }
    }

    onMounted(async () => {
      try {
        // Solo cargar empresas si el usuario está autenticado
        if (authStore.isAuthenticated) {
          await companyStore.fetchCompanies()
          const current = companyStore.getCurrentCompany()
          if (current) {
            companyStore.setCurrentCompany(current)
          } else if (companies.value.length > 0) {
            companyStore.setCurrentCompany(companies.value[0])
          }
        }
      } catch (error) {
        console.error('Error loading companies:', error)
      }
    })

    return {
      user,
      companies,
      currentCompany,
      toggleSidebar,
      selectCompany,
      logout
    }
  }
}
</script>

<style scoped>
.navbar {
  box-shadow: 0 2px 4px rgba(0,0,0,.1);
}

.navbar-brand {
  font-weight: 600;
}

.dropdown-menu {
  min-width: 200px;
}

.badge {
  font-size: 0.7em;
}
</style>
