<template>
  <div class="users-page">
    <!-- Page Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h1 class="h3 mb-0">Gestión de Usuarios</h1>
        <p class="text-muted">Administra los usuarios del sistema</p>
      </div>
      <div>
        <router-link to="/users/new" class="btn btn-primary">
          <i class="fas fa-plus me-2"></i>
          Nuevo Usuario
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
              placeholder="Nombre, usuario o email..."
              @input="debouncedSearch"
            />
          </div>
          <div class="col-md-3">
            <label class="form-label">Rol</label>
            <select class="form-select" v-model="filters.role" @change="loadUsers">
              <option value="">Todos los roles</option>
              <option value="admin">Administrador</option>
              <option value="contador">Contador</option>
              <option value="auditor">Auditor</option>
              <option value="interno">Interno</option>
            </select>
          </div>
          <div class="col-md-3">
            <label class="form-label">Estado</label>
            <select class="form-select" v-model="filters.status" @change="loadUsers">
              <option value="">Todos los estados</option>
              <option value="active">Activo</option>
              <option value="inactive">Inactivo</option>
              <option value="suspended">Suspendido</option>
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

    <!-- Users Table -->
    <div class="card">
      <div class="card-body">
        <div class="table-responsive">
          <table class="table table-hover">
            <thead>
              <tr>
                <th>Usuario</th>
                <th>Nombre</th>
                <th>Email</th>
                <th>Rol</th>
                <th>Estado</th>
                <th>Último Login</th>
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
              <tr v-else-if="users.length === 0">
                <td colspan="7" class="text-center py-4 text-muted">
                  No se encontraron usuarios
                </td>
              </tr>
              <tr v-else v-for="user in users" :key="user.id">
                <td>
                  <div class="d-flex align-items-center">
                    <i class="fas fa-user-circle fa-2x text-muted me-3"></i>
                    <div>
                      <strong>{{ user.username }}</strong>
                    </div>
                  </div>
                </td>
                <td>{{ user.first_name }} {{ user.last_name }}</td>
                <td>{{ user.email }}</td>
                <td>
                  <span :class="`badge badge-${user.role}`">
                    {{ user.role }}
                  </span>
                </td>
                <td>
                  <span :class="`badge bg-${getStatusColor(user.status)}`">
                    {{ user.status }}
                  </span>
                </td>
                <td>
                  <span v-if="user.last_login">
                    {{ formatDate(user.last_login) }}
                  </span>
                  <span v-else class="text-muted">Nunca</span>
                </td>
                <td>
                  <div class="btn-group" role="group">
                    <button
                      class="btn btn-sm btn-outline-primary"
                      @click="editUser(user)"
                      title="Editar"
                    >
                      <i class="fas fa-edit"></i>
                    </button>
                    <button
                      class="btn btn-sm btn-outline-danger"
                      @click="deleteUser(user)"
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
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'vue-toastification'
import api from '@/services/api'
import { debounce } from 'lodash-es'

export default {
  name: 'Users',
  setup() {
    const router = useRouter()
    const toast = useToast()

    // State
    const users = ref([])
    const loading = ref(false)
    const currentPage = ref(1)
    const totalPages = ref(1)
    const pageSize = 10

    const filters = reactive({
      search: '',
      role: '',
      status: ''
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
    const loadUsers = async () => {
      loading.value = true
      try {
        const params = {
          skip: (currentPage.value - 1) * pageSize,
          limit: pageSize,
          ...filters
        }

        const response = await api.get('/users', { params })
        users.value = response.data
        totalPages.value = Math.ceil(response.data.length / pageSize)
      } catch (error) {
        console.error('Error loading users:', error)
        toast.error('Error al cargar usuarios')
      } finally {
        loading.value = false
      }
    }

    const debouncedSearch = debounce(() => {
      currentPage.value = 1
      loadUsers()
    }, 500)

    const changePage = (page) => {
      if (page >= 1 && page <= totalPages.value) {
        currentPage.value = page
        loadUsers()
      }
    }

    const clearFilters = () => {
      filters.search = ''
      filters.role = ''
      filters.status = ''
      currentPage.value = 1
      loadUsers()
    }

    const editUser = (user) => {
      router.push(`/users/${user.id}/edit`)
    }

    const deleteUser = async (user) => {
      if (confirm(`¿Estás seguro de eliminar al usuario ${user.username}?`)) {
        try {
          await api.delete(`/users/${user.id}`)
          toast.success('Usuario eliminado exitosamente')
          loadUsers()
        } catch (error) {
          console.error('Error deleting user:', error)
          toast.error('Error al eliminar usuario')
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
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      }).format(new Date(date))
    }

    // Watchers
    watch(filters, () => {
      currentPage.value = 1
    })

    // Lifecycle
    onMounted(() => {
      loadUsers()
    })

    return {
      users,
      loading,
      currentPage,
      totalPages,
      visiblePages,
      filters,
      loadUsers,
      debouncedSearch,
      changePage,
      clearFilters,
      editUser,
      deleteUser,
      getStatusColor,
      formatDate
    }
  }
}
</script>

<style scoped>
.badge-admin {
  background-color: #dc3545;
}

.badge-contador {
  background-color: #28a745;
}

.badge-auditor {
  background-color: #17a2b8;
}

.badge-interno {
  background-color: #6c757d;
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
</style>










