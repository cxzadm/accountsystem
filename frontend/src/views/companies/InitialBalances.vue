<template>
  <div class="initial-balances-page">
    <!-- Page Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h1 class="h3 mb-0">Saldos Iniciales</h1>
        <p class="text-muted">
          Gestiona los saldos iniciales del plan de cuentas para {{ company?.name }}
        </p>
        <small class="text-info" v-if="calculatingBalances">
          <i class="fas fa-sync-alt fa-spin me-1"></i>
          Calculando saldos padre automáticamente...
        </small>
      </div>
      <div>
        <button
          class="btn btn-outline-info me-2"
          @click="showCreateAccountModal = true"
          :disabled="loading"
        >
          <i class="fas fa-plus me-2"></i>
          Nueva Cuenta
        </button>
        <button
          class="btn btn-outline-success me-2"
          @click="exportToExcel"
          :disabled="loading"
        >
          <i class="fas fa-file-excel me-2"></i>
          Exportar Excel
        </button>
        <button
          class="btn btn-outline-primary me-2"
          @click="showImportModal = true"
          :disabled="loading"
        >
          <i class="fas fa-file-import me-2"></i>
          Importar Excel
        </button>
        <button
          class="btn btn-primary"
          @click="saveBalances"
          :disabled="loading || !hasChanges"
        >
          <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
          {{ loading ? 'Guardando...' : 'Guardar Cambios' }}
        </button>
      </div>
    </div>

    <!-- Filters -->
    <div class="card mb-4">
      <div class="card-body">
        <div class="row">
          <div class="col-md-4">
            <label for="search" class="form-label">Buscar cuenta</label>
            <input
              type="text"
              class="form-control"
              id="search"
              v-model="searchTerm"
              placeholder="Código o nombre de cuenta"
            />
          </div>
          <div class="col-md-3">
            <label for="accountType" class="form-label">Tipo de cuenta</label>
            <select class="form-select" id="accountType" v-model="filterType">
              <option value="">Todos los tipos</option>
              <option value="activo">Activo</option>
              <option value="pasivo">Pasivo</option>
              <option value="patrimonio">Patrimonio</option>
              <option value="ingresos">Ingresos</option>
              <option value="gastos">Gastos</option>
              <option value="costos">Costos</option>
            </select>
          </div>
          <div class="col-md-3">
            <label for="showOnlyWithBalances" class="form-label">Mostrar</label>
            <select class="form-select" id="showOnlyWithBalances" v-model="showOnlyWithBalances">
              <option value="all">Todas las cuentas</option>
              <option value="with-balances">Solo con saldos</option>
              <option value="without-balances">Solo sin saldos</option>
            </select>
          </div>
          <div class="col-md-2 d-flex align-items-end">
            <button class="btn btn-outline-secondary" @click="clearFilters">
              Limpiar filtros
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Summary Cards -->
    <div class="row mb-4" v-if="initialized && filteredAccounts">
      <div class="col-md-3">
        <div class="card bg-light">
          <div class="card-body text-center">
            <h5 class="card-title text-primary">{{ filteredAccounts?.length || 0 }}</h5>
            <p class="card-text">Cuentas mostradas</p>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card bg-light">
          <div class="card-body text-center">
            <h5 class="card-title text-success">{{ formatCurrency(totalDebit) }}</h5>
            <p class="card-text">Total Débito</p>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card bg-light">
          <div class="card-body text-center">
            <h5 class="card-title text-danger">{{ formatCurrency(totalCredit) }}</h5>
            <p class="card-text">Total Crédito</p>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card bg-light">
          <div class="card-body text-center">
            <h5 class="card-title" :class="isBalanced ? 'text-success' : 'text-warning'">
              {{ formatCurrency(Math.abs(totalDebit - totalCredit)) }}
            </h5>
            <p class="card-text">Diferencia</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="!initialized" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Cargando...</span>
      </div>
      <p class="mt-3 text-muted">Cargando plan de cuentas...</p>
    </div>

    <!-- Accounts Table -->
    <div v-else class="card" :key="tableKey">
      <div class="card-body">
        <div class="table-responsive">
          <table class="table table-hover">
            <thead>
              <tr>
                <th>Código</th>
                <th>Cuenta</th>
                <th>Tipo</th>
                <th>Naturaleza</th>
                <th>Padre/Hija</th>
                <th>Saldo Débito</th>
                <th>Saldo Crédito</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="loading">
                <td colspan="8" class="text-center py-4">
                  <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Cargando...</span>
                  </div>
                </td>
              </tr>
              <tr v-else-if="!paginatedAccounts || paginatedAccounts.length === 0">
                <td colspan="8" class="text-center py-4 text-muted">
                  No se encontraron cuentas
                </td>
              </tr>
              <tr v-else v-for="account in (paginatedAccounts || [])" :key="account.id" 
                  :class="getAccountRowClass(account)">
                <td>
                  <code :style="{ paddingLeft: (account.level - 1) * 20 + 'px' }">
                    {{ account.code }}
                  </code>
                </td>
                <td :style="{ paddingLeft: (account.level - 1) * 20 + 'px' }">
                  {{ account.name }}
                </td>
                <td>
                  <span class="badge" :class="getAccountTypeClass(account.account_type)">
                    {{ getAccountTypeLabel(account.account_type) }}
                  </span>
                </td>
                <td>
                  <span class="badge" :class="getNatureClass(account.nature)">
                    {{ getNatureLabel(account.nature) }}
                  </span>
                </td>
                <td class="text-center">
                  <span class="badge" :class="getRelationshipClass(account)">
                    {{ getRelationshipType(account) }}
                  </span>
                </td>
                <td>
                  <input
                    type="number"
                    class="form-control form-control-sm"
                    v-model.number="account.initial_debit_balance"
                    step="0.01"
                    min="0"
                    @input="markAsChanged(account)"
                  />
                </td>
                <td>
                  <input
                    type="number"
                    class="form-control form-control-sm"
                    v-model.number="account.initial_credit_balance"
                    step="0.01"
                    min="0"
                    @input="markAsChanged(account)"
                  />
                </td>
                <td>
                  <button
                    class="btn btn-sm btn-outline-secondary"
                    @click="clearAccountBalances(account)"
                    title="Limpiar saldos"
                  >
                    <i class="fas fa-eraser"></i>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Pagination -->
        <nav v-if="totalPages > 1">
          <ul class="pagination justify-content-center">
            <li class="page-item" :class="{ disabled: currentPage === 1 }">
              <button class="page-link" @click="currentPage = 1">Primera</button>
            </li>
            <li class="page-item" :class="{ disabled: currentPage === 1 }">
              <button class="page-link" @click="currentPage--">Anterior</button>
            </li>
            <li
              v-for="page in visiblePages"
              :key="page"
              class="page-item"
              :class="{ active: page === currentPage }"
            >
              <button class="page-link" @click="currentPage = page">{{ page }}</button>
            </li>
            <li class="page-item" :class="{ disabled: currentPage === totalPages }">
              <button class="page-link" @click="currentPage++">Siguiente</button>
            </li>
            <li class="page-item" :class="{ disabled: currentPage === totalPages }">
              <button class="page-link" @click="currentPage = totalPages">Última</button>
            </li>
          </ul>
        </nav>
      </div>
    </div>

    <!-- Import Modal -->
    <div
      class="modal fade"
      :class="{ show: showImportModal }"
      :style="{ display: showImportModal ? 'block' : 'none' }"
      tabindex="-1"
    >
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Importar Saldos desde Excel</h5>
            <button
              type="button"
              class="btn-close"
              @click="showImportModal = false"
            ></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <label for="excelFile" class="form-label">Archivo Excel</label>
              <input
                type="file"
                class="form-control"
                id="excelFile"
                accept=".xlsx,.xls"
                @change="handleFileUpload"
              />
              <div class="form-text">
                El archivo debe contener las columnas: Código, Cuenta, Tipo, Naturaleza, Código Padre, Nivel, Padre/Hija, Saldo Débito, Saldo Crédito
              </div>
            </div>

            <!-- Preview -->
            <div v-if="importPreview.length > 0" class="mt-4">
              <h6>Vista previa de datos:</h6>
              <div class="table-responsive">
                <table class="table table-sm">
                  <thead>
                    <tr>
                      <th>Código</th>
                      <th>Cuenta</th>
                      <th>Tipo</th>
                      <th>Naturaleza</th>
                      <th>Código Padre</th>
                      <th>Nivel</th>
                      <th>Padre/Hija</th>
                      <th>Saldo Débito</th>
                      <th>Saldo Crédito</th>
                      <th>Estado</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(row, index) in importPreview.slice(0, 10)" :key="index">
                      <td>{{ row.code }}</td>
                      <td>{{ row.name }}</td>
                      <td>
                        <span class="badge bg-primary">{{ row.account_type || 'N/A' }}</span>
                      </td>
                      <td>
                        <span class="badge bg-success">{{ row.nature || 'N/A' }}</span>
                      </td>
                      <td>{{ row.parent_code || '-' }}</td>
                      <td>{{ row.level || 1 }}</td>
                      <td>
                        <span class="badge" :class="row.relationship === 'P' ? 'bg-info' : 'bg-secondary'">
                          {{ row.relationship || 'N/A' }}
                        </span>
                      </td>
                      <td>{{ formatCurrency(row.debit) }}</td>
                      <td>{{ formatCurrency(row.credit) }}</td>
                      <td>
                        <span
                          class="badge"
                          :class="row.valid ? 'bg-success' : 'bg-danger'"
                        >
                          {{ row.valid ? 'Válido' : 'Error' }}
                        </span>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
              <p class="text-muted">
                Mostrando {{ Math.min(10, importPreview.length) }} de {{ importPreview.length }} registros
              </p>
            </div>
          </div>
          <div class="modal-footer">
            <button
              type="button"
              class="btn btn-secondary"
              @click="showImportModal = false"
            >
              Cancelar
            </button>
            <button
              type="button"
              class="btn btn-primary"
              @click="importBalances"
              :disabled="importPreview.length === 0 || importing"
            >
              <span v-if="importing" class="spinner-border spinner-border-sm me-2"></span>
              {{ importing ? 'Importando...' : 'Importar' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Account Modal -->
    <div
      class="modal fade"
      :class="{ show: showCreateAccountModal }"
      :style="{ display: showCreateAccountModal ? 'block' : 'none' }"
      tabindex="-1"
    >
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Nueva Cuenta Contable</h5>
            <button
              type="button"
              class="btn-close"
              @click="closeCreateAccountModal"
            ></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="createAccount">
              <div class="row">
                <div class="col-md-6">
                  <div class="mb-3">
                    <label for="accountCode" class="form-label">Código de Cuenta *</label>
                    <input
                      type="text"
                      class="form-control"
                      id="accountCode"
                      v-model="newAccount.code"
                      placeholder="Ej: 1101"
                      required
                    />
                    <div class="form-text">Código único de la cuenta contable</div>
                  </div>
                </div>
                <div class="col-md-6">
                  <div class="mb-3">
                    <label for="accountName" class="form-label">Nombre de Cuenta *</label>
                    <input
                      type="text"
                      class="form-control"
                      id="accountName"
                      v-model="newAccount.name"
                      placeholder="Ej: CAJA"
                      required
                    />
                  </div>
                </div>
              </div>
              
              <div class="row">
                <div class="col-md-6">
                  <div class="mb-3">
                    <label for="accountType" class="form-label">Tipo de Cuenta *</label>
                    <select class="form-select" id="accountType" v-model="newAccount.account_type" required>
                      <option value="">Seleccionar tipo</option>
                      <option value="activo">Activo</option>
                      <option value="pasivo">Pasivo</option>
                      <option value="patrimonio">Patrimonio</option>
                      <option value="ingresos">Ingresos</option>
                      <option value="gastos">Gastos</option>
                      <option value="costos">Costos</option>
                    </select>
                  </div>
                </div>
                <div class="col-md-6">
                  <div class="mb-3">
                    <label for="accountNature" class="form-label">Naturaleza *</label>
                    <select class="form-select" id="accountNature" v-model="newAccount.nature" required>
                      <option value="">Seleccionar naturaleza</option>
                      <option value="deudora">Deudora</option>
                      <option value="acreedora">Acreedora</option>
                    </select>
                  </div>
                </div>
              </div>

              <div class="row">
                <div class="col-md-6">
                  <div class="mb-3">
                    <label for="parentCode" class="form-label">Código Padre</label>
                    <select class="form-select" id="parentCode" v-model="newAccount.parent_code" @change="updateAccountLevel">
                      <option value="">Seleccionar cuenta padre</option>
                      <option 
                        v-for="account in parentAccounts" 
                        :key="account.id" 
                        :value="account.code"
                      >
                        {{ account.code }} - {{ account.name }}
                      </option>
                    </select>
                    <div class="form-text">Seleccione la cuenta padre para crear una cuenta hija</div>
                  </div>
                </div>
                <div class="col-md-6">
                  <div class="mb-3">
                    <label for="accountLevel" class="form-label">Nivel</label>
                    <input
                      type="number"
                      class="form-control"
                      id="accountLevel"
                      v-model.number="newAccount.level"
                      min="1"
                      max="5"
                      placeholder="1"
                      readonly
                    />
                    <div class="form-text">Nivel calculado automáticamente</div>
                  </div>
                </div>
              </div>

              <div class="row">
                <div class="col-md-6">
                  <div class="mb-3">
                    <label for="accountType" class="form-label">Tipo de Relación</label>
                    <select class="form-select" id="accountType" v-model="newAccount.account_relationship_type">
                      <option value="P">Padre (P)</option>
                      <option value="H">Hija (H)</option>
                    </select>
                    <div class="form-text">Tipo de cuenta en la jerarquía</div>
                  </div>
                </div>
                <div class="col-md-6">
                  <div class="mb-3">
                    <label for="suggestedCode" class="form-label">Código Sugerido</label>
                    <input
                      type="text"
                      class="form-control"
                      id="suggestedCode"
                      v-model="suggestedCode"
                      readonly
                    />
                    <div class="form-text">Código sugerido basado en la jerarquía</div>
                  </div>
                </div>
              </div>

              <div class="mb-3">
                <label for="accountDescription" class="form-label">Descripción</label>
                <textarea
                  class="form-control"
                  id="accountDescription"
                  v-model="newAccount.description"
                  rows="3"
                  placeholder="Descripción detallada de la cuenta..."
                ></textarea>
              </div>

              <div class="row">
                <div class="col-md-6">
                  <div class="mb-3">
                    <label for="initialDebit" class="form-label">Saldo Inicial Débito</label>
                    <input
                      type="number"
                      class="form-control"
                      id="initialDebit"
                      v-model.number="newAccount.initial_debit_balance"
                      step="0.01"
                      min="0"
                      placeholder="0.00"
                    />
                  </div>
                </div>
                <div class="col-md-6">
                  <div class="mb-3">
                    <label for="initialCredit" class="form-label">Saldo Inicial Crédito</label>
                    <input
                      type="number"
                      class="form-control"
                      id="initialCredit"
                      v-model.number="newAccount.initial_credit_balance"
                      step="0.01"
                      min="0"
                      placeholder="0.00"
                    />
                  </div>
                </div>
              </div>

              <div class="form-check">
                <input
                  class="form-check-input"
                  type="checkbox"
                  id="isEditable"
                  v-model="newAccount.is_editable"
                />
                <label class="form-check-label" for="isEditable">
                  Cuenta editable
                </label>
                <div class="form-text">Permitir modificar esta cuenta en el futuro</div>
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button
              type="button"
              class="btn btn-secondary"
              @click="closeCreateAccountModal"
            >
              Cancelar
            </button>
            <button
              type="button"
              class="btn btn-primary"
              @click="createAccount"
              :disabled="creatingAccount"
            >
              <span v-if="creatingAccount" class="spinner-border spinner-border-sm me-2"></span>
              {{ creatingAccount ? 'Creando...' : 'Crear Cuenta' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal Backdrop -->
    <div
      v-if="showImportModal || showCreateAccountModal"
      class="modal-backdrop fade show"
      @click="closeAllModals"
    ></div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useToast } from 'vue-toastification'
import { useCompanyStore } from '@/stores/company'
import api from '@/services/api'
import * as XLSX from 'xlsx'

export default {
  name: 'InitialBalances',
  setup() {
    const route = useRoute()
    const router = useRouter()
    const toast = useToast()
    const companyStore = useCompanyStore()

    // State
    const loading = ref(false)
    const calculatingBalances = ref(false)
    const importing = ref(false)
    const creatingAccount = ref(false)
    const accounts = ref([])
    const changedAccounts = ref(new Set())
    const showImportModal = ref(false)
    const showCreateAccountModal = ref(false)
    const importPreview = ref([])
    const uploadedFile = ref(null)
    const initialized = ref(false)
    const tableKey = ref(0)

    // New account form
    const newAccount = reactive({
      code: '',
      name: '',
      description: '',
      account_type: '',
      nature: '',
      parent_code: '',
      level: 1,
      account_relationship_type: 'H',
      initial_debit_balance: 0,
      initial_credit_balance: 0,
      is_editable: true
    })

    const suggestedCode = ref('')

    // Filters
    const searchTerm = ref('')
    const filterType = ref('')
    const showOnlyWithBalances = ref('all')
    const currentPage = ref(1)
    const itemsPerPage = 50

    // Computed
    const company = computed(() => companyStore.getCurrentCompany())

    const filteredAccounts = computed(() => {
      try {
        // Asegurar que siempre retornamos un array
        if (!accounts.value || !Array.isArray(accounts.value)) {
          console.log('filteredAccounts: accounts.value is not an array:', accounts.value)
          return []
        }

        let filtered = [...accounts.value]
        console.log('filteredAccounts: starting with', filtered.length, 'accounts')

        // Search filter
        if (searchTerm.value) {
          const term = searchTerm.value.toLowerCase()
          filtered = filtered.filter(account =>
            account.code.toLowerCase().includes(term) ||
            account.name.toLowerCase().includes(term)
          )
          console.log('filteredAccounts: after search filter:', filtered.length)
        }

        // Type filter
        if (filterType.value) {
          filtered = filtered.filter(account => account.account_type === filterType.value)
          console.log('filteredAccounts: after type filter:', filtered.length)
        }

        // Balance filter
        if (showOnlyWithBalances.value === 'with-balances') {
          filtered = filtered.filter(account =>
            account.initial_debit_balance > 0 || account.initial_credit_balance > 0
          )
          console.log('filteredAccounts: after with-balances filter:', filtered.length)
        } else if (showOnlyWithBalances.value === 'without-balances') {
          filtered = filtered.filter(account =>
            account.initial_debit_balance === 0 && account.initial_credit_balance === 0
          )
          console.log('filteredAccounts: after without-balances filter:', filtered.length)
        }

        console.log('filteredAccounts: final result:', filtered.length)
        return filtered
      } catch (error) {
        console.error('Error in filteredAccounts computed:', error)
        return []
      }
    })

    const paginatedAccounts = computed(() => {
      const start = (currentPage.value - 1) * itemsPerPage
      const end = start + itemsPerPage
      return (filteredAccounts.value || []).slice(start, end)
    })

    const totalPages = computed(() => {
      return Math.ceil((filteredAccounts.value || []).length / itemsPerPage)
    })

    const visiblePages = computed(() => {
      const pages = []
      const start = Math.max(1, currentPage.value - 2)
      const end = Math.min(totalPages.value, currentPage.value + 2)
      
      for (let i = start; i <= end; i++) {
        pages.push(i)
      }
      return pages
    })

    const totalDebit = computed(() => {
      return (filteredAccounts.value || []).reduce((sum, account) => 
        sum + (account.initial_debit_balance || 0), 0
      )
    })

    const totalCredit = computed(() => {
      return (filteredAccounts.value || []).reduce((sum, account) => 
        sum + (account.initial_credit_balance || 0), 0
      )
    })

    const isBalanced = computed(() => {
      return Math.abs(totalDebit.value - totalCredit.value) < 0.01
    })

    const hasChanges = computed(() => {
      return changedAccounts.value.size > 0
    })

    // Computed for parent accounts (can have children)
    const parentAccounts = computed(() => {
      if (!accounts.value || !Array.isArray(accounts.value)) return []
      
      // Sort accounts by code to maintain hierarchy
      return accounts.value
        .filter(account => account.is_active)
        .sort((a, b) => a.code.localeCompare(b.code, undefined, { numeric: true }))
    })

    // Watch for changes in parent code to update level and suggested code
    watch(() => newAccount.parent_code, (newParentCode) => {
      updateAccountLevel()
      generateSuggestedCode()
    })

    watch(() => newAccount.account_relationship_type, () => {
      generateSuggestedCode()
    })

    watch(() => newAccount.account_type, () => {
      generateSuggestedCode()
    })

    // Methods
    const loadAccounts = async () => {
      if (!company.value) {
        console.warn('No company selected')
        return
      }

      console.log('Loading accounts for company:', company.value.id)
      loading.value = true
      try {
        // Ejecutar cálculo automático de saldos padre antes de cargar datos
        calculatingBalances.value = true
        try {
          console.log('🔄 Ejecutando cálculo automático de saldos padre...')
          await api.post('/accounts/fix-complete-hierarchy', {}, {
            params: { company_id: company.value.id }
          })
          console.log('✅ Cálculo automático de saldos padre completado')
        } catch (calcError) {
          console.warn('⚠️ Error en cálculo automático de saldos padre:', calcError)
          // No interrumpir la carga si falla el cálculo automático
        } finally {
          calculatingBalances.value = false
        }

        const response = await api.get('/accounts', {
          params: { 
            company_id: company.value.id, 
            is_active: true,
            limit: 1000
          }
        })
        console.log('API Response:', response)
        accounts.value = response.data || []
        console.log('Accounts loaded:', accounts.value.length, accounts.value)
        initialized.value = true
      } catch (error) {
        console.error('Error loading accounts:', error)
        toast.error('Error al cargar cuentas')
        accounts.value = []
        initialized.value = true
      } finally {
        loading.value = false
      }
    }

    const markAsChanged = (account) => {
      changedAccounts.value.add(account.id)
      // Calcular automáticamente saldos de cuentas padre
      updateParentBalances(account)
    }

    const clearAccountBalances = (account) => {
      account.initial_debit_balance = 0
      account.initial_credit_balance = 0
      markAsChanged(account)
    }

    const updateParentBalances = (childAccount) => {
      // Encontrar todas las cuentas padre en la jerarquía
      const parentCodes = []
      
      // Construir la jerarquía de padres basándose en el código
      let currentCode = childAccount.code
      while (currentCode.length > 1) {
        // Remover los últimos 2 dígitos para obtener el padre
        const parentCode = currentCode.length > 2 ? currentCode.slice(0, -2) : currentCode.slice(0, -1)
        if (parentCode !== currentCode) {
          parentCodes.push(parentCode)
          currentCode = parentCode
        } else {
          break
        }
      }
      
      // También incluir parent_code directo si existe
      if (childAccount.parent_code && !parentCodes.includes(childAccount.parent_code)) {
        parentCodes.push(childAccount.parent_code)
      }
      
      // Actualizar saldos de cada cuenta padre
      for (const parentCode of parentCodes) {
        const parentAccount = accounts.value.find(acc => acc.code === parentCode)
        if (parentAccount) {
          calculateParentBalance(parentAccount)
        }
      }
    }

    const calculateParentBalance = (parentAccount) => {
      // Encontrar todas las cuentas hijas de esta cuenta padre
      const children = accounts.value.filter(acc => 
        acc.parent_code === parentAccount.code || 
        (acc.code.startsWith(parentAccount.code) && 
         acc.code !== parentAccount.code && 
         acc.code.length === parentAccount.code.length + 2)
      )
      
      // Calcular saldos totales de las cuentas hijas
      let totalDebit = 0
      let totalCredit = 0
      
      for (const child of children) {
        totalDebit += child.initial_debit_balance || 0
        totalCredit += child.initial_credit_balance || 0
      }
      
      // Actualizar saldos de la cuenta padre
      parentAccount.initial_debit_balance = totalDebit
      parentAccount.initial_credit_balance = totalCredit
      
      // Marcar como cambiada
      changedAccounts.value.add(parentAccount.id)
      
      console.log(`💰 Actualizado saldo de cuenta padre ${parentAccount.code}: D=${totalDebit}, C=${totalCredit}`)
    }

    const clearFilters = () => {
      searchTerm.value = ''
      filterType.value = ''
      showOnlyWithBalances.value = 'all'
      currentPage.value = 1
    }

    const saveBalances = async () => {
      if (!hasChanges.value) return

      loading.value = true
      try {
        const changedAccountsData = accounts.value
          .filter(account => changedAccounts.value.has(account.id))
          .map(account => ({
            account_code: account.code,
            initial_debit_balance: account.initial_debit_balance || 0,
            initial_credit_balance: account.initial_credit_balance || 0
          }))

        const response = await api.put('/accounts/initial-balances', {
          balances: changedAccountsData
        }, {
          params: { company_id: company.value.id }
        })

        toast.success(response.data.message)
        changedAccounts.value.clear()

        // Ejecutar cálculo automático de saldos padre después de guardar
        try {
          console.log('🔄 Ejecutando cálculo automático de saldos padre después de guardar...')
          await api.post('/accounts/fix-complete-hierarchy', {}, {
            params: { company_id: company.value.id }
          })
          console.log('✅ Cálculo automático de saldos padre completado')
          
          // Recargar cuentas para mostrar los saldos actualizados
          await loadAccounts()
        } catch (calcError) {
          console.warn('⚠️ Error en cálculo automático de saldos padre:', calcError)
          // Recargar cuentas de todas formas para mostrar los cambios guardados
          await loadAccounts()
        }
      } catch (error) {
        console.error('Error saving balances:', error)
        toast.error('Error al guardar saldos')
      } finally {
        loading.value = false
      }
    }

    const exportToExcel = async () => {
      try {
        // Si no hay cuentas, generar plantilla
        if (!accounts.value || accounts.value.length === 0) {
          generateTemplateExcel()
          return
        }

        const response = await api.get('/accounts/export-chart', {
          params: { company_id: company.value.id }
        })

        const data = response.data.map(account => ({
          'Código': account.code,
          'Cuenta': account.name,
          'Tipo': account.account_type,
          'Naturaleza': account.nature,
          'Código Padre': account.parent_code || '',
          'Nivel': account.level || 1,
          'Padre/Hija': getRelationshipType(account),
          'Saldo Débito': account.initial_debit_balance,
          'Saldo Crédito': account.initial_credit_balance
        }))

        const ws = XLSX.utils.json_to_sheet(data)
        const wb = XLSX.utils.book_new()
        XLSX.utils.book_append_sheet(wb, ws, 'Plan de Cuentas')

        const fileName = `plan_cuentas_${company.value.name}_${new Date().toISOString().split('T')[0]}.xlsx`
        XLSX.writeFile(wb, fileName)

        toast.success('Archivo exportado exitosamente')
      } catch (error) {
        console.error('Error exporting:', error)
        // Si hay error de red, generar plantilla
        if (error.code === 'ERR_NETWORK' || error.response?.status >= 500) {
          toast.warning('No se pudo conectar con el servidor. Generando plantilla...')
          generateTemplateExcel()
        } else {
          toast.error('Error al exportar archivo')
        }
      }
    }

    const generateTemplateExcel = () => {
      // Datos de plantilla con estructura jerárquica de ejemplo
      const templateData = [
        { 'Código': '1', 'Cuenta': 'Activo', 'Tipo': 'activo', 'Naturaleza': 'deudora', 'Código Padre': '', 'Nivel': 1, 'Padre/Hija': 'P', 'Saldo Débito': 0, 'Saldo Crédito': 0 },
        { 'Código': '101', 'Cuenta': 'Activo corriente', 'Tipo': 'activo', 'Naturaleza': 'deudora', 'Código Padre': '1', 'Nivel': 2, 'Padre/Hija': 'P', 'Saldo Débito': 0, 'Saldo Crédito': 0 },
        { 'Código': '10101', 'Cuenta': 'Efectivo y equivalentes al efectivo', 'Tipo': 'activo', 'Naturaleza': 'deudora', 'Código Padre': '101', 'Nivel': 3, 'Padre/Hija': 'P', 'Saldo Débito': 0, 'Saldo Crédito': 0 },
        { 'Código': '1010101', 'Cuenta': 'CAJAS VENTA', 'Tipo': 'activo', 'Naturaleza': 'deudora', 'Código Padre': '10101', 'Nivel': 4, 'Padre/Hija': 'P', 'Saldo Débito': 0, 'Saldo Crédito': 0 },
        { 'Código': '101010101', 'Cuenta': 'CAJA 1', 'Tipo': 'activo', 'Naturaleza': 'deudora', 'Código Padre': '1010101', 'Nivel': 5, 'Padre/Hija': 'H', 'Saldo Débito': 0, 'Saldo Crédito': 0 },
        { 'Código': '101010102', 'Cuenta': 'CAJA 2', 'Tipo': 'activo', 'Naturaleza': 'deudora', 'Código Padre': '1010101', 'Nivel': 5, 'Padre/Hija': 'H', 'Saldo Débito': 0, 'Saldo Crédito': 0 },
        { 'Código': '101010103', 'Cuenta': 'CAJA 3', 'Tipo': 'activo', 'Naturaleza': 'deudora', 'Código Padre': '1010101', 'Nivel': 5, 'Padre/Hija': 'H', 'Saldo Débito': 0, 'Saldo Crédito': 0 },
        { 'Código': '1010102', 'Cuenta': 'CAJA CHICA', 'Tipo': 'activo', 'Naturaleza': 'deudora', 'Código Padre': '10101', 'Nivel': 4, 'Padre/Hija': 'P', 'Saldo Débito': 0, 'Saldo Crédito': 0 },
        { 'Código': '101010201', 'Cuenta': 'CAJA CHICA 1', 'Tipo': 'activo', 'Naturaleza': 'deudora', 'Código Padre': '1010102', 'Nivel': 5, 'Padre/Hija': 'H', 'Saldo Débito': 0, 'Saldo Crédito': 0 },
        { 'Código': '101010202', 'Cuenta': 'CAJA CHICA 2', 'Tipo': 'activo', 'Naturaleza': 'deudora', 'Código Padre': '1010102', 'Nivel': 5, 'Padre/Hija': 'H', 'Saldo Débito': 0, 'Saldo Crédito': 0 },
        { 'Código': '1010103', 'Cuenta': 'BANCOS', 'Tipo': 'activo', 'Naturaleza': 'deudora', 'Código Padre': '10101', 'Nivel': 4, 'Padre/Hija': 'P', 'Saldo Débito': 0, 'Saldo Crédito': 0 },
        { 'Código': '101010301', 'Cuenta': 'Banco del Pichincha', 'Tipo': 'activo', 'Naturaleza': 'deudora', 'Código Padre': '1010103', 'Nivel': 5, 'Padre/Hija': 'H', 'Saldo Débito': 0, 'Saldo Crédito': 0 },
        { 'Código': '101010302', 'Cuenta': 'Banco del Austro', 'Tipo': 'activo', 'Naturaleza': 'deudora', 'Código Padre': '1010103', 'Nivel': 5, 'Padre/Hija': 'H', 'Saldo Débito': 0, 'Saldo Crédito': 0 },
        { 'Código': '101010303', 'Cuenta': 'Banco Produbanco', 'Tipo': 'activo', 'Naturaleza': 'deudora', 'Código Padre': '1010103', 'Nivel': 5, 'Padre/Hija': 'H', 'Saldo Débito': 0, 'Saldo Crédito': 0 },
        { 'Código': '2', 'Cuenta': 'Pasivo', 'Tipo': 'pasivo', 'Naturaleza': 'acreedora', 'Código Padre': '', 'Nivel': 1, 'Padre/Hija': 'P', 'Saldo Débito': 0, 'Saldo Crédito': 0 },
        { 'Código': '201', 'Cuenta': 'Pasivo corriente', 'Tipo': 'pasivo', 'Naturaleza': 'acreedora', 'Código Padre': '2', 'Nivel': 2, 'Padre/Hija': 'P', 'Saldo Débito': 0, 'Saldo Crédito': 0 },
        { 'Código': '20101', 'Cuenta': 'CUENTAS POR PAGAR', 'Tipo': 'pasivo', 'Naturaleza': 'acreedora', 'Código Padre': '201', 'Nivel': 3, 'Padre/Hija': 'H', 'Saldo Débito': 0, 'Saldo Crédito': 0 },
        { 'Código': '20102', 'Cuenta': 'IMPUESTOS POR PAGAR', 'Tipo': 'pasivo', 'Naturaleza': 'acreedora', 'Código Padre': '201', 'Nivel': 3, 'Padre/Hija': 'H', 'Saldo Débito': 0, 'Saldo Crédito': 0 },
        { 'Código': '3', 'Cuenta': 'Patrimonio', 'Tipo': 'patrimonio', 'Naturaleza': 'acreedora', 'Código Padre': '', 'Nivel': 1, 'Padre/Hija': 'P', 'Saldo Débito': 0, 'Saldo Crédito': 0 },
        { 'Código': '301', 'Cuenta': 'CAPITAL SOCIAL', 'Tipo': 'patrimonio', 'Naturaleza': 'acreedora', 'Código Padre': '3', 'Nivel': 2, 'Padre/Hija': 'H', 'Saldo Débito': 0, 'Saldo Crédito': 0 },
        { 'Código': '302', 'Cuenta': 'RESERVAS', 'Tipo': 'patrimonio', 'Naturaleza': 'acreedora', 'Código Padre': '3', 'Nivel': 2, 'Padre/Hija': 'H', 'Saldo Débito': 0, 'Saldo Crédito': 0 },
        { 'Código': '4', 'Cuenta': 'Ingresos', 'Tipo': 'ingresos', 'Naturaleza': 'acreedora', 'Código Padre': '', 'Nivel': 1, 'Padre/Hija': 'P', 'Saldo Débito': 0, 'Saldo Crédito': 0 },
        { 'Código': '401', 'Cuenta': 'VENTAS', 'Tipo': 'ingresos', 'Naturaleza': 'acreedora', 'Código Padre': '4', 'Nivel': 2, 'Padre/Hija': 'H', 'Saldo Débito': 0, 'Saldo Crédito': 0 },
        { 'Código': '5', 'Cuenta': 'Gastos', 'Tipo': 'gastos', 'Naturaleza': 'deudora', 'Código Padre': '', 'Nivel': 1, 'Padre/Hija': 'P', 'Saldo Débito': 0, 'Saldo Crédito': 0 },
        { 'Código': '501', 'Cuenta': 'GASTOS DE VENTAS', 'Tipo': 'gastos', 'Naturaleza': 'deudora', 'Código Padre': '5', 'Nivel': 2, 'Padre/Hija': 'H', 'Saldo Débito': 0, 'Saldo Crédito': 0 },
        { 'Código': '6', 'Cuenta': 'Costos', 'Tipo': 'costos', 'Naturaleza': 'deudora', 'Código Padre': '', 'Nivel': 1, 'Padre/Hija': 'P', 'Saldo Débito': 0, 'Saldo Crédito': 0 },
        { 'Código': '601', 'Cuenta': 'COSTO DE VENTAS', 'Tipo': 'costos', 'Naturaleza': 'deudora', 'Código Padre': '6', 'Nivel': 2, 'Padre/Hija': 'H', 'Saldo Débito': 0, 'Saldo Crédito': 0 }
      ]

      const ws = XLSX.utils.json_to_sheet(templateData)
      const wb = XLSX.utils.book_new()
      XLSX.utils.book_append_sheet(wb, ws, 'Plan de Cuentas')

      // Crear hoja de instrucciones
      const instructionsData = [
        ['INSTRUCCIONES PARA USAR ESTA PLANTILLA JERÁRQUICA'],
        [''],
        ['1. Complete los saldos iniciales en las columnas "Saldo Débito" y "Saldo Crédito"'],
        ['2. Los tipos de cuenta válidos son: activo, pasivo, patrimonio, ingresos, gastos, costos'],
        ['3. Las naturalezas válidas son: deudora, acreedora'],
        ['4. Solo complete los saldos en las cuentas que tengan movimientos iniciales'],
        ['5. El total de débitos debe ser igual al total de créditos'],
        ['6. Guarde el archivo y úselo para importar en el sistema'],
        [''],
        ['ESTRUCTURA JERÁRQUICA:'],
        ['- Código Padre: Código de la cuenta padre (vacío para cuentas raíz)'],
        ['- Nivel: Nivel jerárquico (1-5)'],
        ['- Padre/Hija: P = Cuenta padre, H = Cuenta hija'],
        ['- Las cuentas padre pueden tener cuentas hijas'],
        ['- Las cuentas hijas pertenecen a una cuenta padre'],
        [''],
        ['EJEMPLO DE ESTRUCTURA JERÁRQUICA:'],
        ['Código', 'Cuenta', 'Tipo', 'Naturaleza', 'Código Padre', 'Nivel', 'Padre/Hija', 'Saldo Débito', 'Saldo Crédito'],
        ['1', 'Activo', 'activo', 'deudora', '', '1', 'P', '0.00', '0.00'],
        ['101', 'Activo corriente', 'activo', 'deudora', '1', '2', 'P', '0.00', '0.00'],
        ['10101', 'Efectivo', 'activo', 'deudora', '101', '3', 'P', '0.00', '0.00'],
        ['1010101', 'CAJA 1', 'activo', 'deudora', '10101', '4', 'H', '5000.00', '0.00'],
        ['1010102', 'CAJA 2', 'activo', 'deudora', '10101', '4', 'H', '3000.00', '0.00'],
        [''],
        ['NOTAS IMPORTANTES:'],
        ['- No modifique los códigos de cuenta'],
        ['- No modifique los nombres de las cuentas'],
        ['- No modifique la estructura jerárquica (Código Padre, Nivel, Padre/Hija)'],
        ['- Solo modifique los saldos iniciales'],
        ['- Los saldos deben estar en formato numérico (ej: 1000.50)'],
        ['- Use punto como separador decimal'],
        ['- Para crear nuevas cuentas, mantenga la jerarquía correcta']
      ]

      const instructionsWs = XLSX.utils.aoa_to_sheet(instructionsData)
      XLSX.utils.book_append_sheet(wb, instructionsWs, 'Instrucciones')

      const fileName = `plantilla_plan_cuentas_${company.value?.name || 'empresa'}_${new Date().toISOString().split('T')[0]}.xlsx`
      XLSX.writeFile(wb, fileName)

      toast.success('Plantilla Excel generada exitosamente')
    }

    const handleFileUpload = (event) => {
      const file = event.target.files[0]
      if (!file) return

      uploadedFile.value = file
      parseExcelFile(file)
    }

    const parseExcelFile = (file) => {
      const reader = new FileReader()
      reader.onload = (e) => {
        try {
          const data = new Uint8Array(e.target.result)
          const workbook = XLSX.read(data, { type: 'array' })
          const sheetName = workbook.SheetNames[0]
          const worksheet = workbook.Sheets[sheetName]
          const jsonData = XLSX.utils.sheet_to_json(worksheet)

          importPreview.value = jsonData.map((row, index) => {
            const code = row['Código'] || row['codigo'] || row['code'] || ''
            const name = row['Cuenta'] || row['cuenta'] || row['name'] || ''
            const accountType = row['Tipo'] || row['account_type'] || row['tipo'] || ''
            const nature = row['Naturaleza'] || row['nature'] || row['naturaleza'] || ''
            const parentCode = row['Código Padre'] || row['codigo_padre'] || row['parent_code'] || ''
            const level = parseInt(row['Nivel'] || row['nivel'] || row['level'] || 1)
            const relationship = row['Padre/Hija'] || row['padre_hija'] || row['relationship'] || ''
            const description = row['Descripción'] || row['description'] || row['descripcion'] || ''
            const debit = parseFloat(row['Saldo Débito'] || row['saldo_debito'] || row['debit'] || 0)
            const credit = parseFloat(row['Saldo Crédito'] || row['saldo_credito'] || row['credit'] || 0)

            const typeValid = accountType === '' || ['activo', 'pasivo', 'patrimonio', 'ingresos', 'gastos', 'costos'].includes(accountType.toLowerCase())
            const natureValid = nature === '' || ['deudora', 'acreedora'].includes(nature.toLowerCase())
            const relationshipValid = relationship === '' || ['P', 'H', 'p', 'h'].includes(relationship)

            return {
              code: String(code).trim(),
              name: String(name).trim(),
              account_type: accountType.toLowerCase().trim() || '',
              nature: nature.toLowerCase().trim() || '',
              parent_code: String(parentCode).trim() || null,
              level: level,
              relationship: relationship.toUpperCase(),
              description: String(description).trim(),
              debit: debit,
              credit: credit,
              valid: code && name && typeValid && natureValid && relationshipValid
            }
          }).filter(row => row.code && row.name)

          toast.success(`Se encontraron ${importPreview.value.length} registros válidos`)
        } catch (error) {
          console.error('Error parsing Excel:', error)
          toast.error('Error al procesar archivo Excel')
        }
      }
      reader.readAsArrayBuffer(file)
    }

    const importBalances = async () => {
      if (importPreview.value.length === 0) return

      importing.value = true
      try {
        const balancesData = importPreview.value.map(row => ({
          account_code: row.code,
          name: row.name,
          initial_debit_balance: row.debit,
          initial_credit_balance: row.credit,
          account_type: row.account_type || undefined,
          nature: row.nature || undefined,
          parent_code: row.parent_code || undefined,
          level: row.level || 1,
          description: row.description || undefined
        }))

        const response = await api.post('/accounts/import-initial-balances', {
          balances: balancesData
        }, {
          params: { company_id: company.value.id }
        })

        toast.success(response.data.message)
        if (response.data.errors && response.data.errors.length > 0) {
          console.warn('Errores en importación:', response.data.errors)
          toast.warning(`Advertencia: ${response.data.errors.length} errores encontrados`)
        }

        showImportModal.value = false
        importPreview.value = []
        uploadedFile.value = null
        await loadAccounts()
        clearFilters()
        currentPage.value = 1
        await nextTick()
      } catch (error) {
        console.error('Error importing balances:', error)
        toast.error('Error al importar saldos')
      } finally {
        importing.value = false
      }
    }

    const getAccountTypeClass = (type) => {
      const classes = {
        'activo': 'bg-primary',
        'pasivo': 'bg-success',
        'patrimonio': 'bg-info',
        'ingresos': 'bg-warning',
        'gastos': 'bg-danger',
        'costos': 'bg-secondary'
      }
      return classes[type] || 'bg-secondary'
    }

    const getAccountTypeLabel = (type) => {
      const labels = {
        'activo': 'Activo',
        'pasivo': 'Pasivo',
        'patrimonio': 'Patrimonio',
        'ingresos': 'Ingresos',
        'gastos': 'Gastos',
        'costos': 'Costos'
      }
      return labels[type] || type
    }

    const getNatureClass = (nature) => {
      return nature === 'deudora' ? 'bg-primary' : 'bg-success'
    }

    const getNatureLabel = (nature) => {
      return nature === 'deudora' ? 'Deudora' : 'Acreedora'
    }

    const getRelationshipType = (account) => {
      // Check if this account has children
      const hasChildren = accounts.value.some(acc => acc.parent_code === account.code)
      return hasChildren ? 'P' : 'H'
    }

    const getRelationshipClass = (account) => {
      const hasChildren = accounts.value.some(acc => acc.parent_code === account.code)
      return hasChildren ? 'bg-info' : 'bg-secondary'
    }

    const getAccountRowClass = (account) => {
      const hasChildren = accounts.value.some(acc => acc.parent_code === account.code)
      return hasChildren ? 'table-info' : ''
    }

    const formatCurrency = (amount) => {
      return new Intl.NumberFormat('es-EC', {
        style: 'currency',
        currency: 'USD'
      }).format(amount)
    }

    // Create Account methods
    const closeCreateAccountModal = () => {
      showCreateAccountModal.value = false
      resetNewAccountForm()
    }

    const closeAllModals = () => {
      showImportModal.value = false
      showCreateAccountModal.value = false
      resetNewAccountForm()
    }

    const resetNewAccountForm = () => {
      Object.assign(newAccount, {
        code: '',
        name: '',
        description: '',
        account_type: '',
        nature: '',
        parent_code: '',
        level: 1,
        account_relationship_type: 'H',
        initial_debit_balance: 0,
        initial_credit_balance: 0,
        is_editable: true
      })
      suggestedCode.value = ''
    }

    const updateAccountLevel = () => {
      if (!newAccount.parent_code) {
        newAccount.level = 1
        return
      }

      // Find parent account to get its level
      const parentAccount = accounts.value.find(acc => acc.code === newAccount.parent_code)
      if (parentAccount) {
        newAccount.level = (parentAccount.level || 1) + 1
      } else {
        // If parent not found, calculate level from code length
        newAccount.level = Math.ceil(newAccount.parent_code.length / 2) + 1
      }
    }

    const generateSuggestedCode = () => {
      if (!newAccount.parent_code) {
        // For root level accounts, suggest based on account type
        const typeCodes = {
          'activo': '1',
          'pasivo': '2', 
          'patrimonio': '3',
          'ingresos': '4',
          'gastos': '5',
          'costos': '6'
        }
        suggestedCode.value = typeCodes[newAccount.account_type] || '1'
        return
      }

      // Find the next available code for the parent
      const parentAccount = accounts.value.find(acc => acc.code === newAccount.parent_code)
      if (!parentAccount) {
        suggestedCode.value = newAccount.parent_code + '01'
        return
      }

      // Get all children of the parent account
      const children = accounts.value.filter(acc => 
        acc.parent_code === newAccount.parent_code && 
        acc.code.startsWith(newAccount.parent_code) &&
        acc.code !== newAccount.parent_code
      )

      if (children.length === 0) {
        // First child
        suggestedCode.value = newAccount.parent_code + '01'
      } else {
        // Find the next available number
        const parentCodeLength = newAccount.parent_code.length
        const childNumbers = children
          .map(child => {
            const childSuffix = child.code.substring(parentCodeLength)
            return parseInt(childSuffix) || 0
          })
          .sort((a, b) => a - b)

        let nextNumber = 1
        for (const num of childNumbers) {
          if (num === nextNumber) {
            nextNumber++
          } else {
            break
          }
        }

        // Format with leading zeros (2 digits)
        suggestedCode.value = newAccount.parent_code + nextNumber.toString().padStart(2, '0')
      }
    }

    const createAccount = async () => {
      if (!newAccount.name || !newAccount.account_type || !newAccount.nature) {
        toast.error('Por favor complete todos los campos obligatorios')
        return
      }

      // Use suggested code if no code provided
      if (!newAccount.code && suggestedCode.value) {
        newAccount.code = suggestedCode.value
      }

      if (!newAccount.code) {
        toast.error('Por favor ingrese un código de cuenta')
        return
      }

      creatingAccount.value = true
      try {
        const accountData = {
          code: newAccount.code.trim(),
          name: newAccount.name.trim(),
          description: newAccount.description?.trim() || '',
          account_type: newAccount.account_type,
          nature: newAccount.nature,
          parent_code: newAccount.parent_code?.trim() || null,
          level: newAccount.level || 1,
          initial_debit_balance: newAccount.initial_debit_balance || 0,
          initial_credit_balance: newAccount.initial_credit_balance || 0,
          is_editable: newAccount.is_editable
        }

        const response = await api.post('/accounts', accountData, {
          params: { company_id: company.value.id }
        })

        toast.success('Cuenta creada exitosamente')
        closeCreateAccountModal()
        await loadAccounts()
        
        // Marcar la nueva cuenta como cambiada para que aparezca en la lista de cambios
        const newAccountId = response.data.id
        changedAccounts.value.add(newAccountId)
        
      } catch (error) {
        console.error('Error creating account:', error)
        if (error.response?.data?.detail) {
          toast.error(error.response.data.detail)
        } else {
          toast.error('Error al crear la cuenta')
        }
      } finally {
        creatingAccount.value = false
      }
    }

    // Watch for page changes
    watch(currentPage, () => {
      // Reset to first page if current page is beyond total pages
      if (currentPage.value > totalPages.value && totalPages.value > 0) {
        currentPage.value = totalPages.value
      }
    })

    // Lifecycle
    onMounted(async () => {
      await loadAccounts()
    })

    return {
      loading,
      calculatingBalances,
      importing,
      creatingAccount,
      accounts: accounts,
      paginatedAccounts: paginatedAccounts,
      changedAccounts,
      showImportModal,
      showCreateAccountModal,
      importPreview,
      newAccount,
      suggestedCode,
      parentAccounts,
      searchTerm,
      filterType,
      showOnlyWithBalances,
      currentPage,
      totalPages,
      visiblePages,
      totalDebit,
      totalCredit,
      isBalanced,
      hasChanges,
      company,
      initialized,
      loadAccounts,
      markAsChanged,
      clearAccountBalances,
      updateParentBalances,
      calculateParentBalance,
      clearFilters,
      saveBalances,
      exportToExcel,
      generateTemplateExcel,
      handleFileUpload,
      importBalances,
      closeCreateAccountModal,
      closeAllModals,
      resetNewAccountForm,
      updateAccountLevel,
      generateSuggestedCode,
      createAccount,
      getAccountTypeClass,
      getAccountTypeLabel,
      getNatureClass,
      getNatureLabel,
      getRelationshipType,
      getRelationshipClass,
      getAccountRowClass,
      formatCurrency
    }
  }
}
</script>

<style scoped>
.modal.show {
  display: block !important;
}

.modal-backdrop.show {
  opacity: 0.5;
}

.table th {
  font-size: 0.875rem;
  font-weight: 600;
  border-top: none;
}

.form-control-sm {
  font-size: 0.875rem;
}

.badge {
  font-size: 0.75rem;
}

.pagination {
  margin-top: 1rem;
}

.card.bg-light {
  border: 1px solid #dee2e6;
}

.spinner-border-sm {
  width: 1rem;
  height: 1rem;
}

.table-info {
  background-color: rgba(13, 202, 240, 0.1) !important;
}

.table tbody tr.table-info:hover {
  background-color: rgba(13, 202, 240, 0.2) !important;
}

.badge.bg-info {
  background-color: #0dcaf0 !important;
  color: #000;
}

.badge.bg-secondary {
  background-color: #6c757d !important;
}
</style>
