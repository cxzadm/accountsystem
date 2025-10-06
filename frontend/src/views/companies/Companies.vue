<template>
  <div class="companies-page">
    <!-- Page Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h1 class="h3 mb-0">Gestión de Empresas</h1>
        <p class="text-muted">Administra las empresas del sistema</p>
      </div>
      <div>
        <router-link to="/companies/new" class="btn btn-primary">
          <i class="fas fa-plus me-2"></i>
          Nueva Empresa
        </router-link>
      </div>
    </div>

    <!-- Filters -->
    <div class="card mb-4">
      <div class="card-body">
        <div class="row">
          <div class="col-md-4">
            <label class="form-label">Buscar</label>
            <input
              type="text"
              class="form-control"
              v-model="filters.search"
              placeholder="Nombre, RUC o razón social..."
              @input="debouncedSearch"
            />
          </div>
          <div class="col-md-3">
            <label class="form-label">Estado</label>
            <select class="form-select" v-model="filters.status" @change="loadCompanies">
              <option value="">Todos los estados</option>
              <option value="active">Activo</option>
              <option value="inactive">Inactivo</option>
              <option value="suspended">Suspendido</option>
            </select>
          </div>
          <div class="col-md-3">
            <label class="form-label">Moneda</label>
            <select class="form-select" v-model="filters.currency" @change="loadCompanies">
              <option value="">Todas las monedas</option>
              <option value="USD">USD</option>
              <option value="EUR">EUR</option>
            </select>
          </div>
          <div class="col-md-2 d-flex align-items-end">
            <button class="btn btn-outline-secondary w-100" @click="clearFilters">
              <i class="fas fa-times me-1"></i>
              Limpiar
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Companies Table -->
    <div class="card">
      <div class="card-body">
        <div class="table-responsive">
          <table class="table table-hover">
            <thead>
              <tr>
                <th>Empresa</th>
                <th>RUC</th>
                <th>Razón Social</th>
                <th>Estado</th>
                <th>Moneda</th>
                <th>Fecha Creación</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="loading">
                <td colspan="7" class="text-center py-4">
                  <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Cargando...</span>
                  </div>
                </td>
              </tr>
              <tr v-else-if="companies.length === 0">
                <td colspan="7" class="text-center py-4 text-muted">
                  No se encontraron empresas
                </td>
              </tr>
              <tr v-else v-for="company in companies" :key="company.id">
                <td>
                  <div class="d-flex align-items-center">
                    <i class="fas fa-building fa-2x text-muted me-3"></i>
                    <div>
                      <strong>{{ company.name }}</strong>
                    </div>
                  </div>
                </td>
                <td>{{ company.ruc }}</td>
                <td>{{ company.legal_name }}</td>
                <td>
                  <span :class="`badge bg-${getStatusColor(company.status)}`">
                    {{ company.status }}
                  </span>
                </td>
                <td>
                  <span class="badge bg-info">{{ company.currency }}</span>
                </td>
                <td>{{ formatDate(company.created_at) }}</td>
                <td>
                  <div class="btn-group" role="group">
                    <button
                      class="btn btn-sm btn-outline-secondary"
                      @click="openSettings(company)"
                      title="Configuración"
                    >
                      <i class="fas fa-cog"></i>
                    </button>
                    <button
                      class="btn btn-sm btn-outline-primary"
                      @click="editCompany(company)"
                      title="Editar"
                    >
                      <i class="fas fa-edit"></i>
                    </button>
                    <div class="btn-group" role="group">
                      <button
                        class="btn btn-sm btn-outline-warning dropdown-toggle"
                        type="button"
                        data-bs-toggle="dropdown"
                        aria-expanded="false"
                        title="Acciones de Estado"
                      >
                        <i class="fas fa-ellipsis-v"></i>
                      </button>
                      <ul class="dropdown-menu">
                        <li v-if="company.status === 'active'">
                          <button
                            class="dropdown-item text-warning"
                            @click="deactivateCompany(company)"
                          >
                            <i class="fas fa-pause me-2"></i>Inactivar
                          </button>
                        </li>
                        <li v-if="company.status === 'inactive'">
                          <button
                            class="dropdown-item text-success"
                            @click="activateCompany(company)"
                          >
                            <i class="fas fa-play me-2"></i>Activar
                          </button>
                        </li>
                        <li><hr class="dropdown-divider"></li>
                        <li>
                          <button
                            class="dropdown-item text-danger"
                            @click="forceDeleteCompany(company)"
                          >
                            <i class="fas fa-trash-alt me-2"></i>Eliminar Completamente
                          </button>
                        </li>
                      </ul>
                    </div>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Pagination -->
        <nav v-if="totalPages > 1" class="mt-4">
          <ul class="pagination justify-content-center">
            <li class="page-item" :class="{ disabled: currentPage === 1 }">
              <button class="page-link" @click="changePage(currentPage - 1)">
                Anterior
              </button>
            </li>
            <li
              v-for="page in visiblePages"
              :key="page"
              class="page-item"
              :class="{ active: page === currentPage }"
            >
              <button class="page-link" @click="changePage(page)">
                {{ page }}
              </button>
            </li>
            <li class="page-item" :class="{ disabled: currentPage === totalPages }">
              <button class="page-link" @click="changePage(currentPage + 1)">
                Siguiente
              </button>
            </li>
          </ul>
        </nav>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'vue-toastification'
import api from '@/services/api'
import { debounce } from 'lodash-es'
import { alerts } from '@/services/alerts'
import Swal from 'sweetalert2'

export default {
  name: 'Companies',
  setup() {
    const router = useRouter()
    const toast = useToast()

    // State
    const companies = ref([])
    const loading = ref(false)
    const currentPage = ref(1)
    const totalPages = ref(1)
    const pageSize = 10

    const filters = reactive({
      search: '',
      status: '',
      currency: ''
    })

    // Computed
    const visiblePages = computed(() => {
      const pages = []
      const start = Math.max(1, currentPage.value - 2)
      const end = Math.min(totalPages.value, start + 4)
      
      for (let i = start; i <= end; i++) {
        pages.push(i)
      }
      return pages
    })

    // Methods
    const loadCompanies = async () => {
      loading.value = true
      try {
        const params = {
          skip: (currentPage.value - 1) * pageSize,
          limit: pageSize,
          ...filters
        }

        const response = await api.get('/companies', { params })
        companies.value = response.data
        totalPages.value = Math.ceil(response.data.length / pageSize)
      } catch (error) {
        console.error('Error loading companies:', error)
        toast.error('Error al cargar empresas')
      } finally {
        loading.value = false
      }
    }

    const debouncedSearch = debounce(() => {
      currentPage.value = 1
      loadCompanies()
    }, 500)

    const changePage = (page) => {
      if (page >= 1 && page <= totalPages.value) {
        currentPage.value = page
        loadCompanies()
      }
    }

    const clearFilters = () => {
      filters.search = ''
      filters.status = ''
      filters.currency = ''
      currentPage.value = 1
      loadCompanies()
    }

    const editCompany = (company) => {
      router.push(`/companies/${company.id}/edit`)
    }

    const openSettings = (company) => {
      router.push(`/companies/${company.id}/settings`)
    }

    const deactivateCompany = async (company) => {
      const confirmed = await alerts.confirm({
        title: 'Inactivar Empresa',
        text: `¿Estás seguro de inactivar la empresa "${company.name}"?`,
        confirmButtonText: 'Sí, Inactivar',
        cancelButtonText: 'Cancelar',
        icon: 'warning'
      })
      
      if (confirmed) {
        try {
          const response = await api.delete(`/companies/${company.id}?force_delete=false`)
          toast.success(response.data.message)
          loadCompanies()
        } catch (error) {
          console.error('Error deactivating company:', error)
          toast.error('Error al inactivar empresa')
        }
      }
    }

    const activateCompany = async (company) => {
      const confirmed = await alerts.confirm({
        title: 'Activar Empresa',
        text: `¿Estás seguro de activar la empresa "${company.name}"?`,
        confirmButtonText: 'Sí, Activar',
        cancelButtonText: 'Cancelar',
        icon: 'success'
      })
      
      if (confirmed) {
        try {
          // Actualizar el status a active
          const response = await api.put(`/companies/${company.id}`, {
            status: 'active'
          })
          toast.success('Empresa activada exitosamente')
          loadCompanies()
        } catch (error) {
          console.error('Error activating company:', error)
          toast.error('Error al activar empresa')
        }
      }
    }

    const forceDeleteCompany = async (company) => {
      const confirmed = await alerts.confirm({
        title: '⚠️ ELIMINACIÓN COMPLETA ⚠️',
        text: `¿Estás completamente seguro de eliminar "${company.name}"?

Esto borrará:
• La empresa completamente
• Todas las cuentas contables
• Todos los asientos contables
• Todas las entradas del mayor
• Tipos de documentos
• Reservas de números
• Logs de auditoría relacionados

Esta acción NO SE PUEDE DESHACER.`,
        confirmButtonText: 'Sí, Eliminar Completamente',
        cancelButtonText: 'Cancelar',
        icon: 'error'
      })
      
      if (confirmed) {
        // Segunda confirmación con input
        const doubleConfirm = await Swal.fire({
          title: 'FINAL CONFIRMACIÓN',
          text: `Escriba "ELIMINAR" para confirmar la eliminación de "${company.name}":`,
          input: 'text',
          inputPlaceholder: 'Escriba ELIMINAR aquí',
          showCancelButton: true,
          confirmButtonText: 'Confirmar Eliminación',
          cancelButtonText: 'Cancelar',
          icon: 'warning',
          inputValidator: (value) => {
            if (value !== 'ELIMINAR') {
              return 'Debe escribir exactamente "ELIMINAR"'
            }
          }
        })
        
        if (doubleConfirm.isConfirmed) {
          try {
            const response = await api.delete(`/companies/${company.id}?force_delete=true`)
            toast.success(response.data.message)
            
            // Mostrar detalles de lo que se removió
            if (response.data.deleted_data) {
              const deleted = response.data.deleted_data
              console.log('📊 Datos eliminados:', deleted)
              
              let summary = []
              if (deleted.accounts) summary.push(`${deleted.accounts} cuentas`)
              if (deleted.journal_entries) summary.push(`${deleted.journal_entries} asientos`)
              if (deleted.ledger_entries) summary.push(`${deleted.ledger_entries} entradas del mayor`)
              if (deleted.document_types) summary.push(`${deleted.document_types} tipos de documento`)
              if (deleted.users_updated) summary.push(`${deleted.users_updated} usuarios actualizados`)
              
              if (summary.length > 0) {
                await alerts.info(
                  'Datos Eliminados',
                  `También se eliminaron: ${summary.join(', ')}`
                )
              }
            }
            
            loadCompanies()
          } catch (error) {
            console.error('Error force deleting company:', error)
            toast.error('Error al eliminar empresa completamente')
          }
        }
      }
    }

    const getStatusColor = (status) => {
      const colors = {
        active: 'success',
        inactive: 'secondary',
        suspended: 'warning'
      }
      return colors[status] || 'secondary'
    }

    const formatDate = (date) => {
      return new Intl.DateTimeFormat('es-EC', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      }).format(new Date(date))
    }

    // Lifecycle
    onMounted(() => {
      loadCompanies()
    })

    return {
      companies,
      loading,
      currentPage,
      totalPages,
      visiblePages,
      filters,
      loadCompanies,
      debouncedSearch,
      changePage,
      clearFilters,
      editCompany,
      openSettings,
      deactivateCompany,
      activateCompany,
      forceDeleteCompany,
      getStatusColor,
      formatDate
    }
  }
}
</script>

<style scoped>
.companies-page .table-responsive {
  overflow: visible; /* permitir que el dropdown flote sobre la tabla */
}

.companies-page .card,
.companies-page .card-body,
.companies-page .table {
  overflow: visible; /* evitar recortes por contenedores padres */
}

.companies-page .btn-group {
  position: relative; /* contexto para posicionamiento del dropdown */
}

.companies-page .dropdown-menu {
  z-index: 3000; /* asegurar que quede por encima de la tabla y sombras */
}

.table th {
  border-top: none;
  font-weight: 600;
  color: #5a5c69;
}

.btn-group .btn {
  margin-right: 2px;
}

.btn-group .btn:last-child {
  margin-right: 0;
}

.btn-group .dropdown-menu {
  min-width: 200px;
}

.dropdown-item {
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
}

.dropdown-item i {
  width: 16px;
  text-align: center;
}

.dropdown-item:hover {
  background-color: var(--bs-gray-100);
}

.dropdown-item.text-danger:hover {
  background-color: var(--bs-danger);
  color: white !important;
}

.dropdown-item.text-warning:hover {
  background-color: var(--bs-warning);
  color: white !important;
}

.dropdown-item.text-success:hover {
  background-color: var(--bs-success);
  color: white !important;
}
</style>


