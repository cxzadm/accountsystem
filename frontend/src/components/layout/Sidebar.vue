<template>
  <div class="sidebar bg-dark text-white" id="sidebar">
    <div class="sidebar-content">
      <!-- User info -->
      <div class="sidebar-header p-3 border-bottom">
        <div class="d-flex align-items-center">
          <i class="fas fa-user-circle fa-2x me-3"></i>
          <div>
            <h6 class="mb-0">{{ user.first_name }} {{ user.last_name }}</h6>
            <small class="text-muted">{{ user.role }}</small>
          </div>
        </div>
      </div>

      <!-- Navigation -->
      <nav class="sidebar-nav">
        <ul class="nav flex-column">
          <!-- Dashboard -->
          <li class="nav-item">
            <router-link class="nav-link" to="/" exact-active-class="active">
              <i class="fas fa-tachometer-alt me-2"></i>
              Dashboard
            </router-link>
          </li>

          <!-- Contabilidad -->
          <li class="nav-item">
            <a 
              class="nav-link" 
              data-bs-toggle="collapse" 
              href="#accountingMenu" 
              role="button"
            >
              <i class="fas fa-calculator me-2"></i>
              Contabilidad
              <i class="fas fa-chevron-down ms-auto"></i>
            </a>
            <div class="collapse" id="accountingMenu">
              <ul class="nav flex-column ms-3">
                <li class="nav-item">
                  <router-link class="nav-link" to="/accounts" active-class="active">
                    <i class="fas fa-list me-2"></i>
                    Plan de Cuentas
                  </router-link>
                </li>
                <li class="nav-item">
                  <router-link class="nav-link" to="/journal" active-class="active">
                    <i class="fas fa-book me-2"></i>
                    Diario Contable
                  </router-link>
                </li>
                <li class="nav-item">
                  <router-link class="nav-link" to="/ledger" active-class="active">
                    <i class="fas fa-balance-scale me-2"></i>
                    Mayor General
                  </router-link>
                </li>
                <li class="nav-item">
                  <router-link class="nav-link" to="/reports" active-class="active">
                    <i class="fas fa-chart-bar me-2"></i>
                    Reportes
                  </router-link>
                </li>
              </ul>
            </div>
          </li>

          <!-- SRI -->
          <li class="nav-item" v-if="hasPermission('sri:read')">
            <router-link class="nav-link" to="/sri" active-class="active">
              <i class="fas fa-file-invoice me-2"></i>
              Declaraciones SRI
            </router-link>
          </li>

          <!-- Administración -->
          <li class="nav-item" v-if="hasAnyRole(['admin', 'contador'])">
            <a 
              class="nav-link" 
              data-bs-toggle="collapse" 
              href="#adminMenu" 
              role="button"
            >
              <i class="fas fa-cogs me-2"></i>
              Administración
              <i class="fas fa-chevron-down ms-auto"></i>
            </a>
            <div class="collapse" id="adminMenu">
              <ul class="nav flex-column ms-3">
                <li class="nav-item" v-if="hasPermission('users:read')">
                  <router-link class="nav-link" to="/users" active-class="active">
                    <i class="fas fa-users me-2"></i>
                    Usuarios
                  </router-link>
                </li>
                <li class="nav-item" v-if="hasPermission('companies:read')">
                  <router-link class="nav-link" to="/companies" active-class="active">
                    <i class="fas fa-building me-2"></i>
                    Empresas
                  </router-link>
                </li>
                <li class="nav-item" v-if="hasPermission('audit:read')">
                  <router-link class="nav-link" to="/audit" active-class="active">
                    <i class="fas fa-history me-2"></i>
                    Auditoría
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
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'

export default {
  name: 'Sidebar',
  setup() {
    const authStore = useAuthStore()

    const user = computed(() => authStore.user)

    const hasPermission = (permission) => {
      return authStore.hasPermission(permission)
    }

    const hasAnyRole = (roles) => {
      return authStore.hasAnyRole(roles)
    }

    return {
      user,
      hasPermission,
      hasAnyRole
    }
  }
}
</script>

<style scoped>
.sidebar {
  position: fixed;
  top: 70px;
  left: 0;
  width: 250px;
  height: calc(100vh - 70px);
  z-index: 1000;
  overflow-y: auto;
  transition: all 0.3s;
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
}

.collapse .nav-link {
  padding-left: 2.5rem;
  font-size: 0.9rem;
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

