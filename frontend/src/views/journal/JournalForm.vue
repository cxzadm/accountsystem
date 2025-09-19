<template>
  <div class="journal-form-page">
    <!-- Page Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h1 class="h3 mb-0">
          {{ isEdit ? 'Editar Asiento' : 'Nuevo Asiento' }}
        </h1>
        <p class="text-muted">
          {{ isEdit ? 'Modifica el asiento contable' : 'Crea un nuevo asiento contable' }}
        </p>
      </div>
      <div>
        <router-link to="/journal" class="btn btn-outline-secondary">
          <i class="fas fa-arrow-left me-2"></i>
          Volver
        </router-link>
      </div>
    </div>

    <!-- Form -->
    <div class="row">
      <div class="col-md-8">
        <div class="card">
          <div class="card-body">
            <!-- Prominent number display -->
            <div class="mb-3 p-3 bg-light rounded d-flex align-items-center justify-content-between">
              <div>
                <div class="text-muted small">Número del Documento</div>
                <div class="display-6 mb-0">
                  <code>{{ form.entry_number || (form.document_type_code ? form.document_type_code + '-…' : 'Seleccione tipo') }}</code>
                </div>
              </div>
              <div>
                <button
                  type="button"
                  class="btn btn-outline-secondary"
                  :disabled="!form.document_type_id || reserving"
                  @click="reserveNumber"
                >
                  <span v-if="reserving" class="spinner-border spinner-border-sm me-1"></span>
                  Reservar
                </button>
              </div>
            </div>

            <form @submit.prevent="handleSubmit">
              <div class="row">
                <div class="col-md-6">
                  <div class="mb-3">
                    <label for="date" class="form-label">Fecha *</label>
                    <input
                      type="date"
                      class="form-control"
                      id="date"
                      v-model="form.date"
                      :class="{ 'is-invalid': errors.date }"
                      required
                    />
                    <div class="invalid-feedback" v-if="errors.date">
                      {{ errors.date }}
                    </div>
                  </div>
                </div>
                <div class="col-md-3">
                  <div class="mb-3">
                    <label for="entry_type" class="form-label">Tipo de Asiento</label>
                    <select
                      class="form-select"
                      id="entry_type"
                      v-model="form.entry_type"
                      :class="{ 'is-invalid': errors.entry_type }"
                    >
                      <option value="manual">Manual</option>
                      <option value="automatic">Automático</option>
                      <option value="adjustment">Ajuste</option>
                      <option value="closing">Cierre</option>
                    </select>
                    <div class="invalid-feedback" v-if="errors.entry_type">
                      {{ errors.entry_type }}
                    </div>
                  </div>
                </div>
                <div class="col-md-3">
                  <div class="mb-3">
                    <label for="document_type" class="form-label">Tipo de Documento *</label>
                    <select
                      id="document_type"
                      class="form-select"
                      v-model="form.document_type_id"
                      :class="{ 'is-invalid': errors.document_type_id }"
                      @change="onChangeDocumentType"
                      required
                    >
                      <option value="">Seleccionar...</option>
                      <option v-for="dt in documentTypes" :key="dt.id" :value="dt.id">
                        {{ dt.code }} - {{ dt.name }}
                      </option>
                    </select>
                    <div class="invalid-feedback" v-if="errors.document_type_id">
                      {{ errors.document_type_id }}
                    </div>
                  </div>
                </div>
                
              </div>

              <div class="mb-3">
                <label for="description" class="form-label">Descripción *</label>
                <textarea
                  class="form-control"
                  id="description"
                  v-model="form.description"
                  :class="{ 'is-invalid': errors.description }"
                  rows="3"
                  required
                ></textarea>
                <div class="invalid-feedback" v-if="errors.description">
                  {{ errors.description }}
                </div>
              </div>

              <!-- Journal Lines -->
              <div class="mb-4">
                <div class="d-flex justify-content-between align-items-center mb-3">
                  <h5>Líneas del Asiento</h5>
                  <button
                    type="button"
                    class="btn btn-sm btn-outline-primary"
                    @click="addLine"
                  >
                    <i class="fas fa-plus me-1"></i>
                    Agregar Línea
                  </button>
                </div>

                <div class="table-responsive">
                  <table class="table table-sm">
                    <thead>
                      <tr>
                        <th>Cuenta</th>
                        <th>Descripción</th>
                        <th>Débito</th>
                        <th>Crédito</th>
                        <th>Referencia</th>
                        <th></th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="(line, index) in form.lines" :key="index">
                        <td>
                          <select
                            class="form-select form-select-sm"
                            v-model="line.account_code"
                            @change="updateAccountName(index)"
                          >
                            <option value="">Seleccionar cuenta</option>
                            <optgroup 
                              v-for="accountType in accountTypes" 
                              :key="accountType.type" 
                              :label="accountType.label"
                            >
                              <option
                                v-for="account in accountType.accounts"
                                :key="account.id"
                                :value="account.code"
                                :disabled="account.account_relationship_type === 'P'"
                                :class="{ 'text-muted': account.account_relationship_type === 'P' }"
                              >
                                {{ getAccountDisplayText(account) }}
                              </option>
                            </optgroup>
                          </select>
                          <small class="text-muted" v-if="line.account_code && getSelectedAccountType(line.account_code) === 'P'">
                            <i class="fas fa-info-circle me-1"></i>
                            Solo se pueden seleccionar cuentas hijas (H)
                          </small>
                        </td>
                        <td>
                          <input
                            type="text"
                            class="form-control form-control-sm"
                            v-model="line.description"
                            placeholder="Descripción"
                          />
                        </td>
                        <td>
                          <input
                            type="number"
                            class="form-control form-control-sm"
                            v-model="line.debit"
                            step="0.01"
                            min="0"
                            @input="calculateTotals"
                          />
                        </td>
                        <td>
                          <input
                            type="number"
                            class="form-control form-control-sm"
                            v-model="line.credit"
                            step="0.01"
                            min="0"
                            @input="calculateTotals"
                          />
                        </td>
                        <td>
                          <input
                            type="text"
                            class="form-control form-control-sm"
                            v-model="line.reference"
                            placeholder="Ref."
                          />
                        </td>
                        <td>
                          <button
                            type="button"
                            class="btn btn-sm btn-outline-danger"
                            @click="removeLine(index)"
                          >
                            <i class="fas fa-trash"></i>
                          </button>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>

                <!-- Totals -->
                <div class="row mt-3">
                  <div class="col-md-6">
                    <div class="card bg-light">
                      <div class="card-body py-2">
                        <div class="d-flex justify-content-between">
                          <strong>Total Débito:</strong>
                          <span class="text-danger">{{ formatCurrency(totalDebit) }}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div class="col-md-6">
                    <div class="card bg-light">
                      <div class="card-body py-2">
                        <div class="d-flex justify-content-between">
                          <strong>Total Crédito:</strong>
                          <span class="text-success">{{ formatCurrency(totalCredit) }}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <div class="row mt-2">
                  <div class="col-12">
                    <div class="card" :class="isBalanced ? 'bg-success' : 'bg-danger'">
                      <div class="card-body py-2 text-white">
                        <div class="d-flex justify-content-between">
                          <strong>Diferencia:</strong>
                          <span>{{ formatCurrency(Math.abs(totalDebit - totalCredit)) }}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div class="d-flex justify-content-end gap-2">
                <router-link to="/journal" class="btn btn-secondary">
                  Cancelar
                </router-link>
                <button
                  type="submit"
                  class="btn btn-primary"
                  :disabled="loading || !isBalanced"
                >
                  <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                  {{ loading ? 'Guardando...' : (isEdit ? 'Actualizar' : 'Crear') }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>

      <!-- Help Panel -->
      <div class="col-md-4">
        <div class="card">
          <div class="card-header">
            <h6 class="mb-0">Ayuda</h6>
          </div>
          <div class="card-body">
            <h6>Reglas del Asiento:</h6>
            <ul class="list-unstyled small">
              <li>• El total de débitos debe igualar al total de créditos</li>
              <li>• Al menos debe haber una línea con débito y una con crédito</li>
              <li>• Las cuentas deben estar activas en el plan contable</li>
              <li>• La descripción debe ser clara y concisa</li>
            </ul>

            <h6 class="mt-3">Tipos de Asiento:</h6>
            <ul class="list-unstyled small">
              <li><strong>Manual:</strong> Asiento creado manualmente</li>
              <li><strong>Automático:</strong> Generado por el sistema</li>
              <li><strong>Ajuste:</strong> Para correcciones</li>
              <li><strong>Cierre:</strong> Para cierre de período</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useToast } from 'vue-toastification'
import { useCompanyStore } from '@/stores/company'
import api from '@/services/api'

export default {
  name: 'JournalForm',
  setup() {
    const route = useRoute()
    const router = useRouter()
    const toast = useToast()
    const companyStore = useCompanyStore()

    // State
    const loading = ref(false)
    const accounts = ref([])
    const documentTypes = ref([])
    const reserving = ref(false)

    const form = reactive({
      date: new Date().toISOString().split('T')[0],
      description: '',
      entry_type: 'automatic',
      document_type_id: '',
      document_type_code: '',
      entry_number: '',
      lines: [
        { account_code: '', account_name: '', description: '', debit: 0, credit: 0, reference: '' },
        { account_code: '', account_name: '', description: '', debit: 0, credit: 0, reference: '' }
      ]
    })

    const errors = reactive({})

    // Computed
    const isEdit = computed(() => !!route.params.id)
    const currentCompany = computed(() => companyStore.getCurrentCompany())

    const totalDebit = computed(() => {
      return form.lines.reduce((sum, line) => sum + (parseFloat(line.debit) || 0), 0)
    })

    const totalCredit = computed(() => {
      return form.lines.reduce((sum, line) => sum + (parseFloat(line.credit) || 0), 0)
    })

    const isBalanced = computed(() => {
      return Math.abs(totalDebit.value - totalCredit.value) < 0.01
    })

    // Methods
    const loadAccounts = async () => {
      if (!currentCompany.value) return

      try {
        const response = await api.get('/accounts/', {
          params: { company_id: currentCompany.value.id, is_active: true }
        })
        accounts.value = response.data
      } catch (error) {
        console.error('Error loading accounts:', error)
        toast.error('Error al cargar cuentas')
      }
    }

    // Computed para organizar cuentas por tipo con jerarquía
    const accountTypes = computed(() => {
      const types = {
        activo: { type: 'activo', label: 'ACTIVO', accounts: [] },
        pasivo: { type: 'pasivo', label: 'PASIVO', accounts: [] },
        patrimonio: { type: 'patrimonio', label: 'PATRIMONIO', accounts: [] },
        ingresos: { type: 'ingresos', label: 'INGRESOS', accounts: [] },
        gastos: { type: 'gastos', label: 'GASTOS', accounts: [] },
        costos: { type: 'costos', label: 'COSTOS', accounts: [] }
      }

      // Organizar cuentas por tipo y nivel
      accounts.value.forEach(account => {
        if (types[account.account_type]) {
          types[account.account_type].accounts.push(account)
        }
      })

      // Ordenar cuentas por código para mantener jerarquía
      Object.values(types).forEach(type => {
        type.accounts.sort((a, b) => a.code.localeCompare(b.code))
      })

      return Object.values(types).filter(type => type.accounts.length > 0)
    })

    // Función para mostrar texto de cuenta con jerarquía
    const getAccountDisplayText = (account) => {
      const indent = '  '.repeat(account.level - 1)
      const typeIndicator = account.account_relationship_type === 'P' ? ' (P)' : ' (H)'
      return `${indent}${account.code} - ${account.name}${typeIndicator}`
    }

    // Función para obtener el tipo de relación de una cuenta seleccionada
    const getSelectedAccountType = (accountCode) => {
      const account = accounts.value.find(acc => acc.code === accountCode)
      return account ? account.account_relationship_type : null
    }

    const loadDocumentTypes = async () => {
      if (!currentCompany.value) return
      try {
        const { data } = await api.get('/document-types/', { params: { company_id: currentCompany.value.id } })
        documentTypes.value = data
      } catch (e) {
        console.error('Error loading document types:', e)
      }
    }

    const onChangeDocumentType = async () => {
      const selected = documentTypes.value.find(d => d.id === form.document_type_id)
      form.document_type_code = selected ? selected.code : ''
      form.entry_number = ''
      // Mostrar vista previa sin reservar
      if (form.document_type_id) {
        try {
          const { data } = await api.get(`/document-types/${form.document_type_id}/peek-next/`)
          form.entry_number = data.number
        } catch (e) {
          console.error('Error peeking next number:', e)
        }
      }
    }

    const reserveNumber = async () => {
      if (!form.document_type_id) return
      reserving.value = true
      try {
        // permitir GET o POST según disponibilidad backend
        let data
        try {
          const resp = await api.get(`/document-types/${form.document_type_id}/next-number/`)
          data = resp.data
        } catch (e) {
          const resp = await api.post(`/document-types/${form.document_type_id}/next-number/`, {})
          data = resp.data
        }
        form.entry_number = data.number
      } catch (e) {
        console.error('Error reserving number:', e)
      } finally {
        reserving.value = false
      }
    }

    const loadJournalEntry = async () => {
      if (!isEdit.value) return

      loading.value = true
      try {
        const response = await api.get(`/journal/${route.params.id}/`)
        const entry = response.data
        
        form.date = entry.date.split('T')[0]
        form.description = entry.description
        form.entry_type = entry.entry_type
        form.entry_number = entry.entry_number || ''
        form.document_type_id = entry.document_type_id || ''
        form.document_type_code = entry.document_type_code || ''
        form.lines = entry.lines.map(line => ({
          account_code: line.account_code,
          account_name: line.account_name,
          description: line.description,
          debit: line.debit,
          credit: line.credit,
          reference: line.reference || ''
        }))
      } catch (error) {
        console.error('Error loading journal entry:', error)
        toast.error('Error al cargar asiento')
        router.push('/journal')
      } finally {
        loading.value = false
      }
    }

    const addLine = () => {
      form.lines.push({
        account_code: '',
        account_name: '',
        description: '',
        debit: 0,
        credit: 0,
        reference: ''
      })
    }

    const removeLine = (index) => {
      if (form.lines.length > 2) {
        form.lines.splice(index, 1)
        calculateTotals()
      }
    }

    const updateAccountName = (index) => {
      const account = accounts.value.find(acc => acc.code === form.lines[index].account_code)
      if (account) {
        // Verificar que solo se puedan seleccionar cuentas hijas
        if (account.account_relationship_type === 'P') {
          toast.warning('Solo se pueden seleccionar cuentas hijas (H). Las cuentas padre (P) son solo para referencia de la estructura.')
          form.lines[index].account_code = ''
          form.lines[index].account_name = ''
          return
        }
        
        form.lines[index].account_name = account.name
        // Limpiar descripción si no está llena para usar la descripción de la cuenta
        if (!form.lines[index].description.trim()) {
          form.lines[index].description = account.name
        }
      } else {
        form.lines[index].account_name = ''
      }
    }

    const calculateTotals = () => {
      // This is handled by computed properties
    }

    const validateForm = () => {
      // Clear previous errors
      Object.keys(errors).forEach(key => delete errors[key])

      if (!form.date) {
        errors.date = 'La fecha es requerida'
      }

      if (!form.description.trim()) {
        errors.description = 'La descripción es requerida'
      }
      if (!form.document_type_id) {
        errors.document_type_id = 'Tipo de documento es requerido'
      }
      if (!form.entry_number) {
        errors.entry_number = 'Debe reservar el número'
      }

      if (form.lines.length < 2) {
        errors.lines = 'Debe haber al menos 2 líneas'
      }

      if (!isBalanced.value) {
        errors.balance = 'El asiento no está balanceado'
      }

      // Validate lines
      let hasValidLines = false
      for (let i = 0; i < form.lines.length; i++) {
        const line = form.lines[i]
        if (!line.account_code) {
          errors[`line_${i}_account`] = 'La cuenta es requerida'
        }
        if (!line.description.trim()) {
          errors[`line_${i}_description`] = 'La descripción es requerida'
        }
        if ((parseFloat(line.debit) || 0) === 0 && (parseFloat(line.credit) || 0) === 0) {
          errors[`line_${i}_amount`] = 'Debe haber un monto en débito o crédito'
        } else {
          hasValidLines = true
        }
      }

      if (!hasValidLines) {
        errors.lines = 'Debe haber al menos una línea válida con monto'
      }

      return Object.keys(errors).length === 0
    }

    const handleSubmit = async () => {
      if (!validateForm()) {
        return
      }

      if (!currentCompany.value) {
        toast.error('Selecciona una empresa primero')
        return
      }

      loading.value = true
      try {
        // Preparar datos con el formato correcto
        const data = {
          entry_number: form.entry_number,
          date: new Date(form.date + 'T00:00:00.000Z'), // Convertir a datetime
          description: form.description,
          entry_type: form.entry_type,
          document_type_id: form.document_type_id,
          document_type_code: form.document_type_code,
          lines: form.lines.map(line => ({
            account_code: line.account_code,
            account_name: line.account_name,
            description: line.description,
            debit: parseFloat(line.debit) || 0,
            credit: parseFloat(line.credit) || 0,
            reference: line.reference || null
          }))
        }
        
        console.log('Enviando datos al backend:', data)
        console.log('Company ID:', currentCompany.value.id)
        
        if (isEdit.value) {
          const response = await api.put(`/journal/${route.params.id}/`, data)
          console.log('Respuesta del backend:', response.data)
          toast.success('Asiento actualizado exitosamente')
        } else {
          const response = await api.post('/journal/', data, {
            params: { company_id: currentCompany.value.id }
          })
          console.log('Respuesta del backend:', response.data)
          toast.success('Asiento creado exitosamente')
        }
        
        router.push('/journal')
      } catch (error) {
        console.error('Error saving journal entry:', error)
        console.error('Error response:', error.response?.data)
        console.error('Error status:', error.response?.status)
        
        let errorMessage = 'Error al guardar asiento'
        if (error.response?.data?.detail) {
          errorMessage = error.response.data.detail
        } else if (error.response?.data?.message) {
          errorMessage = error.response.data.message
        } else if (error.message) {
          errorMessage = error.message
        }
        
        toast.error(errorMessage)
      } finally {
        loading.value = false
      }
    }

    const formatCurrency = (amount) => {
      return new Intl.NumberFormat('es-EC', {
        style: 'currency',
        currency: 'USD'
      }).format(amount)
    }

    // Lifecycle
    onMounted(async () => {
      await Promise.all([loadAccounts(), loadDocumentTypes()])
      await loadJournalEntry()
    })

    return {
      form,
      errors,
      loading,
      isEdit,
      accounts,
      accountTypes,
      documentTypes,
      reserving,
      onChangeDocumentType,
      reserveNumber,
      totalDebit,
      totalCredit,
      isBalanced,
      addLine,
      removeLine,
      updateAccountName,
      calculateTotals,
      handleSubmit,
      formatCurrency,
      getAccountDisplayText,
      getSelectedAccountType
    }
  }
}
</script>

<style scoped>
.btn {
  min-width: 120px;
}

.spinner-border-sm {
  width: 1rem;
  height: 1rem;
}

.table th {
  font-size: 0.875rem;
  font-weight: 600;
}

.form-control-sm, .form-select-sm {
  font-size: 0.875rem;
}

.card.bg-success, .card.bg-danger {
  border: none;
}

/* Estilos para el selector de cuentas jerárquico */
optgroup {
  font-weight: bold;
  color: #495057;
  background-color: #f8f9fa;
}

option[disabled] {
  color: #6c757d;
  font-style: italic;
  background-color: #f8f9fa;
}

option:not([disabled]) {
  color: #212529;
}

/* Indentación para cuentas hijas */
option {
  padding-left: 10px;
}
</style>

