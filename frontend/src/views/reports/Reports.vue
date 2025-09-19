<template>
  <div class="reports-page">
    <!-- Page Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h1 class="h3 mb-0">Reportes Contables</h1>
        <p class="text-muted">Genera reportes financieros y contables</p>
      </div>
    </div>

    <!-- Report Cards -->
    <div class="row mb-4">
      <div class="col-md-4 mb-3">
        <div class="card h-100">
          <div class="card-body text-center">
            <i class="fas fa-balance-scale fa-3x text-primary mb-3"></i>
            <h5 class="card-title">Balance General</h5>
            <p class="card-text">Estado de la situación financiera de la empresa</p>
            <button class="btn btn-primary" @click="generateBalanceGeneral">
              <i class="fas fa-file-pdf me-2"></i>
              Generar
            </button>
          </div>
        </div>
      </div>

      <div class="col-md-4 mb-3">
        <div class="card h-100">
          <div class="card-body text-center">
            <i class="fas fa-chart-line fa-3x text-success mb-3"></i>
            <h5 class="card-title">Estado de Resultados</h5>
            <p class="card-text">Rendimiento financiero del período</p>
            <button class="btn btn-success" @click="generateEstadoResultados">
              <i class="fas fa-file-pdf me-2"></i>
              Generar
            </button>
          </div>
        </div>
      </div>

      <div class="col-md-4 mb-3">
        <div class="card h-100">
          <div class="card-body text-center">
            <i class="fas fa-book fa-3x text-info mb-3"></i>
            <h5 class="card-title">Libro Mayor</h5>
            <p class="card-text">Movimientos detallados por cuenta</p>
            <button class="btn btn-info" @click="generateLibroMayor">
              <i class="fas fa-file-pdf me-2"></i>
              Generar
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Report Parameters -->
    <div class="card mb-4" v-if="showParameters">
      <div class="card-header">
        <h6 class="mb-0">Parámetros del Reporte</h6>
      </div>
      <div class="card-body">
        <div class="row">
          <div class="col-md-4">
            <label class="form-label">Fecha de Corte</label>
            <input
              type="date"
              class="form-control"
              v-model="reportParams.as_of_date"
            />
          </div>
          <div class="col-md-4">
            <label class="form-label">Fecha Inicio</label>
            <input
              type="date"
              class="form-control"
              v-model="reportParams.start_date"
            />
          </div>
          <div class="col-md-4">
            <label class="form-label">Fecha Fin</label>
            <input
              type="date"
              class="form-control"
              v-model="reportParams.end_date"
            />
          </div>
        </div>
        <div class="row mt-3">
          <div class="col-md-6">
            <label class="form-label">Formato de Exportación</label>
            <select class="form-select" v-model="reportParams.format">
              <option value="pdf">PDF</option>
              <option value="excel">Excel</option>
            </select>
          </div>
          <div class="col-md-6 d-flex align-items-end">
            <button class="btn btn-primary me-2" @click="generateReport">
              <i class="fas fa-download me-2"></i>
              Generar Reporte
            </button>
            <button class="btn btn-secondary" @click="cancelReport">
              Cancelar
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Recent Reports -->
    <div class="card">
      <div class="card-header">
        <h6 class="mb-0">Reportes Recientes</h6>
      </div>
      <div class="card-body">
        <div class="table-responsive">
          <table class="table table-hover">
            <thead>
              <tr>
                <th>Tipo</th>
                <th>Período</th>
                <th>Fecha Generación</th>
                <th>Formato</th>
                <th>Estado</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="loading">
                <td colspan="6" class="text-center py-4">
                  <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Cargando...</span>
                  </div>
                </td>
              </tr>
              <tr v-else-if="recentReports.length === 0">
                <td colspan="6" class="text-center py-4 text-muted">
                  No hay reportes generados
                </td>
              </tr>
              <tr v-else v-for="report in recentReports" :key="report.id">
                <td>
                  <span :class="`badge bg-${getReportTypeColor(report.type)}`">
                    {{ report.type }}
                  </span>
                </td>
                <td>{{ report.period }}</td>
                <td>{{ formatDate(report.created_at) }}</td>
                <td>
                  <span class="badge bg-secondary">{{ report.format.toUpperCase() }}</span>
                </td>
                <td>
                  <span :class="`badge bg-${getStatusColor(report.status)}`">
                    {{ report.status }}
                  </span>
                </td>
                <td>
                  <div class="btn-group" role="group">
                    <button
                      class="btn btn-sm btn-outline-primary"
                      @click="downloadReport(report)"
                      title="Descargar"
                    >
                      <i class="fas fa-download"></i>
                    </button>
                    <button
                      class="btn btn-sm btn-outline-danger"
                      @click="deleteReport(report)"
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
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { useToast } from 'vue-toastification'
import { useCompanyStore } from '@/stores/company'
import api from '@/services/api'

export default {
  name: 'Reports',
  setup() {
    const toast = useToast()
    const companyStore = useCompanyStore()

    // State
    const loading = ref(false)
    const showParameters = ref(false)
    const currentReportType = ref('')
    const recentReports = ref([])

    const reportParams = reactive({
      as_of_date: new Date().toISOString().split('T')[0],
      start_date: new Date(new Date().getFullYear(), 0, 1).toISOString().split('T')[0],
      end_date: new Date().toISOString().split('T')[0],
      format: 'pdf'
    })

    // Methods
    const generateBalanceGeneral = () => {
      currentReportType.value = 'balance-general'
      showParameters.value = true
    }

    const generateEstadoResultados = () => {
      currentReportType.value = 'estado-resultados'
      showParameters.value = true
    }

    const generateLibroMayor = () => {
      currentReportType.value = 'libro-mayor'
      showParameters.value = true
    }

    const generateReport = async () => {
      if (!companyStore.getCurrentCompany()) {
        toast.error('Selecciona una empresa primero')
        return
      }

      loading.value = true
      try {
        const params = {
          company_id: companyStore.getCurrentCompany().id,
          ...reportParams
        }

        const response = await api.post(`/reports/export/${currentReportType.value}`, null, { params })
        
        toast.success('Reporte generado exitosamente')
        showParameters.value = false
        loadRecentReports()
      } catch (error) {
        console.error('Error generating report:', error)
        toast.error('Error al generar reporte')
      } finally {
        loading.value = false
      }
    }

    const cancelReport = () => {
      showParameters.value = false
      currentReportType.value = ''
    }

    const loadRecentReports = async () => {
      // TODO: Implement load recent reports from API
      recentReports.value = [
        {
          id: 1,
          type: 'Balance General',
          period: '2024-01',
          created_at: new Date(),
          format: 'pdf',
          status: 'completed'
        },
        {
          id: 2,
          type: 'Estado de Resultados',
          period: '2024-01',
          created_at: new Date(Date.now() - 86400000),
          format: 'excel',
          status: 'completed'
        }
      ]
    }

    const downloadReport = (report) => {
      // TODO: Implement download functionality
      toast.info('Descargando reporte...')
    }

    const deleteReport = (report) => {
      if (confirm(`¿Estás seguro de eliminar el reporte ${report.type}?`)) {
        // TODO: Implement delete functionality
        toast.success('Reporte eliminado')
        loadRecentReports()
      }
    }

    const getReportTypeColor = (type) => {
      const colors = {
        'Balance General': 'primary',
        'Estado de Resultados': 'success',
        'Libro Mayor': 'info'
      }
      return colors[type] || 'secondary'
    }

    const getStatusColor = (status) => {
      const colors = {
        completed: 'success',
        processing: 'warning',
        error: 'danger'
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

    // Lifecycle
    onMounted(() => {
      loadRecentReports()
    })

    return {
      loading,
      showParameters,
      currentReportType,
      recentReports,
      reportParams,
      generateBalanceGeneral,
      generateEstadoResultados,
      generateLibroMayor,
      generateReport,
      cancelReport,
      downloadReport,
      deleteReport,
      getReportTypeColor,
      getStatusColor,
      formatDate
    }
  }
}
</script>

<style scoped>
.card {
  transition: transform 0.2s ease-in-out;
}

.card:hover {
  transform: translateY(-2px);
}

.btn-group .btn {
  margin-right: 2px;
}

.btn-group .btn:last-child {
  margin-right: 0;
}
</style>










