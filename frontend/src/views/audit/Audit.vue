<template>
  <div class="audit-page">
    <!-- Page Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h1 class="h3 mb-0">Auditoría del Sistema</h1>
        <p class="text-muted">Registro de actividades y cambios en el sistema</p>
      </div>
    </div>

    <!-- Filters -->
    <div class="card mb-4">
      <div class="card-body">
        <div class="row">
          <div class="col-md-3">
            <label class="form-label">Usuario</label>
            <select class="form-select" v-model="filters.user_id" @change="loadAuditLogs">
              <option value="">Todos los usuarios</option>
              <option v-for="user in users" :key="user.id" :value="user.id">
                {{ user.username }}
              </option>
            </select>
          </div>
          <div class="col-md-2">
            <label class="form-label">Acción</label>
            <select class="form-select" v-model="filters.action" @change="loadAuditLogs">
              <option value="">Todas</option>
              <option value="create">Crear</option>
              <option value="read">Leer</option>
              <option value="update">Actualizar</option>
              <option value="delete">Eliminar</option>
              <option value="login">Login</option>
              <option value="logout">Logout</option>
              <option value="approve">Aprobar</option>
              <option value="reject">Rechazar</option>
              <option value="export">Exportar</option>
            </select>
          </div>
          <div class="col-md-2">
            <label class="form-label">Módulo</label>
            <select class="form-select" v-model="filters.module" @change="loadAuditLogs">
              <option value="">Todos</option>
              <option value="auth">Autenticación</option>
              <option value="users">Usuarios</option>
              <option value="companies">Empresas</option>
              <option value="accounts">Cuentas</option>
              <option value="journal">Diario</option>
              <option value="reports">Reportes</option>
              <option value="sri">SRI</option>
            </select>
          </div>
          <div class="col-md-2">
            <label class="form-label">Fecha Inicio</label>
            <input
              type="date"
              class="form-control"
              v-model="filters.start_date"
              @change="loadAuditLogs"
            />
          </div>
          <div class="col-md-2">
            <label class="form-label">Fecha Fin</label>
            <input
              type="date"
              class="form-control"
              v-model="filters.end_date"
              @change="loadAuditLogs"
            />
          </div>
          <div class="col-md-1 d-flex align-items-end">
            <button class="btn btn-outline-secondary w-100" @click="clearFilters">
              <i class="fas fa-times"></i>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Audit Logs Table -->
    <div class="card">
      <div class="card-body">
        <div class="table-responsive">
          <table class="table table-hover">
            <thead>
              <tr>
                <th>Usuario</th>
                <th>Acción</th>
                <th>Módulo</th>
                <th>Descripción</th>
                <th>IP</th>
                <th>Fecha</th>
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
              <tr v-else-if="auditLogs.length === 0">
                <td colspan="7" class="text-center py-4 text-muted">
                  No se encontraron registros de auditoría
                </td>
              </tr>
              <tr v-else v-for="log in auditLogs" :key="log.id">
                <td>
                  <div class="d-flex align-items-center">
                    <i class="fas fa-user-circle fa-2x text-muted me-2"></i>
                    <div>
                      <strong>{{ log.username }}</strong>
                    </div>
                  </div>
                </td>
                <td>
                  <span :class="`badge bg-${getActionColor(log.action)}`">
                    {{ log.action }}
                  </span>
                </td>
                <td>
                  <span :class="`badge bg-${getModuleColor(log.module)}`">
                    {{ log.module }}
                  </span>
                </td>
                <td>
                  <div>
                    <strong>{{ log.description }}</strong>
                    <div v-if="log.resource_type" class="text-muted small">
                      Recurso: {{ log.resource_type }}
                    </div>
                  </div>
                </td>
                <td>
                  <code>{{ log.ip_address }}</code>
                </td>
                <td>
                  <div>
                    {{ formatDate(log.timestamp) }}
                    <div class="text-muted small">
                      {{ formatTime(log.timestamp) }}
                    </div>
                  </div>
                </td>
                <td>
                  <button
                    class="btn btn-sm btn-outline-primary"
                    @click="viewDetails(log)"
                    title="Ver Detalles"
                  >
                    <i class="fas fa-eye"></i>
                  </button>
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

    <!-- Details Modal -->
    <div class="modal fade" id="auditDetailsModal" tabindex="-1">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Detalles de Auditoría</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body" v-if="selectedLog">
            <div class="row">
              <div class="col-md-6">
                <h6>Información General</h6>
                <ul class="list-unstyled">
                  <li><strong>Usuario:</strong> {{ selectedLog.username }}</li>
                  <li><strong>Acción:</strong> {{ selectedLog.action }}</li>
                  <li><strong>Módulo:</strong> {{ selectedLog.module }}</li>
                  <li><strong>Descripción:</strong> {{ selectedLog.description }}</li>
                  <li><strong>IP:</strong> {{ selectedLog.ip_address }}</li>
                  <li><strong>Fecha:</strong> {{ formatDateTime(selectedLog.timestamp) }}</li>
                </ul>
              </div>
              <div class="col-md-6">
                <h6>Detalles Técnicos</h6>
                <ul class="list-unstyled">
                  <li><strong>ID Recurso:</strong> {{ selectedLog.resource_id || 'N/A' }}</li>
                  <li><strong>Tipo Recurso:</strong> {{ selectedLog.resource_type || 'N/A' }}</li>
                  <li><strong>Empresa:</strong> {{ selectedLog.company_id || 'N/A' }}</li>
                </ul>
              </div>
            </div>
            
            <div v-if="selectedLog.old_values || selectedLog.new_values" class="mt-4">
              <h6>Cambios Realizados</h6>
              <div class="row">
                <div class="col-md-6" v-if="selectedLog.old_values">
                  <h6 class="text-danger">Valores Anteriores</h6>
                  <pre class="bg-light p-3 rounded">{{ JSON.stringify(selectedLog.old_values, null, 2) }}</pre>
                </div>
                <div class="col-md-6" v-if="selectedLog.new_values">
                  <h6 class="text-success">Valores Nuevos</h6>
                  <pre class="bg-light p-3 rounded">{{ JSON.stringify(selectedLog.new_values, null, 2) }}</pre>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { useToast } from 'vue-toastification'
import api from '@/services/api'

export default {
  name: 'Audit',
  setup() {
    const toast = useToast()

    // State
    const auditLogs = ref([])
    const users = ref([])
    const loading = ref(false)
    const currentPage = ref(1)
    const totalPages = ref(1)
    const selectedLog = ref(null)
    const pageSize = 20

    const filters = reactive({
      user_id: '',
      action: '',
      module: '',
      start_date: '',
      end_date: ''
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
    const loadAuditLogs = async () => {
      loading.value = true
      try {
        const params = {
          skip: (currentPage.value - 1) * pageSize,
          limit: pageSize,
          ...filters
        }

        const response = await api.get('/reports/auditoria', { params })
        auditLogs.value = response.data.logs
        totalPages.value = Math.ceil(response.data.total / pageSize)
      } catch (error) {
        console.error('Error loading audit logs:', error)
        toast.error('Error al cargar logs de auditoría')
      } finally {
        loading.value = false
      }
    }

    const loadUsers = async () => {
      try {
        const response = await api.get('/users', { params: { limit: 1000 } })
        users.value = response.data
      } catch (error) {
        console.error('Error loading users:', error)
      }
    }

    const changePage = (page) => {
      if (page >= 1 && page <= totalPages.value) {
        currentPage.value = page
        loadAuditLogs()
      }
    }

    const clearFilters = () => {
      filters.user_id = ''
      filters.action = ''
      filters.module = ''
      filters.start_date = ''
      filters.end_date = ''
      currentPage.value = 1
      loadAuditLogs()
    }

    const viewDetails = (log) => {
      selectedLog.value = log
      // Show modal using Bootstrap
      const modal = new bootstrap.Modal(document.getElementById('auditDetailsModal'))
      modal.show()
    }

    const getActionColor = (action) => {
      const colors = {
        create: 'success',
        read: 'info',
        update: 'warning',
        delete: 'danger',
        login: 'primary',
        logout: 'secondary',
        approve: 'success',
        reject: 'danger',
        export: 'info'
      }
      return colors[action] || 'secondary'
    }

    const getModuleColor = (module) => {
      const colors = {
        auth: 'primary',
        users: 'success',
        companies: 'info',
        accounts: 'warning',
        journal: 'danger',
        reports: 'secondary',
        sri: 'dark'
      }
      return colors[module] || 'secondary'
    }

    const formatDate = (date) => {
      return new Intl.DateTimeFormat('es-EC', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      }).format(new Date(date))
    }

    const formatTime = (date) => {
      return new Intl.DateTimeFormat('es-EC', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      }).format(new Date(date))
    }

    const formatDateTime = (date) => {
      return new Intl.DateTimeFormat('es-EC', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      }).format(new Date(date))
    }

    // Lifecycle
    onMounted(() => {
      loadUsers()
      loadAuditLogs()
    })

    return {
      auditLogs,
      users,
      loading,
      currentPage,
      totalPages,
      visiblePages,
      selectedLog,
      filters,
      loadAuditLogs,
      changePage,
      clearFilters,
      viewDetails,
      getActionColor,
      getModuleColor,
      formatDate,
      formatTime,
      formatDateTime
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

code {
  background-color: #f8f9fa;
  padding: 0.2rem 0.4rem;
  border-radius: 0.25rem;
  font-size: 0.875em;
}

pre {
  font-size: 0.875rem;
  max-height: 200px;
  overflow-y: auto;
}
</style>










