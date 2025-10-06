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
      <div class="col-12">
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
              <div class="d-flex gap-2">
                <button
                  type="button"
                  class="btn btn-outline-info"
                  @click="showHelpModal = true"
                  title="Ayuda para crear asientos"
                >
                  <i class="fas fa-info-circle"></i>
                </button>
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
                <div class="col-md-4">
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
                <div class="col-md-2">
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
                <div class="col-md-3">
                  <div class="mb-3">
                    <label for="responsable" class="form-label">Responsable *</label>
                    <input
                      type="text"
                      class="form-control"
                      id="responsable"
                      v-model="form.responsable"
                      :class="{ 'is-invalid': errors.responsable }"
                      placeholder="Nombre del responsable"
                      required
                    />
                    <div class="invalid-feedback" v-if="errors.responsable">
                      {{ errors.responsable }}
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
                              >
                                {{ getAccountDisplayText(account) }}
                              </option>
                            </optgroup>
                      </select>
                      <small class="text-muted" v-if="line.account_code && getSelectedAccountType(line.account_code) === 'P'">
                            <i class="fas fa-info-circle me-1"></i>
                            Cuenta padre seleccionada
                          </small>
                      <!-- Quick account preview -->
                      <div v-if="line.account_code && getPreview(index).loaded" class="mt-2 p-2 bg-light rounded border">
                        <div class="d-flex justify-content-between align-items-center">
                          <div class="small">
                            <strong>Saldo (D - C):</strong>
                            <span :class="getPreview(index).net >= 0 ? 'text-danger fw-bold' : 'text-success fw-bold'">
                              {{ formatCurrency(getPreview(index).net) }}
                            </span>
                            <span class="text-muted ms-2">(Ini {{ formatCurrency(getPreview(index).initial_net) }})</span>
                          </div>
                          <router-link class="btn btn-xs btn-outline-primary" :to="{ name: 'Ledger', query: { account: line.account_code } }">Ver en Mayor</router-link>
                        </div>
                        <div v-if="getPreview(index).entries && getPreview(index).entries.length" class="mt-2">
                          <div class="text-muted small mb-1">Últimos movimientos:</div>
                          <ul class="list-unstyled mb-0 small">
                            <li v-for="e in (getPreview(index).entries || []).slice(0,3)" :key="e.id || e.date">
                              <span class="text-muted">{{ new Date(e.date).toLocaleDateString() }}:</span>
                              {{ e.description || '-' }}
                              <span class="ms-2 text-danger" v-if="Number(e.debit_amount||0) > 0">D {{ formatCurrency(Number(e.debit_amount||0)) }}</span>
                              <span class="ms-2 text-success" v-if="Number(e.credit_amount||0) > 0">C {{ formatCurrency(Number(e.credit_amount||0)) }}</span>
                            </li>
                          </ul>
                        </div>
                      </div>
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
    </div>

    <!-- Help Modal -->
    <div class="modal fade" :class="{ show: showHelpModal }" :style="{ display: showHelpModal ? 'block' : 'none' }" tabindex="-1">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">
              <i class="fas fa-info-circle me-2 text-info"></i>
              Ayuda para Crear Asientos Contables
            </h5>
            <button type="button" class="btn-close" @click="showHelpModal = false"></button>
          </div>
          <div class="modal-body">
            <div class="row">
              <div class="col-md-6">
                <h6 class="text-primary">
                  <i class="fas fa-balance-scale me-2"></i>
                  Reglas del Asiento
                </h6>
                <ul class="list-unstyled">
                  <li class="mb-2">
                    <i class="fas fa-check-circle text-success me-2"></i>
                    El total de débitos debe igualar al total de créditos
                  </li>
                  <li class="mb-2">
                    <i class="fas fa-check-circle text-success me-2"></i>
                    Al menos debe haber una línea con débito y una con crédito
                  </li>
                  <li class="mb-2">
                    <i class="fas fa-check-circle text-success me-2"></i>
                    Las cuentas deben estar activas en el plan contable
                  </li>
                  <li class="mb-2">
                    <i class="fas fa-check-circle text-success me-2"></i>
                    La descripción debe ser clara y concisa
                  </li>
                </ul>

                <h6 class="text-primary mt-4">
                  <i class="fas fa-magic me-2"></i>
                  Funciones Automáticas
                </h6>
                <ul class="list-unstyled">
                  <li class="mb-2">
                    <i class="fas fa-lightbulb text-warning me-2"></i>
                    <strong>Descripción automática:</strong> Se llena con el nombre de la cuenta seleccionada
                  </li>
                  <li class="mb-2">
                    <i class="fas fa-lightbulb text-warning me-2"></i>
                    <strong>Validación en tiempo real:</strong> Muestra si el asiento está balanceado
                  </li>
                  <li class="mb-2">
                    <i class="fas fa-lightbulb text-warning me-2"></i>
                    <strong>Identificación de cuentas:</strong> Muestra claramente si es cuenta Padre (P) o Hija (H)
                  </li>
                </ul>
              </div>
              <div class="col-md-6">
                <h6 class="text-primary">
                  <i class="fas fa-tags me-2"></i>
                  Tipos de Asiento
                </h6>
                <div class="row">
                  <div class="col-6">
                    <div class="card border-primary mb-2">
                      <div class="card-body p-2">
                        <h6 class="card-title text-primary mb-1">Manual</h6>
                        <p class="card-text small mb-0">Asiento creado manualmente por el usuario</p>
                      </div>
                    </div>
                  </div>
                  <div class="col-6">
                    <div class="card border-success mb-2">
                      <div class="card-body p-2">
                        <h6 class="card-title text-success mb-1">Automático</h6>
                        <p class="card-text small mb-0">Generado automáticamente por el sistema</p>
                      </div>
                    </div>
                  </div>
                  <div class="col-6">
                    <div class="card border-warning mb-2">
                      <div class="card-body p-2">
                        <h6 class="card-title text-warning mb-1">Ajuste</h6>
                        <p class="card-text small mb-0">Para correcciones contables</p>
                      </div>
                    </div>
                  </div>
                  <div class="col-6">
                    <div class="card border-info mb-2">
                      <div class="card-body p-2">
                        <h6 class="card-title text-info mb-1">Cierre</h6>
                        <p class="card-text small mb-0">Para cierre de período contable</p>
                      </div>
                    </div>
                  </div>
                </div>

                <h6 class="text-primary mt-4">
                  <i class="fas fa-tips me-2"></i>
                  Consejos Útiles
                </h6>
                <div class="alert alert-info">
                  <ul class="mb-0 small">
                    <li>Las cuentas <strong>Padre (P)</strong> y <strong>Hija (H)</strong> están claramente identificadas</li>
                    <li>El indicador de balance te muestra si el asiento está correcto</li>
                    <li>La descripción se llena automáticamente al seleccionar una cuenta</li>
                    <li>Usa el botón "Agregar Línea" para crear asientos con múltiples movimientos</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="showHelpModal = false">
              Cerrar
            </button>
          </div>
        </div>
      </div>
    </div>
    <div v-if="showHelpModal" class="modal-backdrop fade show"></div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useToast } from 'vue-toastification'
import { useCompanyStore } from '@/stores/company'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'

export default {
  name: 'JournalForm',
  setup() {
    const route = useRoute()
    const router = useRouter()
    const toast = useToast()
    const companyStore = useCompanyStore()
    const authStore = useAuthStore()

    // State
    const loading = ref(false)
    const accounts = ref([])
    const documentTypes = ref([])
    const reserving = ref(false)
    const showHelpModal = ref(false)

    const form = reactive({
      date: new Date().toISOString().split('T')[0],
      description: '',
      entry_type: 'automatic',
      document_type_id: '',
      document_type_code: '',
      entry_number: '',
      responsable: '',
      lines: [
        { account_code: '', account_name: '', description: '', debit: 0, credit: 0, reference: '' },
        { account_code: '', account_name: '', description: '', debit: 0, credit: 0, reference: '' }
      ]
    })

    const errors = reactive({})
    const previews = ref([])
    const getPreview = (idx) => {
      const p = previews.value && previews.value[idx]
      return p || { loaded: false, initial_net: 0, net: 0, entries: [] }
    }

    // Computed
    const isEdit = computed(() => !!route.params.id)
    const currentCompany = computed(() => companyStore.getCurrentCompany())
    const currentUser = computed(() => authStore.user)
    const userFullName = computed(() => {
      if (currentUser.value.first_name && currentUser.value.last_name) {
        return `${currentUser.value.first_name} ${currentUser.value.last_name}`
      }
      return currentUser.value.username || ''
    })

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

    const fetchPreviewForLine = async (idx) => {
      const line = form.lines[idx]
      if (!line?.account_code || !currentCompany.value) return
      try {
        // Calcular saldos usando la cuenta cargada (coincide con InitialBalances.vue)
        const account = accounts.value.find(a => a.code === line.account_code)
        const initialNet = Number((account?.initial_debit_balance || 0)) - Number((account?.initial_credit_balance || 0))
        const movNet = Number((account?.current_debit_balance || 0)) - Number((account?.current_credit_balance || 0))

        const params = { company_id: currentCompany.value.id }
        let entries = []
        try {
          const accId = getAccountIdByCode(line.account_code)
          if (accId) {
            const entriesResp = await api.get(`/ledger/account/${encodeURIComponent(accId)}/entries/`, { params })
            entries = entriesResp.data?.entries || []
          }
        } catch (e) {
          entries = []
        }
        previews.value[idx] = {
          loaded: true,
          initial_net: initialNet,
          net: initialNet + movNet,
          entries
        }
      } catch (e) {
        // Fallback: minimal preview
        previews.value[idx] = { loaded: true, initial_net: 0, net: 0, entries: [] }
      }
    }

    const getAccountIdByCode = (code) => {
      const acc = accounts.value.find(a => a.code === code)
      return acc ? acc.id : ''
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

    // Función para determinar si una cuenta es padre o hija
    const getRelationshipType = (account) => {
      const hasChildren = accounts.value.some(acc => acc.parent_code === account.code)
      return hasChildren ? 'P' : 'H'
    }

    // Función para mostrar texto de cuenta con jerarquía
    const getAccountDisplayText = (account) => {
      const indent = '  '.repeat(account.level - 1)
      const relationshipType = getRelationshipType(account)
      const typeIndicator = ` (${relationshipType})`
      return `${indent}${account.code} - ${account.name}${typeIndicator}`
    }

    // Función para obtener el tipo de relación de una cuenta seleccionada
    const getSelectedAccountType = (accountCode) => {
      const account = accounts.value.find(acc => acc.code === accountCode)
      return account ? getRelationshipType(account) : null
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

    const updateAccountName = (index) => {
      const line = form.lines[index]
      const account = accounts.value.find(acc => acc.code === line.account_code)
      line.account_name = account ? account.name : ''
      line.description = account ? account.name : ''
      // trigger preview when account changes
      fetchPreviewForLine(index)
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
        form.responsable = entry.responsable || userFullName.value
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
      if (!form.responsable.trim()) {
        errors.responsable = 'El responsable es requerido'
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
          responsable: form.responsable || userFullName.value,
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
      // Inicializar el responsable con el nombre del usuario actual
      if (!isEdit.value) {
        form.responsable = userFullName.value
      }
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
      getPreview,
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
      getSelectedAccountType,
      getRelationshipType,
      showHelpModal
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

/* Ajustar anchos de columnas para mejor visualización */
.table th:nth-child(1),
.table td:nth-child(1) {
  width: 30%;
  min-width: 250px;
}

.table th:nth-child(2),
.table td:nth-child(2) {
  width: 25%;
  min-width: 200px;
}

.table th:nth-child(3),
.table td:nth-child(3) {
  width: 12%;
  min-width: 100px;
}

.table th:nth-child(4),
.table td:nth-child(4) {
  width: 12%;
  min-width: 100px;
}

.table th:nth-child(5),
.table td:nth-child(5) {
  width: 15%;
  min-width: 120px;
}

.table th:nth-child(6),
.table td:nth-child(6) {
  width: 6%;
  min-width: 50px;
}

/* Mejorar el selector de cuentas */
.form-select-sm {
  font-size: 0.85rem;
  padding: 0.4rem 0.6rem;
  min-width: 220px;
  max-width: 100%;
  border-radius: 0.375rem;
  border: 1px solid #ced4da;
  background-color: #fff;
  transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
}

.form-select-sm:focus {
  border-color: #86b7fe;
  outline: 0;
  box-shadow: 0 0 0 0.25rem rgba(13, 110, 253, 0.25);
}

/* Asegurar que el texto del selector sea visible */
.form-select option {
  white-space: nowrap;
  overflow: visible;
  padding: 0.3rem 0.5rem;
  font-size: 0.85rem;
}

/* Mejorar la tabla general */
.table-responsive {
  border-radius: 0.5rem;
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
}

.table {
  margin-bottom: 0;
}

.table th {
  background-color: #f8f9fa;
  border-bottom: 2px solid #dee2e6;
  font-weight: 600;
  color: #495057;
  padding: 0.75rem 0.5rem;
}

.table td {
  padding: 0.6rem 0.5rem;
  vertical-align: middle;
  border-bottom: 1px solid #dee2e6;
}

/* Mejorar los inputs de la tabla */
.table .form-control-sm,
.table .form-select-sm {
  border-radius: 0.375rem;
  border: 1px solid #ced4da;
  transition: all 0.15s ease-in-out;
}

.table .form-control-sm:focus,
.table .form-select-sm:focus {
  border-color: #86b7fe;
  box-shadow: 0 0 0 0.25rem rgba(13, 110, 253, 0.25);
}

/* Mejorar el mensaje informativo */
.table small.text-muted {
  font-size: 0.75rem;
  margin-top: 0.25rem;
  display: block;
  line-height: 1.2;
}
</style>

