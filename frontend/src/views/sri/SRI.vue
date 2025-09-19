<template>
  <div class="sri-page">
    <!-- Page Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h1 class="h3 mb-0">Declaraciones SRI</h1>
        <p class="text-muted">Gestiona las declaraciones fiscales del SRI</p>
      </div>
    </div>

    <!-- SRI Forms -->
    <div class="row mb-4">
      <div class="col-md-4 mb-3">
        <div class="card h-100">
          <div class="card-body text-center">
            <i class="fas fa-file-invoice fa-3x text-warning mb-3"></i>
            <h5 class="card-title">Formulario 103</h5>
            <p class="card-text">Retención en la Fuente</p>
            <button class="btn btn-warning" @click="generateFormulario103">
              <i class="fas fa-file-pdf me-2"></i>
              Generar
            </button>
          </div>
        </div>
      </div>

      <div class="col-md-4 mb-3">
        <div class="card h-100">
          <div class="card-body text-center">
            <i class="fas fa-receipt fa-3x text-info mb-3"></i>
            <h5 class="card-title">Formulario 104</h5>
            <p class="card-text">Declaración de IVA</p>
            <button class="btn btn-info" @click="generateFormulario104">
              <i class="fas fa-file-pdf me-2"></i>
              Generar
            </button>
          </div>
        </div>
      </div>

      <div class="col-md-4 mb-3">
        <div class="card h-100">
          <div class="card-body text-center">
            <i class="fas fa-users fa-3x text-success mb-3"></i>
            <h5 class="card-title">RDEP</h5>
            <p class="card-text">Régimen de Dependencia</p>
            <button class="btn btn-success" @click="generateRDEP">
              <i class="fas fa-file-pdf me-2"></i>
              Generar
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Form Parameters -->
    <div class="card mb-4" v-if="showParameters">
      <div class="card-header">
        <h6 class="mb-0">Parámetros del Formulario</h6>
      </div>
      <div class="card-body">
        <div class="row">
          <div class="col-md-4">
            <label class="form-label">Período</label>
            <input
              type="month"
              class="form-control"
              v-model="formParams.period"
            />
          </div>
          <div class="col-md-4">
            <label class="form-label">Año (para RDEP)</label>
            <input
              type="number"
              class="form-control"
              v-model="formParams.year"
              min="2020"
              :max="new Date().getFullYear()"
            />
          </div>
          <div class="col-md-4 d-flex align-items-end">
            <button class="btn btn-primary me-2" @click="generateForm">
              <i class="fas fa-download me-2"></i>
              Generar Formulario
            </button>
            <button class="btn btn-secondary" @click="cancelForm">
              Cancelar
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- SRI Status -->
    <div class="card mb-4">
      <div class="card-header">
        <h6 class="mb-0">Estado de Envíos SRI</h6>
      </div>
      <div class="card-body">
        <div class="table-responsive">
          <table class="table table-hover">
            <thead>
              <tr>
                <th>Formulario</th>
                <th>Período</th>
                <th>Fecha Envío</th>
                <th>Estado</th>
                <th>Número Referencia</th>
                <th>Observaciones</th>
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
              <tr v-else-if="sriStatus.length === 0">
                <td colspan="7" class="text-center py-4 text-muted">
                  No hay envíos registrados
                </td>
              </tr>
              <tr v-else v-for="status in sriStatus" :key="status.id">
                <td>
                  <span :class="`badge bg-${getFormColor(status.formulario)}`">
                    {{ status.formulario }}
                  </span>
                </td>
                <td>{{ status.periodo }}</td>
                <td>{{ formatDate(status.fecha_envio) }}</td>
                <td>
                  <span :class="`badge bg-${getStatusColor(status.estado)}`">
                    {{ status.estado }}
                  </span>
                </td>
                <td>
                  <code>{{ status.numero_referencia }}</code>
                </td>
                <td>
                  <span v-if="status.observaciones" class="text-muted">
                    {{ status.observaciones }}
                  </span>
                  <span v-else class="text-muted">-</span>
                </td>
                <td>
                  <div class="btn-group" role="group">
                    <button
                      class="btn btn-sm btn-outline-primary"
                      @click="viewForm(status)"
                      title="Ver"
                    >
                      <i class="fas fa-eye"></i>
                    </button>
                    <button
                      class="btn btn-sm btn-outline-success"
                      @click="resendForm(status)"
                      title="Reenviar"
                      v-if="status.estado === 'rechazado'"
                    >
                      <i class="fas fa-paper-plane"></i>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- SRI Configuration -->
    <div class="card">
      <div class="card-header">
        <h6 class="mb-0">Configuración SRI</h6>
      </div>
      <div class="card-body">
        <div class="row">
          <div class="col-md-6">
            <h6>Información de la Empresa</h6>
            <ul class="list-unstyled">
              <li><strong>RUC:</strong> {{ sriConfig.ruc }}</li>
              <li><strong>Nombre:</strong> {{ sriConfig.nombre }}</li>
              <li><strong>Ambiente:</strong> 
                <span :class="`badge ${sriConfig.ambiente === 'produccion' ? 'bg-success' : 'bg-warning'}`">
                  {{ sriConfig.ambiente }}
                </span>
              </li>
            </ul>
          </div>
          <div class="col-md-6">
            <h6>Certificado Digital</h6>
            <ul class="list-unstyled">
              <li><strong>Número de Serie:</strong> {{ sriConfig.certificado_digital.numero_serie }}</li>
              <li><strong>Fecha Vencimiento:</strong> {{ formatDate(sriConfig.certificado_digital.fecha_vencimiento) }}</li>
              <li><strong>Estado:</strong> 
                <span :class="`badge ${sriConfig.certificado_digital.estado === 'activo' ? 'bg-success' : 'bg-danger'}`">
                  {{ sriConfig.certificado_digital.estado }}
                </span>
              </li>
            </ul>
          </div>
        </div>
        <div class="mt-3">
          <button class="btn btn-outline-primary" @click="editSRIConfig">
            <i class="fas fa-edit me-2"></i>
            Editar Configuración
          </button>
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
  name: 'SRI',
  setup() {
    const toast = useToast()
    const companyStore = useCompanyStore()

    // State
    const loading = ref(false)
    const showParameters = ref(false)
    const currentFormType = ref('')
    const sriStatus = ref([])
    const sriConfig = ref({
      ruc: '',
      nombre: '',
      ambiente: 'pruebas',
      certificado_digital: {
        numero_serie: '',
        fecha_vencimiento: null,
        estado: 'activo'
      }
    })

    const formParams = reactive({
      period: new Date().toISOString().slice(0, 7),
      year: new Date().getFullYear()
    })

    // Methods
    const generateFormulario103 = () => {
      currentFormType.value = 'formulario-103'
      showParameters.value = true
    }

    const generateFormulario104 = () => {
      currentFormType.value = 'formulario-104'
      showParameters.value = true
    }

    const generateRDEP = () => {
      currentFormType.value = 'rdep'
      showParameters.value = true
    }

    const generateForm = async () => {
      if (!companyStore.getCurrentCompany()) {
        toast.error('Selecciona una empresa primero')
        return
      }

      loading.value = true
      try {
        const params = {
          company_id: companyStore.getCurrentCompany().id,
          period: formParams.period,
          year: formParams.year
        }

        const response = await api.post(`/sri/enviar-sri/${currentFormType.value}`, null, { params })
        
        toast.success('Formulario generado exitosamente')
        showParameters.value = false
        loadSRIStatus()
      } catch (error) {
        console.error('Error generating form:', error)
        toast.error('Error al generar formulario')
      } finally {
        loading.value = false
      }
    }

    const cancelForm = () => {
      showParameters.value = false
      currentFormType.value = ''
    }

    const loadSRIStatus = async () => {
      if (!companyStore.getCurrentCompany()) return

      loading.value = true
      try {
        const response = await api.get('/sri/estado-envios', {
          params: { company_id: companyStore.getCurrentCompany().id }
        })
        sriStatus.value = response.data.envios
      } catch (error) {
        console.error('Error loading SRI status:', error)
        toast.error('Error al cargar estado SRI')
      } finally {
        loading.value = false
      }
    }

    const loadSRIConfig = async () => {
      if (!companyStore.getCurrentCompany()) return

      try {
        const response = await api.get('/sri/configuracion', {
          params: { company_id: companyStore.getCurrentCompany().id }
        })
        sriConfig.value = response.data
      } catch (error) {
        console.error('Error loading SRI config:', error)
        toast.error('Error al cargar configuración SRI')
      }
    }

    const viewForm = (status) => {
      // TODO: Implement view form functionality
      toast.info('Visualizando formulario...')
    }

    const resendForm = (status) => {
      if (confirm(`¿Estás seguro de reenviar el formulario ${status.formulario}?`)) {
        // TODO: Implement resend functionality
        toast.success('Formulario reenviado')
        loadSRIStatus()
      }
    }

    const editSRIConfig = () => {
      // TODO: Implement edit SRI config functionality
      toast.info('Editando configuración SRI...')
    }

    const getFormColor = (formulario) => {
      const colors = {
        '103': 'warning',
        '104': 'info',
        'RDEP': 'success'
      }
      return colors[formulario] || 'secondary'
    }

    const getStatusColor = (status) => {
      const colors = {
        'aceptado': 'success',
        'rechazado': 'danger',
        'procesando': 'warning',
        'pendiente': 'secondary'
      }
      return colors[status] || 'secondary'
    }

    const formatDate = (date) => {
      if (!date || date === '' || date === null || date === undefined) {
        return 'No especificada'
      }
      
      const dateObj = new Date(date)
      if (isNaN(dateObj.getTime())) {
        return 'Fecha inválida'
      }
      
      return new Intl.DateTimeFormat('es-EC', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      }).format(dateObj)
    }

    // Lifecycle
    onMounted(() => {
      loadSRIStatus()
      loadSRIConfig()
    })

    return {
      loading,
      showParameters,
      currentFormType,
      sriStatus,
      sriConfig,
      formParams,
      generateFormulario103,
      generateFormulario104,
      generateRDEP,
      generateForm,
      cancelForm,
      viewForm,
      resendForm,
      editSRIConfig,
      getFormColor,
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

code {
  background-color: #f8f9fa;
  padding: 0.2rem 0.4rem;
  border-radius: 0.25rem;
  font-size: 0.875em;
}
</style>

