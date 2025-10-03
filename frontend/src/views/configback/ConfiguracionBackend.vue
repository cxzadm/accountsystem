<template>
  <div class="config-container">
    <div class="row">
      <div class="col-12">
        <div class="card main-card">
          <div class="card-header">
            <h4 class="mb-0">
              <i class="fas fa-server me-2"></i>
              Configuración del Backend
            </h4>
          </div>
          <div class="card-body">
            <div class="config-section">
              <div class="card config-card">
                <div class="card-body">
                  <form @submit.prevent="saveConfig" class="backend-form">
                    <div class="form-group mb-4">
                      <label class="form-label">
                        <i class="fas fa-network-wired me-2"></i>
                        IP del Backend
                      </label>
                      <input 
                        type="text" 
                        v-model="backendConfig.IP" 
                        class="form-control"
                        placeholder="Ej: 192.168.1.100"
                      >
                      <small class="form-text text-muted">
                        Ingresa la dirección IP del servidor backend
                      </small>
                    </div>
                    
                    <div class="form-group mb-4">
                      <label class="form-label">
                        <i class="fas fa-plug me-2"></i>
                        Puerto
                      </label>
                      <input 
                        type="text" 
                        v-model="backendConfig.PORT" 
                        class="form-control"
                        placeholder="Ej: 8000"
                      >
                      <small class="form-text text-muted">
                        Puerto en el que se ejecuta el servidor backend
                      </small>
                    </div>
                    
                    <div class="form-group mb-4">
                      <label class="form-label">
                        <i class="fas fa-shield-alt me-2"></i>
                        Protocolo
                      </label>
                      <select v-model="backendConfig.PROTOCOL" class="form-select">
                        <option value="http">HTTP</option>
                        <option value="https">HTTPS</option>
                      </select>
                      <small class="form-text text-muted">
                        Protocolo de comunicación con el servidor
                      </small>
                    </div>

                    <div class="current-config mb-4">
                      <h5 class="text-muted">
                        <i class="fas fa-info-circle me-2"></i>
                        Configuración Actual
                      </h5>
                      <div class="alert alert-info">
                        <p class="mb-1">
                          <strong>URL Base:</strong> {{ currentBaseUrl }}
                        </p>
                        <p class="mb-0">
                          <strong>Estado:</strong> 
                          <span :class="connectionStatus.class">
                            {{ connectionStatus.message }}
                          </span>
                        </p>
                      </div>
                    </div>

                    <div class="d-flex justify-content-end">
                      <button type="submit" class="btn btn-custom-primary">
                        <i class="fas fa-save me-2"></i>
                        Guardar Configuración
                      </button>
                    </div>
                  </form>
                </div>
              </div>
            </div>

            <!-- Sección de Configuración de Base de Datos -->
            <div class="config-section">
              <div class="card config-card">
                <div class="card-header">
                  <h5 class="mb-0">
                    <i class="fas fa-database me-2"></i>
                    Configuración de Base de Datos
                  </h5>
                </div>
                <div class="card-body">
                  <form @submit.prevent="saveDatabaseConfig" class="database-form">
                    <div class="form-group mb-4">
                      <label class="form-label">
                        <i class="fas fa-server me-2"></i>
                        Host de MongoDB
                      </label>
                      <input 
                        type="text" 
                        v-model="databaseConfig.HOST" 
                        class="form-control"
                        placeholder="Ej: localhost o 192.168.1.100"
                      >
                      <small class="form-text text-muted">
                        Dirección del servidor MongoDB
                      </small>
                    </div>
                    
                    <div class="form-group mb-4">
                      <label class="form-label">
                        <i class="fas fa-plug me-2"></i>
                        Puerto de MongoDB
                      </label>
                      <input 
                        type="text" 
                        v-model="databaseConfig.PORT" 
                        class="form-control"
                        placeholder="Ej: 27017"
                      >
                      <small class="form-text text-muted">
                        Puerto por defecto de MongoDB es 27017
                      </small>
                    </div>
                    
                    <div class="form-group mb-4">
                      <label class="form-label">
                        <i class="fas fa-database me-2"></i>
                        Nombre de la Base de Datos
                      </label>
                      <input 
                        type="text" 
                        v-model="databaseConfig.DATABASE" 
                        class="form-control"
                        placeholder="Ej: sistema_contable_ec"
                      >
                      <small class="form-text text-muted">
                        Nombre de la base de datos del sistema contable
                      </small>
                    </div>

                    <div class="form-group mb-4">
                      <label class="form-label">
                        <i class="fas fa-user me-2"></i>
                        Usuario (Opcional)
                      </label>
                      <input 
                        type="text" 
                        v-model="databaseConfig.USERNAME" 
                        class="form-control"
                        placeholder="Usuario de MongoDB"
                      >
                      <small class="form-text text-muted">
                        Dejar vacío si no requiere autenticación
                      </small>
                    </div>

                    <div class="form-group mb-4">
                      <label class="form-label">
                        <i class="fas fa-lock me-2"></i>
                        Contraseña (Opcional)
                      </label>
                      <input 
                        type="password" 
                        v-model="databaseConfig.PASSWORD" 
                        class="form-control"
                        placeholder="Contraseña de MongoDB"
                      >
                      <small class="form-text text-muted">
                        Dejar vacío si no requiere autenticación
                      </small>
                    </div>

                    <div class="database-status mb-4">
                      <h6 class="text-muted">
                        <i class="fas fa-info-circle me-2"></i>
                        Estado de la Base de Datos
                      </h6>
                      <div class="alert" :class="databaseStatus.class">
                        <p class="mb-1">
                          <strong>Conexión:</strong> {{ databaseStatus.message }}
                        </p>
                        <p class="mb-0" v-if="databaseInfo">
                          <strong>Colecciones:</strong> {{ databaseInfo.collections }}
                          <br>
                          <strong>Documentos:</strong> {{ databaseInfo.documents }}
                        </p>
                      </div>
                    </div>

                    <div class="d-flex justify-content-end">
                      <button type="submit" class="btn btn-custom-primary">
                        <i class="fas fa-save me-2"></i>
                        Guardar Configuración DB
                      </button>
                    </div>
                  </form>
                </div>
              </div>
            </div>

            <!-- Sección de Importar/Exportar Base de Datos -->
            <div class="config-section">
              <div class="card config-card">
                <div class="card-header">
                  <h5 class="mb-0">
                    <i class="fas fa-exchange-alt me-2"></i>
                    Importar / Exportar Base de Datos
                  </h5>
                </div>
                <div class="card-body">
                  <div class="row">
                    <!-- Exportar Base de Datos -->
                    <div class="col-md-6">
                      <div class="export-section">
                        <h6 class="text-primary mb-3">
                          <i class="fas fa-download me-2"></i>
                          Exportar Base de Datos
                        </h6>
                        <p class="text-muted mb-3">
                          Exporta toda la base de datos usando mongoexport
                        </p>
                        
                        <div class="form-group mb-3">
                          <label class="form-label">Formato de Exportación</label>
                          <select v-model="exportConfig.format" class="form-select">
                            <option value="json">JSON</option>
                            <option value="csv">CSV</option>
                          </select>
                        </div>

                        <div class="form-group mb-3">
                          <label class="form-label">Colecciones a Exportar</label>
                          <select v-model="exportConfig.collections" class="form-select" multiple>
                            <option value="all">Todas las colecciones</option>
                            <option value="accounts">Cuentas Contables</option>
                            <option value="journal_entries">Asientos Contables</option>
                            <option value="ledger_entries">Mayor General</option>
                            <option value="companies">Empresas</option>
                            <option value="users">Usuarios</option>
                            <option value="audit_logs">Logs de Auditoría</option>
                            <option value="document_types">Tipos de Documento</option>
                            <option value="document_reservations">Reservas de Documentos</option>
                          </select>
                          <small class="form-text text-muted">
                            Mantén presionado Ctrl para seleccionar múltiples
                          </small>
                        </div>

                        <button 
                          @click="exportDatabase" 
                          class="btn btn-success w-100"
                          :disabled="exportLoading"
                        >
                          <i class="fas fa-download me-2" v-if="!exportLoading"></i>
                          <i class="fas fa-spinner fa-spin me-2" v-if="exportLoading"></i>
                          {{ exportLoading ? 'Exportando...' : 'Exportar Base de Datos' }}
                        </button>
                      </div>
                    </div>

                    <!-- Importar Base de Datos -->
                    <div class="col-md-6">
                      <div class="import-section">
                        <h6 class="text-warning mb-3">
                          <i class="fas fa-upload me-2"></i>
                          Importar Base de Datos
                        </h6>
                        <p class="text-muted mb-3">
                          Importa datos usando mongoimport
                        </p>
                        
                        <div class="form-group mb-3">
                          <label class="form-label">Archivo a Importar</label>
                          <input 
                            type="file" 
                            @change="handleFileSelect" 
                            accept=".json,.csv"
                            class="form-control"
                            ref="fileInput"
                          >
                          <small class="form-text text-muted">
                            Selecciona un archivo JSON o CSV
                          </small>
                        </div>

                        <div class="form-group mb-3">
                          <label class="form-label">Modo de Importación</label>
                          <select v-model="importConfig.mode" class="form-select">
                            <option value="insert">Insertar (mantener datos existentes)</option>
                            <option value="upsert">Upsert (actualizar si existe, insertar si no)</option>
                            <option value="replace">Reemplazar (eliminar y reinsertar)</option>
                          </select>
                        </div>

                        <div class="alert alert-warning">
                          <i class="fas fa-exclamation-triangle me-2"></i>
                          <strong>Advertencia:</strong> La importación puede sobrescribir datos existentes.
                        </div>

                        <button 
                          @click="importDatabase" 
                          class="btn btn-warning w-100"
                          :disabled="importLoading || !selectedFile"
                        >
                          <i class="fas fa-upload me-2" v-if="!importLoading"></i>
                          <i class="fas fa-spinner fa-spin me-2" v-if="importLoading"></i>
                          {{ importLoading ? 'Importando...' : 'Importar Base de Datos' }}
                        </button>
                      </div>
                    </div>
                  </div>

                  <!-- Progreso de Operaciones -->
                  <div v-if="operationProgress.show" class="mt-4">
                    <div class="card">
                      <div class="card-body">
                        <h6 class="text-info">
                          <i class="fas fa-cogs me-2"></i>
                          {{ operationProgress.title }}
                        </h6>
                        <div class="progress mb-2">
                          <div 
                            class="progress-bar" 
                            :class="operationProgress.class"
                            :style="{ width: operationProgress.percentage + '%' }"
                          ></div>
                        </div>
                        <p class="mb-0 text-muted">{{ operationProgress.message }}</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { config } from '../../../config-browser.js'
import Swal from 'sweetalert2'
import api from '../../services/api.js'

const backendConfig = ref({
  IP: config.BACKEND_CONFIG.IP,
  PORT: config.BACKEND_CONFIG.PORT,
  PROTOCOL: config.BACKEND_CONFIG.PROTOCOL
})

const databaseConfig = ref({
  HOST: 'localhost',
  PORT: '27017',
  DATABASE: 'sistema_contable_ec',
  USERNAME: '',
  PASSWORD: ''
})

const exportConfig = ref({
  format: 'json',
  collections: ['all']
})

const importConfig = ref({
  mode: 'insert'
})

const selectedFile = ref(null)
const exportLoading = ref(false)
const importLoading = ref(false)

const currentBaseUrl = computed(() => {
  return `${backendConfig.value.PROTOCOL}://${backendConfig.value.IP}:${backendConfig.value.PORT}`
})

const connectionStatus = ref({
  message: 'Verificando conexión...',
  class: 'text-warning'
})

const databaseStatus = ref({
  message: 'Verificando conexión a la base de datos...',
  class: 'alert-warning'
})

const databaseInfo = ref(null)

const operationProgress = ref({
  show: false,
  title: '',
  message: '',
  percentage: 0,
  class: 'bg-info'
})

// Función para verificar la conexión
const checkConnection = async () => {
  try {
    const response = await api.get(`${currentBaseUrl.value}/`, {
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      timeout: 5000, // 5 segundos de timeout
      withCredentials: false // Importante: no enviar credenciales
    })
    
    if (response.data) {
      connectionStatus.value = {
        message: 'Conectado',
        class: 'text-success'
      }
      console.log('Respuesta del servidor:', response.data)
    } else {
      throw new Error('Respuesta vacía del servidor')
    }
  } catch (error) {
    console.error('Error de conexión:', error)
    let errorMessage = 'No se pudo conectar al servidor'
    
    if (error.response) {
      // El servidor respondió con un código de error
      errorMessage = `Error del servidor: ${error.response.status}`
    } else if (error.request) {
      // La solicitud fue hecha pero no se recibió respuesta
      errorMessage = 'No se recibió respuesta del servidor'
    }
    
    connectionStatus.value = {
      message: errorMessage,
      class: 'text-danger'
    }
  }
}

// Función para actualizar la configuración
const updateBackendConfig = (newConfig) => {
  config.BACKEND_CONFIG.IP = newConfig.IP
  config.BACKEND_CONFIG.PORT = newConfig.PORT
  config.BACKEND_CONFIG.PROTOCOL = newConfig.PROTOCOL
  
  // Guardar en localStorage
  localStorage.setItem('backendConfig', JSON.stringify(newConfig))
  
  // Actualizar la URL base
  config.API_BASE_URL = `${newConfig.PROTOCOL}://${newConfig.IP}:${newConfig.PORT}`
}

const saveConfig = async () => {
  try {
    updateBackendConfig(backendConfig.value)
    await checkConnection()
    
    Swal.fire({
      icon: 'success',
      title: 'Configuración guardada',
      text: 'La configuración del backend ha sido actualizada correctamente',
      timer: 2000,
      showConfirmButton: false
    })
  } catch (error) {
    Swal.fire({
      icon: 'error',
      title: 'Error',
      text: 'No se pudo guardar la configuración'
    })
  }
}

// Función para verificar la conexión a la base de datos
const checkDatabaseConnection = async () => {
  try {
    const response = await api.get(`/database/status`, {
      params: databaseConfig.value
    })
    
    if (response.data.success) {
      databaseStatus.value = {
        message: 'Conectado a la base de datos',
        class: 'alert-success'
      }
      databaseInfo.value = response.data.info
    } else {
      throw new Error(response.data.message || 'Error de conexión')
    }
  } catch (error) {
    console.error('Error de conexión a la base de datos:', error)
    databaseStatus.value = {
      message: 'No se pudo conectar a la base de datos',
      class: 'alert-danger'
    }
    databaseInfo.value = null
  }
}

// Función para guardar la configuración de la base de datos
const saveDatabaseConfig = async () => {
  try {
    // Guardar en localStorage
    localStorage.setItem('databaseConfig', JSON.stringify(databaseConfig.value))
    
    // Verificar conexión
    await checkDatabaseConnection()
    
    Swal.fire({
      icon: 'success',
      title: 'Configuración guardada',
      text: 'La configuración de la base de datos ha sido actualizada correctamente',
      timer: 2000,
      showConfirmButton: false
    })
  } catch (error) {
    Swal.fire({
      icon: 'error',
      title: 'Error',
      text: 'No se pudo guardar la configuración de la base de datos'
    })
  }
}

// Función para exportar la base de datos
const exportDatabase = async () => {
  try {
    exportLoading.value = true
    operationProgress.value = {
      show: true,
      title: 'Exportando Base de Datos',
      message: 'Preparando exportación...',
      percentage: 0,
      class: 'bg-info'
    }

    const response = await api.post(`/database/export`, {
      ...databaseConfig.value,
      ...exportConfig.value
    }, {
      responseType: 'blob'
    })

    // Crear y descargar archivo
    const blob = new Blob([response.data])
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    
    const timestamp = new Date().toISOString().split('T')[0]
    const filename = `backup_sistema_contable_${timestamp}.${exportConfig.value.format}`
    link.download = filename
    
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)

    operationProgress.value = {
      show: false,
      title: '',
      message: '',
      percentage: 100,
      class: 'bg-success'
    }

    Swal.fire({
      icon: 'success',
      title: 'Exportación completada',
      text: `La base de datos ha sido exportada como ${filename}`,
      timer: 3000,
      showConfirmButton: false
    })

  } catch (error) {
    console.error('Error al exportar:', error)
    operationProgress.value.show = false
    
    Swal.fire({
      icon: 'error',
      title: 'Error en la exportación',
      text: 'No se pudo exportar la base de datos'
    })
  } finally {
    exportLoading.value = false
  }
}

// Función para manejar la selección de archivo
const handleFileSelect = (event) => {
  const file = event.target.files[0]
  if (file) {
    selectedFile.value = file
    console.log('Archivo seleccionado:', file.name)
  }
}

// Función para importar la base de datos
const importDatabase = async () => {
  if (!selectedFile.value) {
    Swal.fire({
      icon: 'warning',
      title: 'Archivo requerido',
      text: 'Por favor selecciona un archivo para importar'
    })
    return
  }

  try {
    importLoading.value = true
    operationProgress.value = {
      show: true,
      title: 'Importando Base de Datos',
      message: 'Preparando importación...',
      percentage: 0,
      class: 'bg-warning'
    }

    const formData = new FormData()
    formData.append('file', selectedFile.value)
    formData.append('config', JSON.stringify(databaseConfig.value))
    formData.append('mode', importConfig.value.mode)

    const response = await api.post(`/database/import`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })

    operationProgress.value = {
      show: false,
      title: '',
      message: '',
      percentage: 100,
      class: 'bg-success'
    }

    Swal.fire({
      icon: 'success',
      title: 'Importación completada',
      text: `Se importaron ${response.data.imported} documentos exitosamente`,
      timer: 3000,
      showConfirmButton: false
    })

    // Limpiar archivo seleccionado
    selectedFile.value = null
    document.querySelector('input[type="file"]').value = ''

  } catch (error) {
    console.error('Error al importar:', error)
    operationProgress.value.show = false
    
    Swal.fire({
      icon: 'error',
      title: 'Error en la importación',
      text: 'No se pudo importar la base de datos'
    })
  } finally {
    importLoading.value = false
  }
}

// Cargar configuración guardada al iniciar
onMounted(async () => {
  const savedConfig = localStorage.getItem('backendConfig')
  if (savedConfig) {
    const parsedConfig = JSON.parse(savedConfig)
    backendConfig.value = parsedConfig
    updateBackendConfig(parsedConfig)
  }

  const savedDatabaseConfig = localStorage.getItem('databaseConfig')
  if (savedDatabaseConfig) {
    const parsedDatabaseConfig = JSON.parse(savedDatabaseConfig)
    databaseConfig.value = parsedDatabaseConfig
  }

  await checkConnection()
  await checkDatabaseConnection()
})
</script>

<style scoped>
.config-container {
  padding: 2rem;
  background-color: #f8f9fa;
  min-height: 100vh;
}

.main-card {
  border: none;
  border-radius: 15px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.card-header {
  background-color: #165f6e;
  color: white;
  border-radius: 15px 15px 0 0 !important;
  padding: 1.5rem;
}

.card-header h4 {
  font-size: 1.5rem;
  font-weight: 600;
  margin: 0;
}

.config-section {
  margin-bottom: 2rem;
}

.config-card {
  border: 1px solid #e9ecef;
  border-radius: 10px;
  background-color: white;
}

.form-label {
  color: #165f6e;
  font-weight: 500;
  margin-bottom: 0.5rem;
}

.form-control,
.form-select {
  border: 1px solid #ced4da;
  border-radius: 8px;
  padding: 0.75rem;
  transition: all 0.3s ease;
}

.form-control:focus,
.form-select:focus {
  border-color: #165f6e;
  box-shadow: 0 0 0 0.2rem rgba(22, 95, 110, 0.25);
}

.btn-custom-primary {
  background-color: #17a2b8;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  transition: all 0.3s ease;
  font-weight: 500;
  font-size: 1rem;
}

.btn-custom-primary:hover:not(:disabled) {
  background-color: #138496;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.current-config {
  background-color: #f8f9fa;
  padding: 1.5rem;
  border-radius: 8px;
  margin-top: 2rem;
}

.current-config h5 {
  font-size: 1.1rem;
  margin-bottom: 1rem;
}

.alert {
  border-radius: 8px;
  padding: 1rem;
}

.text-success {
  color: #28a745 !important;
}

.text-danger {
  color: #dc3545 !important;
}

.text-warning {
  color: #ffc107 !important;
}

/* Estilos para la sección de base de datos */
.database-form .form-group {
  margin-bottom: 1.5rem;
}

.database-status {
  background-color: #f8f9fa;
  padding: 1.5rem;
  border-radius: 8px;
  margin-top: 1rem;
}

.database-status h6 {
  font-size: 1rem;
  margin-bottom: 1rem;
}

.export-section,
.import-section {
  padding: 1.5rem;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  background-color: #f8f9fa;
}

.export-section h6 {
  color: #17a2b8;
  font-weight: 600;
}

.import-section h6 {
  color: #ffc107;
  font-weight: 600;
}

.btn-success {
  background-color: #28a745;
  border-color: #28a745;
  color: white;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  transition: all 0.3s ease;
  font-weight: 500;
}

.btn-success:hover:not(:disabled) {
  background-color: #218838;
  border-color: #1e7e34;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.btn-warning {
  background-color: #ffc107;
  border-color: #ffc107;
  color: #212529;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  transition: all 0.3s ease;
  font-weight: 500;
}

.btn-warning:hover:not(:disabled) {
  background-color: #e0a800;
  border-color: #d39e00;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.progress {
  height: 1rem;
  border-radius: 0.5rem;
  background-color: #e9ecef;
}

.progress-bar {
  border-radius: 0.5rem;
  transition: width 0.3s ease;
}

.bg-info {
  background-color: #17a2b8 !important;
}

.bg-success {
  background-color: #28a745 !important;
}

.bg-warning {
  background-color: #ffc107 !important;
}

.alert-success {
  background-color: #d4edda;
  border-color: #c3e6cb;
  color: #155724;
}

.alert-danger {
  background-color: #f8d7da;
  border-color: #f5c6cb;
  color: #721c24;
}

.alert-warning {
  background-color: #fff3cd;
  border-color: #ffeaa7;
  color: #856404;
}

/* Estilos para selectores múltiples */
.form-select[multiple] {
  min-height: 120px;
}

.form-select[multiple] option {
  padding: 0.5rem;
}

/* Estilos para el input de archivo */
input[type="file"] {
  padding: 0.5rem;
}

input[type="file"]::-webkit-file-upload-button {
  background-color: #17a2b8;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  margin-right: 1rem;
  cursor: pointer;
}

input[type="file"]::-webkit-file-upload-button:hover {
  background-color: #138496;
}
</style> 