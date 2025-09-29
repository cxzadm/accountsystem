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
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { config } from '../../../config.js'
import Swal from 'sweetalert2'
import axios from 'axios'

const backendConfig = ref({
  IP: config.BACKEND_CONFIG.IP,
  PORT: config.BACKEND_CONFIG.PORT,
  PROTOCOL: config.BACKEND_CONFIG.PROTOCOL
})

const currentBaseUrl = computed(() => {
  return `${backendConfig.value.PROTOCOL}://${backendConfig.value.IP}:${backendConfig.value.PORT}`
})

const connectionStatus = ref({
  message: 'Verificando conexión...',
  class: 'text-warning'
})

// Función para verificar la conexión
const checkConnection = async () => {
  try {
    const response = await axios.get(`${currentBaseUrl.value}/`, {
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

// Cargar configuración guardada al iniciar
onMounted(async () => {
  const savedConfig = localStorage.getItem('backendConfig')
  if (savedConfig) {
    const parsedConfig = JSON.parse(savedConfig)
    backendConfig.value = parsedConfig
    updateBackendConfig(parsedConfig)
  }
  await checkConnection()
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
</style> 