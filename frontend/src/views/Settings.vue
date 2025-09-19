<template>
  <div class="container-fluid">
    <div class="row">
      <div class="col-12">
        <div class="d-flex justify-content-between align-items-center mb-4">
          <h2><i class="fas fa-cog me-2"></i>Configuración del Sistema</h2>
        </div>
      </div>
    </div>

    <div class="row">
      <div class="col-md-6">
        <div class="card">
          <div class="card-header">
            <h5 class="card-title mb-0">Configuración General</h5>
          </div>
          <div class="card-body">
            <form @submit.prevent="saveSettings">
              <div class="mb-3">
                <label for="companyName" class="form-label">Nombre de la Empresa</label>
                <input
                  type="text"
                  class="form-control"
                  id="companyName"
                  v-model="settings.company_name"
                />
              </div>

              <div class="mb-3">
                <label for="currency" class="form-label">Moneda</label>
                <select class="form-select" id="currency" v-model="settings.currency">
                  <option value="USD">Dólar Americano (USD)</option>
                  <option value="EUR">Euro (EUR)</option>
                  <option value="PEN">Sol Peruano (PEN)</option>
                </select>
              </div>

              <div class="mb-3">
                <label for="dateFormat" class="form-label">Formato de Fecha</label>
                <select class="form-select" id="dateFormat" v-model="settings.date_format">
                  <option value="DD/MM/YYYY">DD/MM/YYYY</option>
                  <option value="MM/DD/YYYY">MM/DD/YYYY</option>
                  <option value="YYYY-MM-DD">YYYY-MM-DD</option>
                </select>
              </div>

              <div class="mb-3">
                <label for="timezone" class="form-label">Zona Horaria</label>
                <select class="form-select" id="timezone" v-model="settings.timezone">
                  <option value="America/Guayaquil">Guayaquil (GMT-5)</option>
                  <option value="America/New_York">Nueva York (GMT-5)</option>
                  <option value="Europe/Madrid">Madrid (GMT+1)</option>
                </select>
              </div>

              <button type="submit" class="btn btn-primary" :disabled="loading">
                <i class="fas fa-save me-1"></i>
                {{ loading ? 'Guardando...' : 'Guardar Configuración' }}
              </button>
            </form>
          </div>
        </div>
      </div>

      <div class="col-md-6">
        <div class="card">
          <div class="card-header">
            <h5 class="card-title mb-0">Configuración de Seguridad</h5>
          </div>
          <div class="card-body">
            <div class="mb-3">
              <div class="form-check">
                <input
                  class="form-check-input"
                  type="checkbox"
                  id="twoFactor"
                  v-model="settings.two_factor_auth"
                />
                <label class="form-check-label" for="twoFactor">
                  Autenticación de Dos Factores
                </label>
              </div>
            </div>

            <div class="mb-3">
              <div class="form-check">
                <input
                  class="form-check-input"
                  type="checkbox"
                  id="sessionTimeout"
                  v-model="settings.session_timeout_enabled"
                />
                <label class="form-check-label" for="sessionTimeout">
                  Timeout de Sesión Automático
                </label>
              </div>
            </div>

            <div class="mb-3" v-if="settings.session_timeout_enabled">
              <label for="sessionTimeoutMinutes" class="form-label">Minutos de Inactividad</label>
              <input
                type="number"
                class="form-control"
                id="sessionTimeoutMinutes"
                v-model="settings.session_timeout_minutes"
                min="5"
                max="480"
              />
            </div>

            <div class="mb-3">
              <div class="form-check">
                <input
                  class="form-check-input"
                  type="checkbox"
                  id="auditLog"
                  v-model="settings.audit_log_enabled"
                />
                <label class="form-check-label" for="auditLog">
                  Habilitar Log de Auditoría
                </label>
              </div>
            </div>
          </div>
        </div>

        <div class="card mt-3">
          <div class="card-header">
            <h5 class="card-title mb-0">Configuración de Reportes</h5>
          </div>
          <div class="card-body">
            <div class="mb-3">
              <label for="reportFormat" class="form-label">Formato de Reportes por Defecto</label>
              <select class="form-select" id="reportFormat" v-model="settings.default_report_format">
                <option value="pdf">PDF</option>
                <option value="excel">Excel</option>
                <option value="csv">CSV</option>
              </select>
            </div>

            <div class="mb-3">
              <div class="form-check">
                <input
                  class="form-check-input"
                  type="checkbox"
                  id="autoBackup"
                  v-model="settings.auto_backup_enabled"
                />
                <label class="form-check-label" for="autoBackup">
                  Respaldo Automático
                </label>
              </div>
            </div>

            <div class="mb-3" v-if="settings.auto_backup_enabled">
              <label for="backupFrequency" class="form-label">Frecuencia de Respaldo</label>
              <select class="form-select" id="backupFrequency" v-model="settings.backup_frequency">
                <option value="daily">Diario</option>
                <option value="weekly">Semanal</option>
                <option value="monthly">Mensual</option>
              </select>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useToast } from 'vue-toastification'

export default {
  name: 'Settings',
  setup() {
    const toast = useToast()
    const loading = ref(false)
    
    const settings = ref({
      company_name: '',
      currency: 'USD',
      date_format: 'DD/MM/YYYY',
      timezone: 'America/Guayaquil',
      two_factor_auth: false,
      session_timeout_enabled: true,
      session_timeout_minutes: 30,
      audit_log_enabled: true,
      default_report_format: 'pdf',
      auto_backup_enabled: false,
      backup_frequency: 'daily'
    })

    const loadSettings = () => {
      // Cargar configuración desde localStorage o API
      const savedSettings = localStorage.getItem('system_settings')
      if (savedSettings) {
        settings.value = { ...settings.value, ...JSON.parse(savedSettings) }
      }
    }

    const saveSettings = async () => {
      loading.value = true
      try {
        // Guardar en localStorage (en producción sería en la API)
        localStorage.setItem('system_settings', JSON.stringify(settings.value))
        toast.success('Configuración guardada correctamente')
      } catch (error) {
        toast.error('Error al guardar la configuración')
        console.error('Error saving settings:', error)
      } finally {
        loading.value = false
      }
    }

    onMounted(() => {
      loadSettings()
    })

    return {
      settings,
      loading,
      saveSettings
    }
  }
}
</script>






