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
          <!-- Local Filters similar to Accounts.vue -->
          <div class="card mb-3">
            <div class="card-body py-2">
              <div class="row g-2">
                <div class="col-md-6">
                  <label class="form-label small">Búsqueda Inteligente</label>
                  <div class="input-group">
                    <input
                      type="text"
                      class="form-control form-control-sm"
                      v-model="filters.search"
                      placeholder="Código, nombre o saldo:>1000 / :=0 / <0"
                    />
                    <button 
                      class="btn btn-outline-secondary btn-sm dropdown-toggle" 
                      type="button" 
                      data-bs-toggle="dropdown"
                      title="Búsquedas rápidas"
                    >
                      <i class="fas fa-search"></i>
                    </button>
                    <ul class="dropdown-menu dropdown-menu-end">
                      <li><h6 class="dropdown-header">Rápidos</h6></li>
                      <template v-if="currentReportType === 'balance-general'">
                        <li><a class="dropdown-item" href="#" @click.prevent="applyQuickCategory('1')"><i class="fas fa-building me-2 text-primary"></i>Activo</a></li>
                        <li><a class="dropdown-item" href="#" @click.prevent="applyQuickCategory('2')"><i class="fas fa-credit-card me-2 text-warning"></i>Pasivo</a></li>
                        <li><a class="dropdown-item" href="#" @click.prevent="applyQuickCategory('3')"><i class="fas fa-chart-line me-2 text-info"></i>Patrimonio</a></li>
                      </template>
                      <template v-else-if="currentReportType === 'estado-resultados'">
                        <li><a class="dropdown-item" href="#" @click.prevent="applyQuickCategory('4')"><i class="fas fa-arrow-up me-2 text-success"></i>Ingresos</a></li>
                        <li><a class="dropdown-item" href="#" @click.prevent="applyQuickCategory('5')"><i class="fas fa-arrow-down me-2 text-danger"></i>Gastos</a></li>
                        <li><a class="dropdown-item" href="#" @click.prevent="applyQuickCategory('6')"><i class="fas fa-equals me-2 text-secondary"></i>Resultados</a></li>
                      </template>
                      <li><hr class="dropdown-divider"></li>
                      <li><a class="dropdown-item" href="#" @click.prevent="applyQuickSearch('saldo:>0')"><i class="fas fa-plus-circle me-2 text-success"></i>Saldo positivo</a></li>
                      <li><a class="dropdown-item" href="#" @click.prevent="applyQuickSearch('saldo:<0')"><i class="fas fa-minus-circle me-2 text-danger"></i>Saldo negativo</a></li>
                      <li><a class="dropdown-item" href="#" @click.prevent="applyQuickSearch('saldo:=0')"><i class="fas fa-equals me-2 text-muted"></i>Saldo cero</a></li>
                    </ul>
                    <button 
                      class="btn btn-outline-secondary btn-sm" 
                      type="button" 
                      @click="showSearchHelp = !showSearchHelp"
                      title="Ayuda de búsqueda"
                    >
                      <i class="fas fa-question-circle"></i>
                    </button>
                  </div>
                  <div v-if="showSearchHelp" class="mt-1">
                    <small class="text-muted">
                      <strong>Ejemplos:</strong>
                      <code>1.1</code>, <code>caja</code>, <code>saldo:>1000</code>, <code>saldo:=0</code>
                    </small>
                  </div>
                </div>
                <div class="col-md-3">
                  <label class="form-label small">Categoría</label>
                  <select class="form-select form-select-sm" v-model="filters.category">
                    <option value="">Todas</option>
                    <option v-if="currentReportType === 'balance-general'" value="1">1 - Activo</option>
                    <option v-if="currentReportType === 'balance-general'" value="2">2 - Pasivo</option>
                    <option v-if="currentReportType === 'balance-general'" value="3">3 - Patrimonio</option>
                    <option v-if="currentReportType === 'estado-resultados'" value="4">4 - Ingresos</option>
                    <option v-if="currentReportType === 'estado-resultados'" value="5">5 - Gastos</option>
                    <option v-if="currentReportType === 'estado-resultados'" value="6">6 - Resultados</option>
                  </select>
                </div>
                <div class="col-md-3 d-flex align-items-end">
                  <button class="btn btn-outline-secondary btn-sm me-2" @click="clearLocalFilters">
                    <i class="fas fa-times me-1"></i>Limpiar
                  </button>
                </div>
              </div>
            </div>
          </div>
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

      <!-- Report Result -->
      <div class="card mb-4" v-if="reportResult">
        <div class="card-header d-flex justify-content-between align-items-center">
          <div>
            <h6 class="mb-0">{{ resultTitle }}</h6>
            <small class="text-muted" v-if="resultSubtitle">{{ resultSubtitle }}</small>
          </div>
          <div>
            <span class="badge bg-secondary" v-if="reportResult.empresa">Empresa: {{ reportResult.empresa }}</span>
          </div>
        </div>
        <div class="card-body">
          <div class="table-responsive">
            <table class="table table-hover table-sm mb-0">
              <thead class="table-light">
                <tr>
                  <th style="width: 120px;">Código</th>
                  <th>Cuenta</th>
                  <th style="width: 120px;">Grupo</th>
                  <th class="text-end" style="width: 160px;">Saldo</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="loading">
                  <td colspan="4" class="text-center py-3">
                    <div class="spinner-border spinner-border-sm text-primary" role="status">
                      <span class="visually-hidden">Cargando...</span>
                    </div>
                  </td>
                </tr>
                <tr v-else-if="filteredAccounts.length === 0">
                  <td colspan="4" class="text-center py-3 text-muted">No hay cuentas para mostrar</td>
                </tr>
                <tr v-else v-for="row in filteredAccounts" :key="row.id" :class="getRowClass(row)" class="align-middle">
                  <td><code class="small">{{ row.codigo }}</code></td>
                  <td>
                    <div class="small"><strong>{{ row.nombre }}</strong></div>
                  </td>
                  <td>
                    <span class="badge bg-light text-dark">{{ row.group_key }} - {{ row.group_desc }}</span>
                  </td>
                  <td class="text-end"><strong>{{ formatCurrency(row.saldo) }}</strong></td>
                </tr>
              </tbody>
              <tfoot v-if="groupTotalsList.length > 0" class="table-light">
                <tr v-for="gt in groupTotalsList" :key="gt.key">
                  <td colspan="3" class="text-end"><strong>Total {{ gt.key }} - {{ gt.descripcion }}</strong></td>
                  <td class="text-end"><strong>{{ formatCurrency(gt.total) }}</strong></td>
                </tr>
              </tfoot>
            </table>
          </div>

          <div v-if="currentReportType === 'estado-resultados'" class="mt-3">
            <div class="alert alert-info d-flex justify-content-between align-items-center">
              <div><strong>Utilidad Neta</strong></div>
              <div><strong>{{ formatCurrency(reportResult.utilidad_neta || 0) }}</strong></div>
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
  import { ref, reactive, onMounted, computed, watch } from 'vue'
  import { useToast } from 'vue-toastification'
  import { useCompanyStore } from '@/stores/company'
  import api from '@/services/api'
  import { debounce } from 'lodash-es'
  
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
      const reportResult = ref(null)
      const resultTitle = ref('')
      const resultSubtitle = ref('')
  
      const reportParams = reactive({
        as_of_date: new Date().toISOString().split('T')[0],
        start_date: new Date(new Date().getFullYear(), 0, 1).toISOString().split('T')[0],
        end_date: new Date().toISOString().split('T')[0],
        format: 'pdf'
      })

      // Local filters similar to Accounts.vue
      const filters = reactive({
        search: '',
        category: ''
      })
      const showSearchHelp = ref(false)

      const groupsList = computed(() => {
        if (!reportResult.value || !reportResult.value.grupos) return []
        return Object.keys(reportResult.value.grupos)
          .sort()
          .map((key) => ({ key, ...reportResult.value.grupos[key] }))
      })

      const flattenedAccounts = computed(() => {
        if (!reportResult.value || !reportResult.value.grupos) return []
        const rows = []
        for (const key of Object.keys(reportResult.value.grupos)) {
          const grp = reportResult.value.grupos[key] || { cuentas: [] }
          const cuentas = grp.cuentas || []
          for (const c of cuentas) {
            rows.push({
              ...c,
              group_key: key,
              group_desc: grp.descripcion || ''
            })
          }
        }
        return rows
      })

      const flattenedTotal = computed(() => {
        return flattenedAccounts.value.reduce((acc, r) => acc + Number(r.saldo || 0), 0)
      })

      const filteredAccounts = computed(() => {
        let rows = flattenedAccounts.value
        // Category filter by group key
        if (filters.category) {
          rows = rows.filter(r => r.group_key === filters.category)
        }

        // Intelligent search parsing (simple): saldo operators and text contains
        const q = (filters.search || '').trim()
        if (q) {
          const saldoMatch = q.match(/^saldo:\s*([><=]+)\s*(\d+(?:\.\d+)?)$/i)
          if (saldoMatch) {
            const operator = saldoMatch[1]
            const value = parseFloat(saldoMatch[2])
            rows = rows.filter(r => {
              const s = Number(r.saldo || 0)
              if (operator.includes('>')) return s > value
              if (operator.includes('<')) return s < value
              if (operator.includes('=')) return s === value
              return true
            })
          } else {
            const text = q.toLowerCase()
            rows = rows.filter(r =>
              (r.codigo || '').toLowerCase().includes(text) ||
              (r.nombre || '').toLowerCase().includes(text)
            )
          }
        }
        return rows
      })

      const filteredTotal = computed(() => {
        return filteredAccounts.value.reduce((acc, r) => acc + Number(r.saldo || 0), 0)
      })

      const groupTotalsList = computed(() => {
        if (!reportResult.value || !reportResult.value.grupos) return []
        const grupos = reportResult.value.grupos
        let keys = Object.keys(grupos)
        if (currentReportType.value === 'balance-general') keys = ['1','2','3']
        else if (currentReportType.value === 'estado-resultados') keys = ['4','5','6']
        return keys
          .filter(k => grupos[k])
          .map(k => ({ key: k, descripcion: grupos[k].descripcion, total: grupos[k].total }))
      })

      // Visual helpers: detect if a row is parent (has children by code pattern +2)
      const parentCodeSet = computed(() => {
        const codes = (flattenedAccounts.value || []).map(r => r.codigo).filter(Boolean)
        const set = new Set()
        for (const code of codes) {
          const expectedLen = (code || '').length + 2
          if (codes.some(c => c && c.startsWith(code) && c.length === expectedLen)) {
            set.add(code)
          }
        }
        return set
      })

      const getRowClass = (row) => {
        if (!row || !row.codigo) return 'align-middle'
        return parentCodeSet.value.has(row.codigo) ? 'table-info align-middle' : 'align-middle'
      }
  
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
          const companyId = companyStore.getCurrentCompany().id
          if (currentReportType.value === 'balance-general') {
            // Si el usuario define Fecha Fin, úsala como fecha de corte (como en Accounts)
            const cutoff = reportParams.end_date || reportParams.as_of_date
            const { data } = await api.get('/reports/balance-general', {
              params: { company_id: companyId, as_of_date: cutoff }
            })
            reportResult.value = data
            resultTitle.value = 'Balance General (Estado de Situación Financiera)'
            resultSubtitle.value = `Fecha de corte: ${cutoff}`
          } else if (currentReportType.value === 'estado-resultados') {
            const { data } = await api.get('/reports/estado-resultados', {
              params: {
                company_id: companyId,
                start_date: reportParams.start_date,
                end_date: reportParams.end_date
              }
            })
            reportResult.value = data
            resultTitle.value = 'Estado de Resultados'
            resultSubtitle.value = `Período: ${reportParams.start_date} a ${reportParams.end_date}`
          } else if (currentReportType.value === 'libro-mayor') {
            const { data } = await api.get('/reports/libro-mayor', {
              params: {
                company_id: companyId,
                start_date: reportParams.start_date,
                end_date: reportParams.end_date
              }
            })
            reportResult.value = data
            resultTitle.value = 'Libro Mayor'
            resultSubtitle.value = `Período: ${reportParams.start_date} a ${reportParams.end_date}`
          }

          toast.success('Reporte generado exitosamente')
          loadRecentReports()
        } catch (error) {
          console.error('Error generating report:', error)
          toast.error('Error al generar reporte')
        } finally {
          loading.value = false
        }
      }

      // Auto-refresh on date changes with debounce
      let autoTimer = null
      const scheduleAutoRefresh = () => {
        if (!currentReportType.value) return
        if (autoTimer) clearTimeout(autoTimer)
        autoTimer = setTimeout(() => {
          generateReport()
        }, 400)
      }

      watch(() => reportParams.as_of_date, () => {
        if (currentReportType.value === 'balance-general') scheduleAutoRefresh()
      })
      watch(() => reportParams.start_date, () => {
        if (currentReportType.value === 'estado-resultados' || currentReportType.value === 'libro-mayor') scheduleAutoRefresh()
      })
      watch(() => reportParams.end_date, () => {
        if (currentReportType.value === 'estado-resultados' || currentReportType.value === 'libro-mayor') scheduleAutoRefresh()
      })
  
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

      // Local filter helpers
      const applyQuickCategory = (cat) => { filters.category = cat }
      const applyQuickSearch = (term) => { filters.search = term }
      const clearLocalFilters = () => { filters.search = ''; filters.category = '' }
  
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

      const formatCurrency = (value) => {
        try {
          return new Intl.NumberFormat('es-EC', { style: 'currency', currency: 'USD' }).format(Number(value || 0))
        } catch (e) {
          return value
        }
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
        reportResult,
        resultTitle,
        resultSubtitle,
        groupsList,
        flattenedAccounts,
        flattenedTotal,
        filteredAccounts,
        filteredTotal,
        groupTotalsList,
        filters,
        showSearchHelp,
        reportParams,
        generateBalanceGeneral,
        generateEstadoResultados,
        generateLibroMayor,
        generateReport,
        applyQuickCategory,
        applyQuickSearch,
        clearLocalFilters,
        cancelReport,
        downloadReport,
        deleteReport,
        getReportTypeColor,
        getStatusColor,
        formatDate,
        formatCurrency
        ,
        getRowClass
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