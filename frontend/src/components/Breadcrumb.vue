<template>
  <nav aria-label="breadcrumb" class="breadcrumb-nav">
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
  </nav>
</template>

<script>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useCompanyStore } from '@/stores/company'
import { useBreadcrumb } from '@/composables/useBreadcrumb'

export default {
  name: 'Breadcrumb',
  setup() {
    const route = useRoute()
    const router = useRouter()
    const companyStore = useCompanyStore()
    const { getDynamicBreadcrumbs } = useBreadcrumb()

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

    return {
      breadcrumbItems
    }
  }
}
</script>

<style scoped>
.breadcrumb-nav {
  background: linear-gradient(135deg, #f8f9fc 0%, #e3e6f0 100%);
  border-bottom: 2px solid #bb8945;
  padding: 0.75rem 1rem;
  margin-bottom: 1rem;
  border-radius: 0 0 0.35rem 0.35rem;
  box-shadow: 0 0.15rem 1.75rem 0 rgba(22, 92, 106, 0.1);
}

.breadcrumb {
  margin-bottom: 0;
  background: none;
  padding: 0;
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

/* Iconos con color de acento */
.breadcrumb-link i,
.breadcrumb-current i {
  color: #bb8945;
  margin-right: 0.25rem;
}

/* Responsive */
@media (max-width: 768px) {
  .breadcrumb-nav {
    padding: 0.5rem;
    font-size: 0.875rem;
    border-radius: 0;
  }
  
  .breadcrumb-item + .breadcrumb-item::before {
    margin: 0 0.25rem;
  }
  
  .breadcrumb-link,
  .breadcrumb-current {
    padding: 0.2rem 0.4rem;
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
.breadcrumb-nav:hover {
  box-shadow: 0 0.25rem 2rem 0 rgba(22, 92, 106, 0.15);
  transition: box-shadow 0.3s ease-in-out;
}
</style>
