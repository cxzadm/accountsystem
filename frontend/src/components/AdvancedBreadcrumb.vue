<template>
  <nav aria-label="breadcrumb" class="advanced-breadcrumb-nav">
    <div class="breadcrumb-container">
      <ol class="breadcrumb">
        <li 
          v-for="(item, index) in breadcrumbItems" 
          :key="item.path || index"
          class="breadcrumb-item"
          :class="{ 'active': index === breadcrumbItems.length - 1 }"
        >
          <router-link 
            v-if="!item.active && item.path" 
            :to="item.path" 
            class="breadcrumb-link"
            @click="addToHistory(item)"
          >
            <i v-if="item.icon" :class="item.icon" class="me-1"></i>
            {{ item.label }}
          </router-link>
          <span v-else class="breadcrumb-current">
            <i v-if="item.icon" :class="item.icon" class="me-1"></i>
            {{ item.label }}
          </span>
        </li>
      </ol>
      
      <!-- Controles adicionales -->
      <div class="breadcrumb-controls" v-if="showControls">
        <button 
          class="btn btn-sm btn-outline-secondary me-2"
          @click="goBack"
          :disabled="!canGoBack"
          title="Página anterior"
        >
          <i class="fas fa-arrow-left"></i>
        </button>
        
        <button 
          class="btn btn-sm btn-outline-secondary me-2"
          @click="goForward"
          :disabled="!canGoForward"
          title="Página siguiente"
        >
          <i class="fas fa-arrow-right"></i>
        </button>
        
        <button 
          class="btn btn-sm btn-outline-secondary"
          @click="showHistory = !showHistory"
          title="Historial de navegación"
        >
          <i class="fas fa-history"></i>
        </button>
      </div>
    </div>
    
    <!-- Historial de navegación -->
    <div v-if="showHistory" class="breadcrumb-history">
      <div class="history-header">
        <h6>Historial de Navegación</h6>
        <button class="btn-close" @click="showHistory = false"></button>
      </div>
      <div class="history-list">
        <div 
          v-for="(item, index) in navigationHistory" 
          :key="index"
          class="history-item"
          @click="navigateToHistoryItem(item)"
        >
          <i v-if="item.icon" :class="item.icon" class="me-2"></i>
          <span>{{ item.label }}</span>
          <small class="text-muted ms-auto">{{ formatTime(item.timestamp) }}</small>
        </div>
        <div v-if="navigationHistory.length === 0" class="text-muted text-center py-2">
          No hay historial de navegación
        </div>
      </div>
    </div>
  </nav>
</template>

<script>
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useCompanyStore } from '@/stores/company'
import { useBreadcrumb } from '@/composables/useBreadcrumb'

export default {
  name: 'AdvancedBreadcrumb',
  props: {
    showControls: {
      type: Boolean,
      default: true
    }
  },
  setup(props) {
    const route = useRoute()
    const router = useRouter()
    const companyStore = useCompanyStore()
    const { getDynamicBreadcrumbs } = useBreadcrumb()

    // Estado
    const showHistory = ref(false)
    const navigationHistory = ref([])
    const currentHistoryIndex = ref(-1)

    // Breadcrumbs estáticos (misma lógica que Breadcrumb.vue)
    const breadcrumbItems = computed(() => {
      const items = []
      const currentRoute = route.path
      const currentCompany = companyStore.getCurrentCompany()

      // Inicio siempre visible
      items.push({
        label: 'Inicio',
        path: '/',
        icon: 'fas fa-home'
      })

      // Dashboard
      if (currentRoute === '/dashboard') {
        items.push({
          label: 'Dashboard',
          active: true,
          icon: 'fas fa-tachometer-alt'
        })
        return items
      }

      // Gestión de Empresas
      if (currentRoute.startsWith('/companies')) {
        items.push({
          label: 'Empresas',
          path: '/companies',
          icon: 'fas fa-building'
        })

        if (currentRoute === '/companies') {
          items.push({
            label: 'Lista de Empresas',
            active: true,
            icon: 'fas fa-list'
          })
        } else if (currentRoute.includes('/new')) {
          items.push({
            label: 'Nueva Empresa',
            active: true,
            icon: 'fas fa-plus'
          })
        } else if (currentRoute.includes('/edit/')) {
          items.push({
            label: 'Editar Empresa',
            active: true,
            icon: 'fas fa-edit'
          })
        } else if (currentRoute.includes('/settings/')) {
          const companyId = currentRoute.split('/')[2]
          items.push({
            label: currentCompany?.name || 'Empresa',
            path: `/companies/${companyId}`,
            icon: 'fas fa-building'
          })
          items.push({
            label: 'Configuración',
            active: true,
            icon: 'fas fa-cog'
          })
        } else if (currentRoute.includes('/initial-balances/')) {
          const companyId = currentRoute.split('/')[2]
          items.push({
            label: currentCompany?.name || 'Empresa',
            path: `/companies/${companyId}`,
            icon: 'fas fa-building'
          })
          items.push({
            label: 'Saldos Iniciales',
            active: true,
            icon: 'fas fa-coins'
          })
        } else if (currentRoute.includes('/users/')) {
          const companyId = currentRoute.split('/')[2]
          items.push({
            label: currentCompany?.name || 'Empresa',
            path: `/companies/${companyId}`,
            icon: 'fas fa-building'
          })
          items.push({
            label: 'Usuarios',
            active: true,
            icon: 'fas fa-users'
          })
        } else if (currentRoute.includes('/document-types/')) {
          const companyId = currentRoute.split('/')[2]
          items.push({
            label: currentCompany?.name || 'Empresa',
            path: `/companies/${companyId}`,
            icon: 'fas fa-building'
          })
          items.push({
            label: 'Tipos de Documento',
            active: true,
            icon: 'fas fa-file-alt'
          })
        } else if (currentRoute.includes('/document-reservations/')) {
          const companyId = currentRoute.split('/')[2]
          items.push({
            label: currentCompany?.name || 'Empresa',
            path: `/companies/${companyId}`,
            icon: 'fas fa-building'
          })
          items.push({
            label: 'Reservaciones de Documentos',
            active: true,
            icon: 'fas fa-calendar-check'
          })
        } else if (currentRoute.includes('/audit/')) {
          const companyId = currentRoute.split('/')[2]
          items.push({
            label: currentCompany?.name || 'Empresa',
            path: `/companies/${companyId}`,
            icon: 'fas fa-building'
          })
          items.push({
            label: 'Auditoría',
            active: true,
            icon: 'fas fa-search'
          })
        } else if (currentRoute.includes('/sri/')) {
          const companyId = currentRoute.split('/')[2]
          items.push({
            label: currentCompany?.name || 'Empresa',
            path: `/companies/${companyId}`,
            icon: 'fas fa-building'
          })
          items.push({
            label: 'SRI',
            active: true,
            icon: 'fas fa-file-invoice'
          })
        } else if (currentRoute.includes('/reports/')) {
          const companyId = currentRoute.split('/')[2]
          items.push({
            label: currentCompany?.name || 'Empresa',
            path: `/companies/${companyId}`,
            icon: 'fas fa-building'
          })
          items.push({
            label: 'Reportes',
            active: true,
            icon: 'fas fa-chart-bar'
          })
        } else if (currentRoute.includes('/')) {
          const companyId = currentRoute.split('/')[2]
          items.push({
            label: currentCompany?.name || 'Empresa',
            active: true,
            icon: 'fas fa-building'
          })
        }
      }

      // Plan de Cuentas
      else if (currentRoute.startsWith('/accounts')) {
        items.push({
          label: 'Plan de Cuentas',
          active: true,
          icon: 'fas fa-list-alt'
        })
      }

      // Diario Contable
      else if (currentRoute.startsWith('/journal')) {
        items.push({
          label: 'Diario Contable',
          active: true,
          icon: 'fas fa-book'
        })
      }

      // Mayor General
      else if (currentRoute.startsWith('/ledger')) {
        items.push({
          label: 'Mayor General',
          active: true,
          icon: 'fas fa-table'
        })
      }

      // Perfil de Usuario
      else if (currentRoute.startsWith('/profile')) {
        items.push({
          label: 'Mi Perfil',
          active: true,
          icon: 'fas fa-user'
        })
      }

      // Configuración General
      else if (currentRoute.startsWith('/settings')) {
        items.push({
          label: 'Configuración',
          active: true,
          icon: 'fas fa-cog'
        })
      }

      // Usuarios (Global)
      else if (currentRoute.startsWith('/users')) {
        items.push({
          label: 'Usuarios',
          active: true,
          icon: 'fas fa-users'
        })
      }

      // Agregar breadcrumbs dinámicos al final
      items.push(...getDynamicBreadcrumbs.value)

      return items
    })

    // Navegación hacia atrás/adelante
    const canGoBack = computed(() => currentHistoryIndex.value > 0)
    const canGoForward = computed(() => currentHistoryIndex.value < navigationHistory.value.length - 1)

    // Agregar al historial
    const addToHistory = (item) => {
      const historyItem = {
        ...item,
        timestamp: new Date(),
        route: route.path
      }
      
      // Si estamos en el medio del historial, eliminar elementos posteriores
      if (currentHistoryIndex.value < navigationHistory.value.length - 1) {
        navigationHistory.value = navigationHistory.value.slice(0, currentHistoryIndex.value + 1)
      }
      
      navigationHistory.value.push(historyItem)
      currentHistoryIndex.value = navigationHistory.value.length - 1
      
      // Limitar historial a 50 elementos
      if (navigationHistory.value.length > 50) {
        navigationHistory.value.shift()
        currentHistoryIndex.value--
      }
    }

    // Navegar hacia atrás
    const goBack = () => {
      if (canGoBack.value) {
        currentHistoryIndex.value--
        const item = navigationHistory.value[currentHistoryIndex.value]
        if (item.path) {
          router.push(item.path)
        }
      }
    }

    // Navegar hacia adelante
    const goForward = () => {
      if (canGoForward.value) {
        currentHistoryIndex.value++
        const item = navigationHistory.value[currentHistoryIndex.value]
        if (item.path) {
          router.push(item.path)
        }
      }
    }

    // Navegar a elemento del historial
    const navigateToHistoryItem = (item) => {
      if (item.path) {
        router.push(item.path)
        showHistory.value = false
      }
    }

    // Formatear tiempo
    const formatTime = (timestamp) => {
      const now = new Date()
      const diff = now - timestamp
      const minutes = Math.floor(diff / 60000)
      
      if (minutes < 1) return 'Ahora'
      if (minutes < 60) return `${minutes}m`
      if (minutes < 1440) return `${Math.floor(minutes / 60)}h`
      return timestamp.toLocaleDateString()
    }

    // Cargar historial del localStorage
    onMounted(() => {
      const saved = localStorage.getItem('breadcrumb-history')
      if (saved) {
        try {
          const parsed = JSON.parse(saved)
          navigationHistory.value = parsed.map(item => ({
            ...item,
            timestamp: new Date(item.timestamp)
          }))
          currentHistoryIndex.value = navigationHistory.value.length - 1
        } catch (e) {
          console.warn('Error loading breadcrumb history:', e)
        }
      }
    })

    // Guardar historial en localStorage
    const saveHistory = () => {
      localStorage.setItem('breadcrumb-history', JSON.stringify(navigationHistory.value))
    }

    // Guardar historial cuando cambie
    watch(navigationHistory, saveHistory, { deep: true })

    // Limpiar al desmontar
    onUnmounted(() => {
      saveHistory()
    })

    return {
      breadcrumbItems,
      showHistory,
      navigationHistory,
      canGoBack,
      canGoForward,
      addToHistory,
      goBack,
      goForward,
      navigateToHistoryItem,
      formatTime
    }
  }
}
</script>

<style scoped>
.advanced-breadcrumb-nav {
  background: linear-gradient(135deg, #f8f9fc 0%, #e3e6f0 100%);
  border-bottom: 2px solid #bb8945;
  padding: 0.75rem 1rem;
  margin-bottom: 1rem;
  position: relative;
  border-radius: 0 0 0.35rem 0.35rem;
  box-shadow: 0 0.15rem 1.75rem 0 rgba(22, 92, 106, 0.1);
}

.breadcrumb-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.breadcrumb {
  margin-bottom: 0;
  background: none;
  padding: 0;
  flex: 1;
}

.breadcrumb-item {
  display: flex;
  align-items: center;
}

.breadcrumb-item + .breadcrumb-item::before {
  content: ">";
  color: #bb8945;
  font-weight: 600;
  margin: 0 0.5rem;
  font-size: 0.9rem;
}

.breadcrumb-link {
  color: #165c6a;
  text-decoration: none;
  transition: all 0.15s ease-in-out;
  display: flex;
  align-items: center;
  font-weight: 500;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
}

.breadcrumb-link:hover {
  color: #0f3d47;
  background-color: rgba(187, 137, 69, 0.1);
  text-decoration: none;
  transform: translateY(-1px);
}

.breadcrumb-current {
  color: #0f3d47;
  font-weight: 600;
  display: flex;
  align-items: center;
  padding: 0.25rem 0.5rem;
  background-color: rgba(187, 137, 69, 0.1);
  border-radius: 0.25rem;
  border-left: 3px solid #bb8945;
}

.breadcrumb-item.active .breadcrumb-current {
  color: #0f3d47;
  font-weight: 700;
}

.breadcrumb-controls {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.breadcrumb-controls .btn {
  background: linear-gradient(45deg, #bb8945, #d4a853);
  border: none;
  color: #fff;
  font-weight: 500;
  border-radius: 0.25rem;
  padding: 0.375rem 0.75rem;
  font-size: 0.875rem;
  transition: all 0.2s ease-in-out;
}

.breadcrumb-controls .btn:hover {
  background: linear-gradient(45deg, #d4a853, #bb8945);
  transform: translateY(-1px);
  box-shadow: 0 0.125rem 0.25rem rgba(187, 137, 69, 0.25);
}

.breadcrumb-controls .btn:disabled {
  background: #6c757d;
  opacity: 0.6;
  transform: none;
  box-shadow: none;
}

.breadcrumb-history {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: #fff;
  border: 1px solid #bb8945;
  border-top: none;
  border-radius: 0 0 0.35rem 0.35rem;
  box-shadow: 0 0.25rem 2rem 0 rgba(22, 92, 106, 0.15);
  z-index: 1000;
  max-height: 300px;
  overflow-y: auto;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  border-bottom: 2px solid #bb8945;
  background: linear-gradient(90deg, #bb8945, #d4a853);
  color: #fff;
  border-radius: 0.35rem 0.35rem 0 0;
}

.history-header h6 {
  margin: 0;
  font-size: 0.875rem;
  font-weight: 600;
  color: #fff;
}

.history-header .btn-close {
  background: none;
  border: none;
  color: #fff;
  font-size: 1.25rem;
  opacity: 0.8;
  transition: opacity 0.2s ease-in-out;
}

.history-header .btn-close:hover {
  opacity: 1;
}

.history-list {
  max-height: 200px;
  overflow-y: auto;
}

.history-item {
  display: flex;
  align-items: center;
  padding: 0.75rem 1rem;
  cursor: pointer;
  transition: all 0.2s ease-in-out;
  border-bottom: 1px solid #f8f9fc;
}

.history-item:hover {
  background: linear-gradient(90deg, rgba(187, 137, 69, 0.1), rgba(212, 168, 83, 0.1));
  color: #0f3d47;
  transform: translateX(5px);
}

.history-item i {
  color: #bb8945;
  margin-right: 0.5rem;
}

.history-item small {
  color: #6c757d;
  font-size: 0.75rem;
}

.history-item:last-child {
  border-bottom: none;
}

/* Iconos con color de acento */
.breadcrumb-link i,
.breadcrumb-current i {
  color: #bb8945;
  margin-right: 0.25rem;
}

/* Responsive */
@media (max-width: 768px) {
  .advanced-breadcrumb-nav {
    padding: 0.5rem;
    font-size: 0.875rem;
    border-radius: 0;
  }
  
  .breadcrumb-container {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  
  .breadcrumb-controls {
    align-self: flex-end;
    flex-wrap: wrap;
  }
  
  .breadcrumb-item + .breadcrumb-item::before {
    margin: 0 0.25rem;
  }
  
  .breadcrumb-link,
  .breadcrumb-current {
    padding: 0.2rem 0.4rem;
    font-size: 0.8rem;
  }
  
  .breadcrumb-controls .btn {
    padding: 0.25rem 0.5rem;
    font-size: 0.8rem;
  }
}

/* Animaciones suaves */
.breadcrumb-link {
  transition: all 0.2s ease-in-out;
}

.breadcrumb-link:hover {
  box-shadow: 0 0.125rem 0.25rem rgba(187, 137, 69, 0.15);
}

/* Efecto de hover para el contenedor */
.advanced-breadcrumb-nav:hover {
  box-shadow: 0 0.25rem 2rem 0 rgba(22, 92, 106, 0.15);
  transition: box-shadow 0.3s ease-in-out;
}

</style>
