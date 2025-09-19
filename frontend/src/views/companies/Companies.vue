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
                    <button
                      class="btn btn-sm btn-outline-danger"
                      @click="deleteCompany(company)"
                      title="Eliminar"
                    >
                      <i class="fas fa-trash"></i>
                    </button>
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

    const deleteCompany = async (company) => {
      if (confirm(`¿Estás seguro de eliminar la empresa ${company.name}?`)) {
        try {
          await api.delete(`/companies/${company.id}`)
          toast.success('Empresa eliminada exitosamente')
          loadCompanies()
        } catch (error) {
          console.error('Error deleting company:', error)
          toast.error('Error al eliminar empresa')
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
      deleteCompany,
      getStatusColor,
      formatDate
    }
  }
}
</script>

<style scoped>
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
</style>


