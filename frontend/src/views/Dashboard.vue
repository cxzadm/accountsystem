<template>
  <div class="dashboard">
    <!-- Page Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h1 class="h3 mb-0">Dashboard</h1>
        <p class="text-muted">Resumen general del sistema contable</p>
      </div>
      <div>
        <button class="btn btn-primary" @click="refreshData">
          <i class="fas fa-sync-alt me-2"></i>
          Actualizar
        </button>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="row mb-4">
      <div class="col-xl-3 col-md-6 mb-4">
        <div class="card border-left-primary shadow h-100 py-2">
          <div class="card-body">
            <div class="row no-gutters align-items-center">
              <div class="col mr-2">
                <div class="text-xs font-weight-bold text-primary text-uppercase mb-1">
                  Total Empresas
                </div>
                <div class="h5 mb-0 font-weight-bold text-gray-800">
                  {{ stats.companies }}
                </div>
              </div>
              <div class="col-auto">
                <i class="fas fa-building fa-2x text-gray-300"></i>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="col-xl-3 col-md-6 mb-4">
        <div class="card border-left-success shadow h-100 py-2">
          <div class="card-body">
            <div class="row no-gutters align-items-center">
              <div class="col mr-2">
                <div class="text-xs font-weight-bold text-success text-uppercase mb-1">
                  Asientos del Mes
                </div>
                <div class="h5 mb-0 font-weight-bold text-gray-800">
                  {{ stats.journalEntries }}
                </div>
              </div>
              <div class="col-auto">
                <i class="fas fa-book fa-2x text-gray-300"></i>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="col-xl-3 col-md-6 mb-4">
        <div class="card border-left-info shadow h-100 py-2">
          <div class="card-body">
            <div class="row no-gutters align-items-center">
              <div class="col mr-2">
                <div class="text-xs font-weight-bold text-info text-uppercase mb-1">
                  Cuentas Contables
                </div>
                <div class="h5 mb-0 font-weight-bold text-gray-800">
                  {{ stats.accounts }}
                </div>
              </div>
              <div class="col-auto">
                <i class="fas fa-list fa-2x text-gray-300"></i>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="col-xl-3 col-md-6 mb-4">
        <div class="card border-left-warning shadow h-100 py-2">
          <div class="card-body">
            <div class="row no-gutters align-items-center">
              <div class="col mr-2">
                <div class="text-xs font-weight-bold text-warning text-uppercase mb-1">
                  Usuarios Activos
                </div>
                <div class="h5 mb-0 font-weight-bold text-gray-800">
                  {{ stats.activeUsers }}
                </div>
              </div>
              <div class="col-auto">
                <i class="fas fa-users fa-2x text-gray-300"></i>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Charts Row -->
    <div class="row mb-4">
      <!-- Journal Entries Chart -->
      <div class="col-xl-8 col-lg-7">
        <div class="card shadow mb-4">
          <div class="card-header py-3 d-flex flex-row align-items-center justify-content-between">
            <h6 class="m-0 font-weight-bold text-primary">Asientos Contables por Mes</h6>
          </div>
          <div class="card-body">
            <div class="chart-area">
              <canvas id="journalChart" ref="journalChart"></canvas>
            </div>
          </div>
        </div>
      </div>

      <!-- Account Types Chart -->
      <div class="col-xl-4 col-lg-5">
        <div class="card shadow mb-4">
          <div class="card-header py-3 d-flex flex-row align-items-center justify-content-between">
            <h6 class="m-0 font-weight-bold text-primary">Tipos de Cuentas</h6>
          </div>
          <div class="card-body">
            <div class="chart-pie pt-4 pb-2">
              <canvas id="accountTypesChart" ref="accountTypesChart"></canvas>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Recent Activity -->
    <div class="row">
      <div class="col-lg-6">
        <div class="card shadow mb-4">
          <div class="card-header py-3">
            <h6 class="m-0 font-weight-bold text-primary">Actividad Reciente</h6>
          </div>
          <div class="card-body">
            <div class="list-group list-group-flush">
              <div 
                v-for="activity in recentActivity" 
                :key="activity.id"
                class="list-group-item d-flex justify-content-between align-items-start"
              >
                <div class="ms-2 me-auto">
                  <div class="fw-bold">{{ activity.description }}</div>
                  <small class="text-muted">{{ activity.user }} - {{ formatDate(activity.timestamp) }}</small>
                </div>
                <span class="badge bg-primary rounded-pill">{{ activity.module }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="col-lg-6">
        <div class="card shadow mb-4">
          <div class="card-header py-3">
            <h6 class="m-0 font-weight-bold text-primary">Acciones Rápidas</h6>
          </div>
          <div class="card-body">
            <div class="row">
              <div class="col-md-6 mb-3">
                <router-link to="/journal/new" class="btn btn-outline-primary w-100">
                  <i class="fas fa-plus me-2"></i>
                  Nuevo Asiento
                </router-link>
              </div>
              <div class="col-md-6 mb-3">
                <router-link to="/accounts/new" class="btn btn-outline-success w-100">
                  <i class="fas fa-list me-2"></i>
                  Nueva Cuenta
                </router-link>
              </div>
              <div class="col-md-6 mb-3">
                <router-link to="/reports" class="btn btn-outline-info w-100">
                  <i class="fas fa-chart-bar me-2"></i>
                  Ver Reportes
                </router-link>
              </div>
              <div class="col-md-6 mb-3">
                <router-link to="/sri" class="btn btn-outline-warning w-100">
                  <i class="fas fa-file-invoice me-2"></i>
                  Declaraciones SRI
                </router-link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useCompanyStore } from '@/stores/company'
import { useToast } from 'vue-toastification'
import { Chart, registerables } from 'chart.js'

Chart.register(...registerables)

export default {
  name: 'Dashboard',
  setup() {
    const authStore = useAuthStore()
    const companyStore = useCompanyStore()
    const toast = useToast()

    // Refs
    const journalChart = ref(null)
    const accountTypesChart = ref(null)

    // State
    const stats = reactive({
      companies: 0,
      journalEntries: 0,
      accounts: 0,
      activeUsers: 0
    })

    const recentActivity = ref([])

    // Methods
    const loadStats = async () => {
      try {
        // Solo cargar estadísticas si el usuario está autenticado
        if (!authStore.isAuthenticated) {
          console.warn('User not authenticated, skipping stats load')
          return
        }

        // Load companies
        const companies = await companyStore.fetchCompanies()
        stats.companies = companies.length

        // TODO: Load other stats from API
        stats.journalEntries = 0
        stats.accounts = 0
        stats.activeUsers = 0
      } catch (error) {
        console.error('Error loading stats:', error)
        toast.error('Error al cargar estadísticas')
      }
    }

    const loadRecentActivity = async () => {
      try {
        // TODO: Load recent activity from API
        recentActivity.value = [
          {
            id: 1,
            description: 'Usuario creado: Juan Pérez',
            user: 'admin',
            module: 'users',
            timestamp: new Date()
          },
          {
            id: 2,
            description: 'Asiento contable aprobado: AS-2024-000001',
            user: 'contador',
            module: 'journal',
            timestamp: new Date(Date.now() - 3600000)
          },
          {
            id: 3,
            description: 'Empresa creada: Empresa Ejemplo S.A.',
            user: 'admin',
            module: 'companies',
            timestamp: new Date(Date.now() - 7200000)
          }
        ]
      } catch (error) {
        console.error('Error loading recent activity:', error)
      }
    }

    const createCharts = () => {
      // Journal Entries Chart
      if (journalChart.value) {
        new Chart(journalChart.value, {
          type: 'line',
          data: {
            labels: ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun'],
            datasets: [{
              label: 'Asientos Contables',
              data: [12, 19, 3, 5, 2, 3],
              borderColor: 'rgb(75, 192, 192)',
              tension: 0.1
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false
          }
        })
      }

      // Account Types Chart
      if (accountTypesChart.value) {
        new Chart(accountTypesChart.value, {
          type: 'doughnut',
          data: {
            labels: ['Activos', 'Pasivos', 'Patrimonio', 'Ingresos', 'Gastos'],
            datasets: [{
              data: [30, 25, 20, 15, 10],
              backgroundColor: [
                '#FF6384',
                '#36A2EB',
                '#FFCE56',
                '#4BC0C0',
                '#9966FF'
              ]
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false
          }
        })
      }
    }

    const refreshData = async () => {
      await loadStats()
      await loadRecentActivity()
      toast.success('Datos actualizados')
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

    // Lifecycle
    onMounted(async () => {
      await loadStats()
      await loadRecentActivity()
      
      // Create charts after a short delay to ensure DOM is ready
      setTimeout(createCharts, 100)
    })

    return {
      stats,
      recentActivity,
      journalChart,
      accountTypesChart,
      refreshData,
      formatDate
    }
  }
}
</script>

<style scoped>
.border-left-primary {
  border-left: 0.25rem solid #4e73df !important;
}

.border-left-success {
  border-left: 0.25rem solid #1cc88a !important;
}

.border-left-info {
  border-left: 0.25rem solid #36b9cc !important;
}

.border-left-warning {
  border-left: 0.25rem solid #f6c23e !important;
}

.text-xs {
  font-size: 0.7rem;
}

.text-gray-300 {
  color: #dddfeb !important;
}

.text-gray-800 {
  color: #5a5c69 !important;
}

.chart-area {
  position: relative;
  height: 10rem;
}

.chart-pie {
  position: relative;
  height: 15rem;
}

.list-group-item {
  border: none;
  border-bottom: 1px solid #e3e6f0;
}

.list-group-item:last-child {
  border-bottom: none;
}
</style>
