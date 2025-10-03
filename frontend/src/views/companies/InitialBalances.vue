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
        <div class="d-inline-block position-relative me-2" ref="exportMenuRef">
          <button
            class="btn btn-outline-success"
            @click.stop="toggleExportMenu"
            :disabled="loading"
          >
            <i class="fas fa-file-excel me-2"></i>
            Exportar
            <i class="fas fa-caret-down ms-1"></i>
          </button>
          <div v-if="showExportMenu" class="export-menu shadow-sm">
            <ul class="list-unstyled mb-0">
              <li>
                <button class="dropdown-item" @click.stop="onExportTemplate">Descargar plantilla</button>
              </li>
              <li>
                <button class="dropdown-item" @click.stop="onExportLoaded">
                  Descargar saldos cargados
                </button>
              </li>
            </ul>
          </div>
        </div>
        <div class="d-inline-block position-relative me-2" ref="clearMenuRef">
          <button
            class="btn btn-outline-danger"
            @click.stop="toggleClearMenu"
            :disabled="loading || clearing"
            title="Pone en 0 saldos iniciales"
          >
            <i class="fas fa-broom me-2"></i>
            Limpiar
            <i class="fas fa-caret-down ms-1"></i>
          </button>
          <div v-if="showClearMenu" class="export-menu shadow-sm">
            <ul class="list-unstyled mb-0">
              <li>
                <button class="dropdown-item" @click.stop="clearBalancesVisible">
                  Limpiar solo saldos visibles
                </button>
              </li>
              <li>
                <button class="dropdown-item text-danger" @click.stop="clearBalancesAll">
                  Limpiar todo
                </button>
              </li>
            </ul>
          </div>
        </div>
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
                  <div class="btn-group" role="group">
                    <button
                      class="btn btn-sm btn-outline-primary"
                      @click="editAccount(account)"
                      title="Editar cuenta"
                      :disabled="!account.is_editable"
                    >
                      <i class="fas fa-edit"></i>
                    </button>
                    <button
                      class="btn btn-sm btn-outline-secondary"
                      @click="clearAccountBalances(account)"
                      title="Limpiar saldos"
                    >
                      <i class="fas fa-eraser"></i>
                    </button>
                    <button
                      class="btn btn-sm btn-outline-danger"
                      @click="deleteAccount(account)"
                      title="Eliminar cuenta"
                      :disabled="!account.is_editable"
                    >
                      <i class="fas fa-trash"></i>
                    </button>
                  </div>
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

    <!-- Account Form Modal -->
    <AccountFormModal
      :show="showCreateAccountModal"
      :account="editingAccount"
      :company-id="company?.id"
      :all-accounts="accounts"
      :on-save="handleSaveAccount"
      @close="closeCreateAccountModal"
    />

    <!-- Modal Backdrop -->
    <div
      v-if="showImportModal || showCreateAccountModal"
      class="modal-backdrop fade show"
      @click="closeAllModals"
    ></div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted, watch, nextTick, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { alerts } from '@/services/alerts'
import { useCompanyStore } from '@/stores/company'
import { useBreadcrumb } from '@/composables/useBreadcrumb'
import api from '@/services/api'
import * as XLSX from 'xlsx'
import AccountFormModal from '@/components/AccountFormModal.vue'

export default {
  name: 'InitialBalances',
  components: {
    AccountFormModal
  },
  setup() {
    const route = useRoute()
    const router = useRouter()
    
    const companyStore = useCompanyStore()
    const { addBreadcrumb, clearBreadcrumbs } = useBreadcrumb()

    // State
    const loading = ref(false)
    const calculatingBalances = ref(false)
    const importing = ref(false)
    const accounts = ref([])
    const changedAccounts = ref(new Set())
    const showExportMenu = ref(false)
    const exportMenuRef = ref(null)
    const showClearMenu = ref(false)
    const clearMenuRef = ref(null)
    const clearing = ref(false)
    const showImportModal = ref(false)
    const showCreateAccountModal = ref(false)
    const editingAccount = ref(null)
    const importPreview = ref([])
    const uploadedFile = ref(null)
    const initialized = ref(false)
    const tableKey = ref(0)

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

    const hasAnyLoadedBalances = computed(() => {
      const list = accounts.value || []
      return list.some(acc => (acc.initial_debit_balance || 0) > 0 || (acc.initial_credit_balance || 0) > 0)
    })

    const hasLoadedBalancesVisible = computed(() => {
      const source = (filteredAccounts.value && filteredAccounts.value.length > 0)
        ? filteredAccounts.value
        : (accounts.value || [])
      return source.some(acc => (acc.initial_debit_balance || 0) > 0 || (acc.initial_credit_balance || 0) > 0)
    })

    // Computed for parent accounts (can have children)
    const parentAccounts = computed(() => {
      if (!accounts.value || !Array.isArray(accounts.value)) return []
      
      // Sort accounts by code to maintain hierarchy
      return accounts.value
        .filter(account => account.is_active)
        .sort((a, b) => a.code.localeCompare(b.code, undefined, { numeric: true }))
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
        alerts.error('Error', 'Error al cargar cuentas')
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

        alerts.success('Éxito', response.data.message)
        changedAccounts.value.clear()

        // Notificar cambio en el store para sincronizar con otras vistas
        companyStore.notifyAccountsChanged()

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
        alerts.error('Error', 'Error al guardar saldos')
      } finally {
        loading.value = false
      }
    }

    const toggleExportMenu = () => {
      showExportMenu.value = !showExportMenu.value
    }

    const onExportTemplate = () => {
      showExportMenu.value = false
      generateTemplateExcel()
    }

    const onExportLoaded = () => {
      showExportMenu.value = false
      exportToExcel()
    }

    const handleClickOutside = (event) => {
      const exportEl = exportMenuRef.value
      const clearEl = clearMenuRef.value
      if (showExportMenu.value && exportEl && !exportEl.contains(event.target)) {
        showExportMenu.value = false
      }
      if (showClearMenu.value && clearEl && !clearEl.contains(event.target)) {
        showClearMenu.value = false
      }
    }

    const exportToExcel = async () => {
      try {
        // Tomar las cuentas actualmente cargadas y filtradas en pantalla
        const sourceAccounts = (filteredAccounts.value && filteredAccounts.value.length > 0)
          ? filteredAccounts.value
          : (accounts.value || [])

        // Si no hay cuentas, generar plantilla
        if (!sourceAccounts || sourceAccounts.length === 0) {
          generateTemplateExcel()
          return
        }

        const data = sourceAccounts.map(account => ({
          'Código': account.code,
          'Cuenta': account.name,
          'Tipo': account.account_type,
          'Naturaleza': account.nature,
          'Saldo Débito': account.initial_debit_balance || 0,
          'Saldo Crédito': account.initial_credit_balance || 0
        }))

        const ws = XLSX.utils.json_to_sheet(data)
        const wb = XLSX.utils.book_new()
        XLSX.utils.book_append_sheet(wb, ws, 'Saldos Iniciales')

        const fileName = `saldos_iniciales_${company.value?.name || 'empresa'}_${new Date().toISOString().split('T')[0]}.xlsx`
        XLSX.writeFile(wb, fileName)

        alerts.success('Éxito', 'Archivo exportado exitosamente')
      } catch (error) {
        console.error('Error exporting:', error)
        alerts.error('Error', 'Error al exportar archivo')
      }
    }

    const toggleClearMenu = () => {
      showClearMenu.value = !showClearMenu.value
    }

    const clearBalances = async (targetAccounts) => {
      if (!targetAccounts || targetAccounts.length === 0) return
      const payload = targetAccounts
        .filter(acc => (acc.initial_debit_balance || 0) !== 0 || (acc.initial_credit_balance || 0) !== 0)
        .map(acc => ({
          account_code: acc.code,
          initial_debit_balance: 0,
          initial_credit_balance: 0
        }))

      if (payload.length === 0) {
        alerts.info('Sin cambios', 'No hay saldos para limpiar')
        return
      }

      clearing.value = true
      try {
        await api.put('/accounts/initial-balances', { balances: payload }, {
          params: { company_id: company.value.id }
        })

        alerts.success('Éxito', 'Saldos iniciales limpiados correctamente')
        await loadAccounts()
        clearFilters()
        currentPage.value = 1
        await nextTick()
      } catch (error) {
        console.error('Error clearing balances:', error)
        alerts.error('Error', 'Error al limpiar saldos')
      } finally {
        clearing.value = false
      }
    }

    const clearBalancesVisible = async () => {
      showClearMenu.value = false
      const confirmed = await alerts.confirm({ title: 'Confirmación', text: '¿Poner en 0 los saldos iniciales de las cuentas visibles?' })
      if (!confirmed) return
      const target = (filteredAccounts.value && filteredAccounts.value.length > 0)
        ? filteredAccounts.value
        : (accounts.value || [])
      await clearBalances(target)
    }

    const clearBalancesAll = async () => {
      showClearMenu.value = false
      const confirmed = await alerts.confirm({ title: 'Confirmación', text: '¿LIMPIAR TODO? Se eliminará el plan de cuentas (forzado).' })
      if (!confirmed) return
      try {
        clearing.value = true
        // Purga forzada directa: borra journal, mayor y cuentas
        await api.delete('/accounts/purge', {
          params: { company_id: company.value.id, force: true }
        })
        alerts.success('Éxito', 'Se eliminó el plan de cuentas (forzado)')
        await loadAccounts()
        clearFilters()
        currentPage.value = 1
        await nextTick()
      } catch (error) {
        console.error('Error eliminando el plan de cuentas:', error)
        alerts.error('Error', 'No se pudo eliminar el plan de cuentas')
      } finally {
        clearing.value = false
      }
    }

    const generateTemplateExcel = () => {
      // Datos de plantilla simplificada (jerarquía se derivará del Código)
      const templateData = [
        { 'Código': '1', 'Cuenta': 'Activo', 'Tipo': 'activo', 'Naturaleza': 'deudora', 'Saldo Débito': 0, 'Saldo Crédito': 0 },
        { 'Código': '101', 'Cuenta': 'Activo corriente', 'Tipo': 'activo', 'Naturaleza': 'deudora', 'Saldo Débito': 0, 'Saldo Crédito': 0 },
        { 'Código': '10101', 'Cuenta': 'Efectivo y equivalentes al efectivo', 'Tipo': 'activo', 'Naturaleza': 'deudora', 'Saldo Débito': 0, 'Saldo Crédito': 0 },
        { 'Código': '1010101', 'Cuenta': 'CAJAS VENTA', 'Tipo': 'activo', 'Naturaleza': 'deudora', 'Saldo Débito': 0, 'Saldo Crédito': 0 },
        { 'Código': '101010101', 'Cuenta': 'CAJA 1', 'Tipo': 'activo', 'Naturaleza': 'deudora', 'Saldo Débito': 0, 'Saldo Crédito': 0 },
        { 'Código': '101010102', 'Cuenta': 'CAJA 2', 'Tipo': 'activo', 'Naturaleza': 'deudora', 'Saldo Débito': 0, 'Saldo Crédito': 0 },
        { 'Código': '101010103', 'Cuenta': 'CAJA 3', 'Tipo': 'activo', 'Naturaleza': 'deudora', 'Saldo Débito': 0, 'Saldo Crédito': 0 },
        { 'Código': '1010102', 'Cuenta': 'CAJA CHICA', 'Tipo': 'activo', 'Naturaleza': 'deudora', 'Saldo Débito': 0, 'Saldo Crédito': 0 },
        { 'Código': '101010201', 'Cuenta': 'CAJA CHICA 1', 'Tipo': 'activo', 'Naturaleza': 'deudora', 'Saldo Débito': 0, 'Saldo Crédito': 0 },
        { 'Código': '101010202', 'Cuenta': 'CAJA CHICA 2', 'Tipo': 'activo', 'Naturaleza': 'deudora', 'Saldo Débito': 0, 'Saldo Crédito': 0 },
        { 'Código': '1010103', 'Cuenta': 'BANCOS', 'Tipo': 'activo', 'Naturaleza': 'deudora', 'Saldo Débito': 0, 'Saldo Crédito': 0 },
        { 'Código': '101010301', 'Cuenta': 'Banco del Pichincha', 'Tipo': 'activo', 'Naturaleza': 'deudora', 'Saldo Débito': 0, 'Saldo Crédito': 0 },
        { 'Código': '101010302', 'Cuenta': 'Banco del Austro', 'Tipo': 'activo', 'Naturaleza': 'deudora', 'Saldo Débito': 0, 'Saldo Crédito': 0 },
        { 'Código': '101010303', 'Cuenta': 'Banco Produbanco', 'Tipo': 'activo', 'Naturaleza': 'deudora', 'Saldo Débito': 0, 'Saldo Crédito': 0 },
        { 'Código': '2', 'Cuenta': 'Pasivo', 'Tipo': 'pasivo', 'Naturaleza': 'acreedora', 'Saldo Débito': 0, 'Saldo Crédito': 0 },
        { 'Código': '201', 'Cuenta': 'Pasivo corriente', 'Tipo': 'pasivo', 'Naturaleza': 'acreedora', 'Saldo Débito': 0, 'Saldo Crédito': 0 },
        { 'Código': '20101', 'Cuenta': 'CUENTAS POR PAGAR', 'Tipo': 'pasivo', 'Naturaleza': 'acreedora', 'Saldo Débito': 0, 'Saldo Crédito': 0 },
        { 'Código': '20102', 'Cuenta': 'IMPUESTOS POR PAGAR', 'Tipo': 'pasivo', 'Naturaleza': 'acreedora', 'Saldo Débito': 0, 'Saldo Crédito': 0 },
        { 'Código': '3', 'Cuenta': 'Patrimonio', 'Tipo': 'patrimonio', 'Naturaleza': 'acreedora', 'Saldo Débito': 0, 'Saldo Crédito': 0 },
        { 'Código': '301', 'Cuenta': 'CAPITAL SOCIAL', 'Tipo': 'patrimonio', 'Naturaleza': 'acreedora', 'Saldo Débito': 0, 'Saldo Crédito': 0 },
        { 'Código': '302', 'Cuenta': 'RESERVAS', 'Tipo': 'patrimonio', 'Naturaleza': 'acreedora', 'Saldo Débito': 0, 'Saldo Crédito': 0 },
        { 'Código': '4', 'Cuenta': 'Ingresos', 'Tipo': 'ingresos', 'Naturaleza': 'acreedora', 'Saldo Débito': 0, 'Saldo Crédito': 0 },
        { 'Código': '401', 'Cuenta': 'VENTAS', 'Tipo': 'ingresos', 'Naturaleza': 'acreedora', 'Saldo Débito': 0, 'Saldo Crédito': 0 },
        { 'Código': '5', 'Cuenta': 'Gastos', 'Tipo': 'gastos', 'Naturaleza': 'deudora', 'Saldo Débito': 0, 'Saldo Crédito': 0 },
        { 'Código': '501', 'Cuenta': 'GASTOS DE VENTAS', 'Tipo': 'gastos', 'Naturaleza': 'deudora', 'Saldo Débito': 0, 'Saldo Crédito': 0 },
        { 'Código': '6', 'Cuenta': 'Costos', 'Tipo': 'costos', 'Naturaleza': 'deudora', 'Saldo Débito': 0, 'Saldo Crédito': 0 },
        { 'Código': '601', 'Cuenta': 'COSTO DE VENTAS', 'Tipo': 'costos', 'Naturaleza': 'deudora', 'Saldo Débito': 0, 'Saldo Crédito': 0 }
      ]

      const ws = XLSX.utils.json_to_sheet(templateData)
      const wb = XLSX.utils.book_new()
      XLSX.utils.book_append_sheet(wb, ws, 'Plan de Cuentas')

      // Crear hoja de instrucciones
      const instructionsData = [
        ['INSTRUCCIONES PARA USAR ESTA PLANTILLA SIMPLIFICADA'],
        [''],
        ['1. Complete los saldos iniciales en las columnas "Saldo Débito" y "Saldo Crédito"'],
        ['2. Los tipos de cuenta válidos son: activo, pasivo, patrimonio, ingresos, gastos, costos'],
        ['3. Las naturalezas válidas son: deudora, acreedora'],
        ['4. Solo complete los saldos en las cuentas que tengan movimientos iniciales'],
        ['5. El total de débitos debe ser igual al total de créditos'],
        ['6. Guarde el archivo y úselo para importar en el sistema'],
        [''],
        ['ESTRUCTURA Y JERARQUÍA (automática):'],
        ['- El sistema derivará automáticamente el Código Padre y el Nivel a partir del Código'],
        ['- No es necesario incluir columnas de Código Padre/Nivel/Padre-Hija'],
        ['- La jerarquía se calcula basándose en la longitud del código'],
        ['- Ejemplo: código "101" será nivel 2, padre "1"; código "10101" será nivel 3, padre "101"'],
        [''],
        ['EJEMPLO DE ESTRUCTURA SIMPLIFICADA:'],
        ['Código', 'Cuenta', 'Tipo', 'Naturaleza', 'Saldo Débito', 'Saldo Crédito'],
        ['1', 'Activo', 'activo', 'deudora', '0.00', '0.00'],
        ['101', 'Activo corriente', 'activo', 'deudora', '0.00', '0.00'],
        ['10101', 'Efectivo', 'activo', 'deudora', '0.00', '0.00'],
        ['1010101', 'CAJA 1', 'activo', 'deudora', '5000.00', '0.00'],
        ['1010102', 'CAJA 2', 'activo', 'deudora', '3000.00', '0.00'],
        [''],
        ['NOTAS IMPORTANTES:'],
        ['- No modifique los códigos de cuenta existentes'],
        ['- No modifique los nombres de las cuentas existentes'],
        ['- Solo modifique los saldos iniciales'],
        ['- Los saldos deben estar en formato numérico (ej: 1000.50)'],
        ['- Use punto como separador decimal'],
        ['- Para crear nuevas cuentas, use códigos que sigan la jerarquía numérica'],
        ['- El sistema calculará automáticamente la relación padre-hijo']
      ]

      const instructionsWs = XLSX.utils.aoa_to_sheet(instructionsData)
      XLSX.utils.book_append_sheet(wb, instructionsWs, 'Instrucciones')

      const fileName = `plantilla_plan_cuentas_${company.value?.name || 'empresa'}_${new Date().toISOString().split('T')[0]}.xlsx`
      XLSX.writeFile(wb, fileName)

      alerts.success('Éxito', 'Plantilla Excel generada exitosamente')
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

          alerts.success('Éxito', `Se encontraron ${importPreview.value.length} registros válidos`)
        } catch (error) {
          console.error('Error parsing Excel:', error)
          alerts.error('Error', 'Error al procesar archivo Excel')
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

        alerts.success('Éxito', response.data.message)
        if (response.data.errors && response.data.errors.length > 0) {
          console.warn('Errores en importación:', response.data.errors)
          alerts.warning('Advertencia', `${response.data.errors.length} errores encontrados`)
        }

        // Notificar cambio en el store para sincronizar con otras vistas
        companyStore.notifyAccountsChanged()

        showImportModal.value = false
        importPreview.value = []
        uploadedFile.value = null
        await loadAccounts()
        clearFilters()
        currentPage.value = 1
        await nextTick()
      } catch (error) {
        console.error('Error importing balances:', error)
        alerts.error('Error', 'Error al importar saldos')
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

    // Account Modal methods
    const closeCreateAccountModal = () => {
      showCreateAccountModal.value = false
      editingAccount.value = null
    }

    const editAccount = (account) => {
      editingAccount.value = account
      showCreateAccountModal.value = true
    }

    const deleteAccount = async (account) => {
      const confirmed = await alerts.confirm({
        title: '¿Eliminar cuenta?',
        text: `¿Estás seguro de que deseas eliminar la cuenta "${account.name}" (${account.code})? Esta acción no se puede deshacer.`,
        icon: 'warning',
        confirmButtonText: 'Eliminar',
        confirmButtonColor: '#dc3545'
      })

      if (confirmed) {
        try {
          await api.delete(`/accounts/${account.id}`, {
            params: { company_id: company.value.id }
          })
          
          alerts.success('Éxito', 'Cuenta eliminada correctamente')
          
          // Notificar cambio en el store
          companyStore.notifyAccountsChanged()
          
          // Recargar la lista de cuentas
          await loadAccounts()
        } catch (error) {
          console.error('Error deleting account:', error)
          alerts.error('Error', 'Error al eliminar la cuenta')
        }
      }
    }

    const closeAllModals = () => {
      showImportModal.value = false
      showCreateAccountModal.value = false
      showExportMenu.value = false
      editingAccount.value = null
    }

    const handleSaveAccount = async (accountData) => {
      try {
        if (editingAccount.value) {
          // Actualizar cuenta existente
          await api.put(`/accounts/${editingAccount.value.id}`, accountData, {
            params: { company_id: company.value.id }
          })
        } else {
          // Crear nueva cuenta
          const response = await api.post('/accounts', accountData, {
            params: { company_id: company.value.id }
          })
          
          // Marcar la nueva cuenta como cambiada para que aparezca en la lista de cambios
          const newAccountId = response.data.id
          changedAccounts.value.add(newAccountId)
        }
        
        // Notificar cambio en el store para sincronizar con otras vistas
        companyStore.notifyAccountsChanged()
        
        // Recargar cuentas para mostrar los cambios
        await loadAccounts()
        return true
      } catch (error) {
        console.error('Error saving account:', error)
        if (error.response?.data?.detail) {
          throw new Error(error.response.data.detail)
        } else {
          throw new Error('Error al guardar la cuenta')
        }
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
      document.addEventListener('click', handleClickOutside)
    })

    onBeforeUnmount(() => {
      document.removeEventListener('click', handleClickOutside)
    })

    return {
      loading,
      calculatingBalances,
      importing,
      accounts: accounts,
      filteredAccounts,
      paginatedAccounts: paginatedAccounts,
      changedAccounts,
      showImportModal,
      showCreateAccountModal,
      editingAccount,
      importPreview,
      parentAccounts,
      searchTerm,
      filterType,
      showOnlyWithBalances,
      currentPage,
      tableKey,
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
      editAccount,
      deleteAccount,
      handleSaveAccount,
      showExportMenu,
      exportMenuRef,
      showClearMenu,
      clearMenuRef,
      clearing,
      hasAnyLoadedBalances,
      hasLoadedBalancesVisible,
      toggleExportMenu,
      onExportTemplate,
      onExportLoaded,
      toggleClearMenu,
      clearBalancesVisible,
      clearBalancesAll,
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

.export-menu {
  position: absolute;
  top: 100%;
  left: 0;
  z-index: 1050;
  background: #fff;
  border: 1px solid #dee2e6;
  border-radius: 0.25rem;
  min-width: 240px;
  margin-top: 4px;
}

.export-menu .dropdown-item {
  width: 100%;
  text-align: left;
  padding: 0.5rem 0.75rem;
  background: transparent;
  border: none;
}

.export-menu .dropdown-item:hover {
  background: #f8f9fa;
}
</style>
