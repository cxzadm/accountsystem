<template>
  <div class="sidebar bg-dark text-white" :class="{ 'collapsed': isCollapsed }" id="sidebar">
    <div class="sidebar-content">
      <!-- User info -->
      <div class="sidebar-header p-3 border-bottom" v-if="!isCollapsed">
        <div class="d-flex align-items-center">
          <i class="fas fa-user-circle fa-2x me-3"></i>
          <div>
            <h6 class="mb-0">{{ user.first_name }} {{ user.last_name }}</h6>
            <small class="text-muted">{{ user.role }}</small>
          </div>
        </div>
      </div>

      <!-- User info collapsed -->
      <div class="sidebar-header p-3 border-bottom text-center" v-else>
        <i class="fas fa-user-circle fa-2x"></i>
      </div>

      <!-- Navigation -->
      <nav class="sidebar-nav">
        <ul class="nav flex-column">
          <!-- Dashboard -->
          <li class="nav-item">
            <router-link class="nav-link" to="/" exact-active-class="active" :title="isCollapsed ? 'Dashboard' : ''">
              <i class="fas fa-tachometer-alt" :class="{ 'me-2': !isCollapsed }"></i>
              <span v-if="!isCollapsed">Dashboard</span>
            </router-link>
          </li>

          <!-- Contabilidad -->
          <li class="nav-item">
            <a 
              class="nav-link" 
              data-bs-toggle="collapse" 
              href="#accountingMenu" 
              role="button"
              :title="isCollapsed ? 'Contabilidad' : ''"
              @click="handleMenuClick('accountingMenu')"
            >
              <i class="fas fa-calculator" :class="{ 'me-2': !isCollapsed }"></i>
              <span v-if="!isCollapsed">Contabilidad</span>
              <i v-if="!isCollapsed" class="fas fa-chevron-down ms-auto"></i>
            </a>
            <div class="collapse" id="accountingMenu" :class="{ 'show': expandedMenu === 'accountingMenu' }">
              <div class="submenu-header d-flex justify-content-between align-items-center px-3 py-2" v-if="isCollapsed">
                <small class="text-muted">Contabilidad</small>
                <button class="btn btn-sm btn-outline-light" @click="closeSubmenu('accountingMenu')" title="Cerrar menú">
                  <i class="fas fa-times"></i>
                </button>
              </div>
              <ul class="nav flex-column" :class="{ 'ms-3': !isCollapsed }">
                <li class="nav-item">
                  <router-link class="nav-link" to="/accounts" active-class="active" :title="isCollapsed ? 'Plan de Cuentas' : ''">
                    <i class="fas fa-list" :class="{ 'me-2': !isCollapsed }"></i>
                    <span v-if="!isCollapsed">Plan de Cuentas</span>
                  </router-link>
                </li>
                <li class="nav-item">
                  <router-link class="nav-link" to="/journal" active-class="active" :title="isCollapsed ? 'Diario Contable' : ''">
                    <i class="fas fa-book" :class="{ 'me-2': !isCollapsed }"></i>
                    <span v-if="!isCollapsed">Diario Contable</span>
                  </router-link>
                </li>
                <li class="nav-item">
                  <router-link class="nav-link" to="/ledger" active-class="active" :title="isCollapsed ? 'Mayor General' : ''">
                    <i class="fas fa-balance-scale" :class="{ 'me-2': !isCollapsed }"></i>
                    <span v-if="!isCollapsed">Mayor General</span>
                  </router-link>
                </li>
                <li class="nav-item">
                  <router-link class="nav-link" to="/reports" active-class="active" :title="isCollapsed ? 'Reportes' : ''">
                    <i class="fas fa-chart-bar" :class="{ 'me-2': !isCollapsed }"></i>
                    <span v-if="!isCollapsed">Reportes</span>
                  </router-link>
                </li>
              </ul>
            </div>
          </li>

          <!-- SRI -->
          <li class="nav-item" v-if="hasPermission('sri:read')">
            <router-link class="nav-link" to="/sri" active-class="active" :title="isCollapsed ? 'Declaraciones SRI' : ''">
              <i class="fas fa-file-invoice" :class="{ 'me-2': !isCollapsed }"></i>
              <span v-if="!isCollapsed">Declaraciones SRI</span>
            </router-link>
          </li>

          <!-- Administración -->
          <li class="nav-item" v-if="hasAnyRole(['admin', 'contador'])">
            <a 
              class="nav-link" 
              data-bs-toggle="collapse" 
              href="#adminMenu" 
              role="button"
              :title="isCollapsed ? 'Administración' : ''"
              @click="handleMenuClick('adminMenu')"
            >
              <i class="fas fa-cogs" :class="{ 'me-2': !isCollapsed }"></i>
              <span v-if="!isCollapsed">Administración</span>
              <i v-if="!isCollapsed" class="fas fa-chevron-down ms-auto"></i>
            </a>
            <div class="collapse" id="adminMenu" :class="{ 'show': expandedMenu === 'adminMenu' }">
              <div class="submenu-header d-flex justify-content-between align-items-center px-3 py-2" v-if="isCollapsed">
                <small class="text-muted">Administración</small>
                <button class="btn btn-sm btn-outline-light" @click="closeSubmenu('adminMenu')" title="Cerrar menú">
                  <i class="fas fa-times"></i>
                </button>
              </div>
              <ul class="nav flex-column" :class="{ 'ms-3': !isCollapsed }">
                <li class="nav-item" v-if="hasPermission('users:read')">
                  <router-link class="nav-link" to="/users" active-class="active" :title="isCollapsed ? 'Usuarios' : ''">
                    <i class="fas fa-users" :class="{ 'me-2': !isCollapsed }"></i>
                    <span v-if="!isCollapsed">Usuarios</span>
                  </router-link>
                </li>
                <li class="nav-item" v-if="hasPermission('companies:read')">
                  <router-link class="nav-link" to="/companies" active-class="active" :title="isCollapsed ? 'Empresas' : ''">
                    <i class="fas fa-building" :class="{ 'me-2': !isCollapsed }"></i>
                    <span v-if="!isCollapsed">Empresas</span>
                  </router-link>
                </li>
                <li class="nav-item" v-if="hasPermission('audit:read')">
                  <router-link class="nav-link" to="/audit" active-class="active" :title="isCollapsed ? 'Auditoría' : ''">
                    <i class="fas fa-history" :class="{ 'me-2': !isCollapsed }"></i>
                    <span v-if="!isCollapsed">Auditoría</span>
                  </router-link>
                </li>
              </ul>
            </div>
          </li>
        </ul>
      </nav>
    </div>
  </div>
</template>

<script>
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '@/stores/auth'

export default {
  name: 'Sidebar',
  setup() {
    const authStore = useAuthStore()
    const isCollapsed = ref(false)
    const expandedMenu = ref(null)
    const wasOriginallyCollapsed = ref(false)

    const user = computed(() => authStore.user)

    const hasPermission = (permission) => {
      return authStore.hasPermission(permission)
    }

    const hasAnyRole = (roles) => {
      return authStore.hasAnyRole(roles)
    }

    const toggleCollapse = (menuId) => {
      if (expandedMenu.value === menuId) {
        expandedMenu.value = null
      } else {
        expandedMenu.value = menuId
      }
    }

    const handleToggleSidebar = () => {
      isCollapsed.value = !isCollapsed.value
      document.body.classList.toggle('sidebar-collapsed', isCollapsed.value)
    }

    const handleMenuClick = (menuId) => {
      if (isCollapsed.value) {
        // Si está contraído, expandir temporalmente
        wasOriginallyCollapsed.value = true
        isCollapsed.value = false
        document.body.classList.remove('sidebar-collapsed')
        expandedMenu.value = menuId
        
        // Expandir el menú después de un pequeño delay para la animación
        setTimeout(() => {
          const menuElement = document.getElementById(menuId)
          if (menuElement) {
            menuElement.classList.add('show')
          }
        }, 150)
      } else {
        // Si está expandido, toggle normal
        toggleCollapse(menuId)
      }
    }

    const closeSubmenu = (menuId) => {
      expandedMenu.value = null
      const menuElement = document.getElementById(menuId)
      if (menuElement) {
        menuElement.classList.remove('show')
      }
    }

    const handleNavigation = () => {
      // Solo contraer el sidebar si estaba originalmente contraído
      // Pero mantener los submenús expandidos
      if (wasOriginallyCollapsed.value) {
        wasOriginallyCollapsed.value = false
        // Volver a contraer el sidebar pero mantener el menú expandido
        isCollapsed.value = true
        document.body.classList.add('sidebar-collapsed')
      }
    }

    onMounted(() => {
      // Escuchar el evento de toggle del navbar
      document.addEventListener('toggle-sidebar', handleToggleSidebar)
      
      // Escuchar eventos de navegación para contraer el sidebar
      document.addEventListener('click', (event) => {
        // Si se hace clic en un enlace de navegación dentro del sidebar
        const navLink = event.target.closest('.sidebar .nav-link[href^="/"]')
        if (navLink) {
          setTimeout(() => {
            handleNavigation()
          }, 200)
        }
      })
      
      // Verificar estado inicial
      isCollapsed.value = document.body.classList.contains('sidebar-collapsed')
    })

    onUnmounted(() => {
      document.removeEventListener('toggle-sidebar', handleToggleSidebar)
    })

    return {
      user,
      isCollapsed,
      expandedMenu,
      hasPermission,
      hasAnyRole,
      toggleCollapse,
      handleMenuClick,
      closeSubmenu
    }
  }
}
</script>

<style scoped>
.sidebar {
  position: fixed;
  top: 0;
  left: 0;
  width: 250px;
  height: 100vh;
  z-index: 1000;
  overflow-y: auto;
  transition: all 0.3s ease;
  padding-top: 70px;
}

.sidebar.collapsed {
  width: 70px;
}

.sidebar-content {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  flex-shrink: 0;
}

.sidebar-nav {
  flex: 1;
  padding: 1rem 0;
}

.nav-link {
  color: #adb5bd;
  padding: 0.75rem 1rem;
  border-radius: 0;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  text-decoration: none;
  white-space: nowrap;
}

.nav-link:hover {
  color: #fff;
  background-color: rgba(255, 255, 255, 0.1);
}

.nav-link.active {
  color: #fff;
  background-color: rgba(255, 255, 255, 0.2);
  border-right: 3px solid #007bff;
}

.nav-link i {
  width: 20px;
  text-align: center;
  flex-shrink: 0;
}

.collapse .nav-link {
  padding-left: 2.5rem;
  font-size: 0.9rem;
}

/* Estilos para sidebar contraído */
.sidebar.collapsed .nav-link {
  justify-content: center;
  padding: 0.75rem 0.5rem;
}

.sidebar.collapsed .nav-link span {
  display: none;
}

.sidebar.collapsed .nav-link i {
  margin: 0;
}

.sidebar.collapsed .sidebar-header {
  padding: 1rem 0.5rem;
}

.sidebar.collapsed .collapse {
  position: absolute;
  left: 70px;
  top: 0;
  background: #343a40;
  min-width: 200px;
  box-shadow: 2px 0 5px rgba(0,0,0,0.2);
  z-index: 1001;
}

.sidebar.collapsed .collapse .nav-link {
  padding-left: 1rem;
  justify-content: flex-start;
}

.sidebar.collapsed .collapse .nav-link span {
  display: inline;
}

.sidebar.collapsed .collapse .nav-link i {
  margin-right: 0.5rem;
}

/* Estilos para el header del submenú */
.submenu-header {
  background-color: rgba(255, 255, 255, 0.1);
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}

.submenu-header .btn {
  padding: 0.25rem 0.5rem;
  font-size: 0.75rem;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.submenu-header .btn:hover {
  background-color: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.5);
}

@media (max-width: 768px) {
  .sidebar {
    transform: translateX(-100%);
  }
  
  .sidebar.show {
    transform: translateX(0);
  }
}
</style>

