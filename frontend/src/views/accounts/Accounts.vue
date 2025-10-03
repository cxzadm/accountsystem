<template>
  <div class="accounts-page">
    <!-- Page Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h1 class="h3 mb-0">Plan de Cuentas</h1>
        <p class="text-muted">Administra el plan de cuentas contables</p>
      </div>
      <div>
        <button class="btn btn-primary me-2" @click="showCreateAccountModal = true">
          <i class="fas fa-plus me-2"></i>
          Nueva Cuenta
        </button>
        
      </div>
    </div>

    <!-- Filters -->
    <div class="card mb-3">
      <div class="card-body py-2">
        <div class="row g-2">
          <div class="col-md-3">
            <label class="form-label small">Búsqueda Inteligente</label>
            <div class="input-group">
              <input
                type="text"
                class="form-control form-control-sm"
                v-model="filters.search"
                placeholder="Código, nombre, descripción, saldo..."
                @input="debouncedSearch"
                list="searchSuggestions"
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
                <li><h6 class="dropdown-header">Búsquedas Rápidas</h6></li>
                <li><a class="dropdown-item" href="#" @click.prevent="applyQuickSearch('tipo:activo')">
                  <i class="fas fa-building me-2 text-primary"></i>Cuentas de Activo
                </a></li>
                <li><a class="dropdown-item" href="#" @click.prevent="applyQuickSearch('tipo:pasivo')">
                  <i class="fas fa-credit-card me-2 text-warning"></i>Cuentas de Pasivo
                </a></li>
                <li><a class="dropdown-item" href="#" @click.prevent="applyQuickSearch('tipo:patrimonio')">
                  <i class="fas fa-chart-line me-2 text-success"></i>Cuentas de Patrimonio
                </a></li>
                <li><a class="dropdown-item" href="#" @click.prevent="applyQuickSearch('tipo:ingresos')">
                  <i class="fas fa-arrow-up me-2 text-info"></i>Cuentas de Ingresos
                </a></li>
                <li><a class="dropdown-item" href="#" @click.prevent="applyQuickSearch('tipo:gastos')">
                  <i class="fas fa-arrow-down me-2 text-danger"></i>Cuentas de Gastos
                </a></li>
                <li><hr class="dropdown-divider"></li>
                <li><a class="dropdown-item" href="#" @click.prevent="applyQuickSearch('nivel:1')">
                  <i class="fas fa-layer-group me-2 text-secondary"></i>Cuentas de Nivel 1
                </a></li>
                <li><a class="dropdown-item" href="#" @click.prevent="applyQuickSearch('nivel:2')">
                  <i class="fas fa-layer-group me-2 text-secondary"></i>Cuentas de Nivel 2
                </a></li>
                <li><a class="dropdown-item" href="#" @click.prevent="applyQuickSearch('nivel:3')">
                  <i class="fas fa-layer-group me-2 text-secondary"></i>Cuentas de Nivel 3
                </a></li>
                <li><hr class="dropdown-divider"></li>
                <li><a class="dropdown-item" href="#" @click.prevent="applyQuickSearch('naturaleza:deudora')">
                  <i class="fas fa-hand-holding-usd me-2 text-primary"></i>Cuentas Deudoras
                </a></li>
                <li><a class="dropdown-item" href="#" @click.prevent="applyQuickSearch('naturaleza:acreedora')">
                  <i class="fas fa-hand-holding-usd me-2 text-success"></i>Cuentas Acreedoras
                </a></li>
                <li><hr class="dropdown-divider"></li>
                <li><a class="dropdown-item" href="#" @click.prevent="applyQuickSearch('saldo:>0')">
                  <i class="fas fa-plus-circle me-2 text-success"></i>Con Saldo Positivo
                </a></li>
                <li><a class="dropdown-item" href="#" @click.prevent="applyQuickSearch('saldo:<0')">
                  <i class="fas fa-minus-circle me-2 text-danger"></i>Con Saldo Negativo
                </a></li>
                <li><a class="dropdown-item" href="#" @click.prevent="applyQuickSearch('saldo:=0')">
                  <i class="fas fa-equals me-2 text-muted"></i>Con Saldo Cero
                </a></li>
                <li><hr class="dropdown-divider"></li>
                <li><a class="dropdown-item" href="#" @click.prevent="applyQuickSearch('estado:activo')">
                  <i class="fas fa-check-circle me-2 text-success"></i>Cuentas Activas
                </a></li>
                <li><a class="dropdown-item" href="#" @click.prevent="applyQuickSearch('estado:inactivo')">
                  <i class="fas fa-times-circle me-2 text-secondary"></i>Cuentas Inactivas
                </a></li>
                <li><hr class="dropdown-divider"></li>
                <li><h6 class="dropdown-header">Búsqueda por Documentos</h6></li>
                <li><a class="dropdown-item" href="#" @click.prevent="applyQuickSearch('doc:FACT')">
                  <i class="fas fa-file-invoice me-2 text-primary"></i>Facturas
                </a></li>
                <li><a class="dropdown-item" href="#" @click.prevent="applyQuickSearch('doc:REC')">
                  <i class="fas fa-receipt me-2 text-success"></i>Recibos
                </a></li>
                <li><a class="dropdown-item" href="#" @click.prevent="applyQuickSearch('doc:NC')">
                  <i class="fas fa-file-invoice-dollar me-2 text-warning"></i>Notas de Crédito
                </a></li>
                <li><a class="dropdown-item" href="#" @click.prevent="applyQuickSearch('doc:ND')">
                  <i class="fas fa-file-invoice-dollar me-2 text-danger"></i>Notas de Débito
                </a></li>
                <li><a class="dropdown-item" href="#" @click.prevent="applyQuickSearch('doc:COMP')">
                  <i class="fas fa-shopping-cart me-2 text-info"></i>Compras
                </a></li>
                <li><a class="dropdown-item" href="#" @click.prevent="applyQuickSearch('doc:GAST')">
                  <i class="fas fa-credit-card me-2 text-secondary"></i>Gastos
                </a></li>
                <li><hr class="dropdown-divider"></li>
                <li><a class="dropdown-item" href="#" @click.prevent="applyQuickSearch('ref:001')">
                  <i class="fas fa-hashtag me-2 text-muted"></i>Con Referencia 001
                </a></li>
                <li><a class="dropdown-item" href="#" @click.prevent="applyQuickSearch('ref:TRANS')">
                  <i class="fas fa-exchange-alt me-2 text-muted"></i>Con Referencia TRANS
                </a></li>
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
                <strong>Ejemplos:</strong><br>
                • <code>1.1</code> - Buscar por código<br>
                • <code>caja</code> - Buscar por nombre<br>
                • <code>desc:banco</code> - Buscar en descripción<br>
                • <code>saldo:>1000</code> - Saldo mayor a 1000<br>
                • <code>tipo:activo</code> - Filtrar por tipo<br>
                • <code>nivel:1</code> - Filtrar por nivel<br>
                • <code>doc:FACT</code> - Buscar por tipo de documento<br>
                • <code>ref:001</code> - Buscar por referencia
              </small>
            </div>
          </div>
          <div class="col-md-2">
            <label class="form-label small">Fecha Inicio</label>
            <input type="date" class="form-control form-control-sm" v-model="filters.start_date" @change="loadAccounts" />
          </div>
          <div class="col-md-2">
            <label class="form-label small">Fecha Fin</label>
            <input type="date" class="form-control form-control-sm" v-model="filters.end_date" @change="loadAccounts" />
          </div>
          <div class="col-md-2">
            <label class="form-label small">Tipo</label>
            <select class="form-select form-select-sm" v-model="filters.account_type" @change="loadAccounts">
              <option value="">Todos</option>
              <option value="activo">Activo</option>
              <option value="pasivo">Pasivo</option>
              <option value="patrimonio">Patrimonio</option>
              <option value="ingresos">Ingresos</option>
              <option value="gastos">Gastos</option>
              <option value="costos">Costos</option>
            </select>
          </div>
          <div class="col-md-2">
            <label class="form-label small">Estado</label>
            <select class="form-select form-select-sm" v-model="filters.is_active" @change="loadAccounts">
              <option value="">Todos</option>
              <option value="true">Activo</option>
              <option value="false">Inactivo</option>
            </select>
          </div>
          <div class="col-md-1 d-flex align-items-end">
            <button class="btn btn-outline-secondary btn-sm w-100" @click="clearFilters">
              <i class="fas fa-times me-1"></i>Limpiar
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Accounts Table -->
    <div class="card">
      <div class="card-body p-2">
        <div class="table-responsive">
          <table class="table table-hover table-sm mb-0">
            <thead class="table-light">
              <tr>
                <th>Código</th>
                <th>Nombre</th>
                <th>Tipo</th>
                <th>Naturaleza</th>
                <th>P/H</th>
                <th>Nivel</th>
                <th>Saldo (rango)</th>
                <th>Estado</th>
                <th style="width: 80px;">Acciones</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="loading">
                <td colspan="9" class="text-center py-2">
                  <div class="spinner-border spinner-border-sm text-primary" role="status">
                    <span class="visually-hidden">Cargando...</span>
                  </div>
                </td>
              </tr>
              <tr v-else-if="accounts.length === 0">
                <td colspan="9" class="text-center py-2 text-muted">
                  No se encontraron cuentas
                </td>
              </tr>
              <tr v-else v-for="account in accounts" :key="account.id" :class="getAccountRowClass(account)" class="align-middle">
                <td>
                  <code class="small" :style="{ paddingLeft: (account.level - 1) * 15 + 'px' }">
                    {{ account.code }}
                  </code>
                </td>
                <td :style="{ paddingLeft: (account.level - 1) * 15 + 'px' }">
                  <div class="small">
                    <strong>{{ account.name }}</strong>
                    <div v-if="account.description" class="text-muted" style="font-size: 0.7rem;">
                      {{ account.description }}
                    </div>
                  </div>
                </td>
                <td>
                  <span :class="`badge badge-sm bg-${getAccountTypeColor(account.account_type)}`">
                    {{ account.account_type.charAt(0).toUpperCase() }}
                  </span>
                </td>
                <td>
                  <span :class="`badge badge-sm ${account.nature === 'deudora' ? 'bg-primary' : 'bg-success'}`">
                    {{ account.nature.charAt(0).toUpperCase() }}
                  </span>
                </td>
                <td class="text-center">
                  <span class="badge badge-sm" :class="getRelationshipClass(account)">
                    {{ getRelationshipType(account) }}
                  </span>
                </td>
                <td>
                  <span class="badge badge-sm bg-secondary">{{ account.level }}</span>
                </td>
                <td class="text-end small">
                  <span :class="balanceClass(getAccountBalance(account))">
                    {{ formatCurrency(getAccountBalance(account)) }}
                  </span>
                </td>
                <td>
                  <span :class="`badge badge-sm bg-${account.is_active ? 'success' : 'secondary'}`">
                    {{ account.is_active ? 'A' : 'I' }}
                  </span>
                </td>
                <td>
                  <div class="btn-group" role="group">
                    <button
                      class="btn btn-xs btn-outline-info"
                      @click="viewAccountMovements(account)"
                      title="Ver Movimientos"
                    >
                      <i class="fas fa-history"></i>
                    </button>
                    <button
                      class="btn btn-xs btn-outline-primary"
                      @click="editAccount(account)"
                      title="Editar"
                      :disabled="!account.is_editable"
                    >
                      <i class="fas fa-edit"></i>
                    </button>
                    <button
                      :class="`btn btn-xs ${account.is_active ? 'btn-outline-warning' : 'btn-outline-success'}`"
                      @click="toggleAccountStatus(account)"
                      :title="account.is_active ? 'Desactivar' : 'Activar'"
                      :disabled="!account.is_editable"
                    >
                      <i :class="account.is_active ? 'fas fa-pause' : 'fas fa-play'"></i>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Pagination -->
        <nav v-if="totalPages > 1" class="mt-2">
          <ul class="pagination pagination-sm justify-content-center">
            <li class="page-item" :class="{ disabled: currentPage === 1 }">
              <button class="page-link" @click="changePage(currentPage - 1)">
                Anterior
              </button>
            </li>
            <li
              v-for="page in visiblePages"
              :key="page"
              class="page-item"
              :class="{ active: page === currentPage }"
            >
              <button class="page-link" @click="changePage(page)">
                {{ page }}
              </button>
            </li>
            <li class="page-item" :class="{ disabled: currentPage === totalPages }">
              <button class="page-link" @click="changePage(currentPage + 1)">
                Siguiente
              </button>
            </li>
          </ul>
        </nav>
      </div>
    </div>

    <!-- Account Form Modal -->
    <AccountFormModal
      :show="showCreateAccountModal"
      :account="editingAccount"
      :company-id="currentCompany?.id"
      :all-accounts="accounts"
      :on-save="handleSaveAccount"
      @close="closeCreateAccountModal"
    />
  </div>

  <!-- Datalist para sugerencias de búsqueda -->
  <datalist id="searchSuggestions">
    <option value="tipo:activo">Cuentas de Activo</option>
    <option value="tipo:pasivo">Cuentas de Pasivo</option>
    <option value="tipo:patrimonio">Cuentas de Patrimonio</option>
    <option value="tipo:ingresos">Cuentas de Ingresos</option>
    <option value="tipo:gastos">Cuentas de Gastos</option>
    <option value="nivel:1">Cuentas de Nivel 1</option>
    <option value="nivel:2">Cuentas de Nivel 2</option>
    <option value="nivel:3">Cuentas de Nivel 3</option>
    <option value="naturaleza:deudora">Cuentas Deudoras</option>
    <option value="naturaleza:acreedora">Cuentas Acreedoras</option>
    <option value="saldo:>0">Con Saldo Positivo</option>
    <option value="saldo:<0">Con Saldo Negativo</option>
    <option value="saldo:=0">Con Saldo Cero</option>
    <option value="estado:activo">Cuentas Activas</option>
    <option value="estado:inactivo">Cuentas Inactivas</option>
    <option value="doc:FACT">Facturas</option>
    <option value="doc:REC">Recibos</option>
    <option value="doc:NC">Notas de Crédito</option>
    <option value="doc:ND">Notas de Débito</option>
    <option value="ref:001">Con Referencia 001</option>
    <option value="ref:TRANS">Con Referencia TRANS</option>
    <option value="num:001-001">Número de Documento</option>
  </datalist>
</template>

<script>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { alerts } from '@/services/alerts'
import { useCompanyStore } from '@/stores/company'
import { useBreadcrumb } from '@/composables/useBreadcrumb'
import api from '@/services/api'
import { debounce } from 'lodash-es'
import AccountFormModal from '@/components/AccountFormModal.vue'

export default {
  name: 'Accounts',
  components: {
    AccountFormModal
  },
  setup() {
    const router = useRouter()
    const companyStore = useCompanyStore()
    const { addBreadcrumb, clearBreadcrumbs } = useBreadcrumb()

    // State
    const accounts = ref([])
    const rangeBalances = ref({}) // Map accountId -> net_balance for date range
    const loading = ref(false)
    const currentPage = ref(1)
    const totalPages = ref(1)
    const pageSize = 1000  // Mostrar todas las cuentas

    const filters = reactive({
      search: '',
      account_type: '',
      is_active: '',
      relationship: '',
      start_date: '',
      end_date: ''
    })

    // Modal state
    const showCreateAccountModal = ref(false)
    const editingAccount = ref(null)
    
    const showSearchHelp = ref(false)

    // Computed
    const visiblePages = computed(() => {
      const pages = []
      const start = Math.max(1, currentPage.value - 2)
      const end = Math.min(totalPages.value, start + 4)
      
      for (let i = start; i <= end; i++) {
        pages.push(i)
      }
      return pages
    })

    const currentCompany = computed(() => companyStore.getCurrentCompany())

    const parentAccounts = computed(() => {
      return accounts.value.filter(acc => acc.is_active && !acc.parent_code)
    })

    // Methods
    const loadAccounts = async () => {
      if (!currentCompany.value) {
        alerts.error('Error', 'Selecciona una empresa primero')
        return
      }

      loading.value = true
      try {
        const params = {
          company_id: currentCompany.value.id,
          skip: (currentPage.value - 1) * pageSize,
          limit: pageSize
        }

        // Solo agregar filtros que no estén vacíos
        if (filters.search && filters.search.trim()) {
          const searchQuery = filters.search.trim()
          
          // Parsear búsqueda inteligente
          const parsedSearch = parseIntelligentSearch(searchQuery)
          Object.assign(params, parsedSearch)
        }
        if (filters.account_type && filters.account_type.trim()) {
          params.account_type = filters.account_type
        }
        if (filters.is_active !== '' && filters.is_active !== null) {
          params.is_active = filters.is_active === 'true'
        }
        if (filters.relationship && filters.relationship.trim()) {
          params.relationship = filters.relationship
        }
        if (filters.start_date) params.start_date = filters.start_date
        if (filters.end_date) params.end_date = filters.end_date

        const response = await api.get('/accounts', { params })
        accounts.value = response.data
        totalPages.value = Math.ceil(response.data.length / pageSize)
        
        // Si hay menos de 1000 cuentas, no mostrar paginación
        if (response.data.length <= pageSize) {
          totalPages.value = 1
        }

        // Cargar balances por rango si hay fechas (excluir movimientos posteriores correctamente)
        rangeBalances.value = {}
        if (filters.start_date || filters.end_date) {
          try {
            const balParams = {}
            if (filters.start_date) balParams.start_date = filters.start_date
            if (filters.end_date) balParams.end_date = filters.end_date
            const balRes = await api.get(`/accounts/${currentCompany.value.id}/balance`, { params: balParams })
            const map = {}
            for (const b of balRes.data || []) {
              const acc = b.account || {}
              // b.net_balance ya es saldo inicial + movimientos dentro del rango, según backend
              if (acc.id) map[acc.id] = Number(b.net_balance || 0)
            }
            rangeBalances.value = map
          } catch (e) {
            console.error('Error loading range balances:', e)
          }
        }
      } catch (error) {
        console.error('Error loading accounts:', error)
        alerts.error('Error', 'Error al cargar cuentas')
      } finally {
        loading.value = false
      }
    }

    const debouncedSearch = debounce(() => {
      currentPage.value = 1
      loadAccounts()
    }, 500)

    // Búsqueda inteligente
    const parseIntelligentSearch = (query) => {
      const params = {}
      
      // Detectar patrones específicos
      const patterns = {
        // Búsqueda por descripción: desc:texto
        desc: /^desc:\s*(.+)$/i,
        // Búsqueda por saldo: saldo:>1000, saldo:<500, saldo:1000-2000
        saldo: /^saldo:\s*([><=]+)\s*(\d+(?:\.\d+)?)$/i,
        // Búsqueda por tipo: tipo:activo
        tipo: /^tipo:\s*(.+)$/i,
        // Búsqueda por nivel: nivel:1
        nivel: /^nivel:\s*(\d+)$/i,
        // Búsqueda por naturaleza: naturaleza:deudora
        naturaleza: /^naturaleza:\s*(.+)$/i,
        // Búsqueda por código padre: padre:1.1
        padre: /^padre:\s*(.+)$/i,
        // Búsqueda por estado: estado:activo
        estado: /^estado:\s*(.+)$/i,
        // Búsqueda por tipo de documento: doc:FACT
        doc: /^doc:\s*(.+)$/i,
        // Búsqueda por referencia: ref:001
        ref: /^ref:\s*(.+)$/i,
        // Búsqueda por número de documento: num:001-001
        num: /^num:\s*(.+)$/i
      }
      
      // Verificar cada patrón
      for (const [key, pattern] of Object.entries(patterns)) {
        const match = query.match(pattern)
        if (match) {
          switch (key) {
            case 'desc':
              params.description = match[1]
              break
            case 'saldo':
              const operator = match[1]
              const value = parseFloat(match[2])
              if (operator.includes('>')) {
                params.min_balance = value
              } else if (operator.includes('<')) {
                params.max_balance = value
              } else if (operator.includes('=')) {
                params.exact_balance = value
              }
              break
            case 'tipo':
              params.account_type = match[1].toLowerCase()
              break
            case 'nivel':
              params.level = parseInt(match[1])
              break
            case 'naturaleza':
              params.nature = match[1].toLowerCase()
              break
            case 'padre':
              params.parent_code = match[1]
              break
            case 'estado':
              params.is_active = match[1].toLowerCase() === 'activo'
              break
            case 'doc':
              params.document_type_code = match[1].toUpperCase()
              break
            case 'ref':
              params.reference = match[1]
              break
            case 'num':
              params.entry_number = match[1]
              break
          }
          return params
        }
      }
      
      // Si no coincide con ningún patrón, búsqueda general
      params.search = query
      return params
    }

    const applyQuickSearch = (searchTerm) => {
      filters.search = searchTerm
      currentPage.value = 1
      loadAccounts()
    }

    const changePage = (page) => {
      if (page >= 1 && page <= totalPages.value) {
        currentPage.value = page
        loadAccounts()
      }
    }

    const clearFilters = () => {
      filters.search = ''
      filters.account_type = ''
      filters.is_active = ''
      filters.relationship = ''
      filters.start_date = ''
      filters.end_date = ''
      currentPage.value = 1
      loadAccounts()
    }

    const editAccount = (account) => {
      editingAccount.value = account
      showCreateAccountModal.value = true
      
      // Agregar breadcrumb dinámico para la cuenta que se está editando
      addBreadcrumb({
        label: `Editando: ${account.code} - ${account.name}`,
        path: null,
        icon: 'fas fa-edit',
        active: true
      })
    }

    const viewAccountMovements = (account) => {
      // Navegar al Mayor General y abrir el mayor de esta cuenta específica
      router.push({
        path: '/ledger',
        query: { 
          account: account.code, // Usar código de cuenta para consistencia
          start_date: filters.start_date || '',
          end_date: filters.end_date || ''
        }
      })
      
      alerts.info('Redirigiendo', `Mayor General para la cuenta ${account.code}`)
    }

    const toggleAccountStatus = async (account) => {
      const action = account.is_active ? 'desactivar' : 'activar'
      const ok = await alerts.confirm({
        title: `¿${action.charAt(0).toUpperCase() + action.slice(1)} cuenta ${account.code}?`,
        text: `${account.name}.`,
        icon: 'question',
        confirmButtonText: action.charAt(0).toUpperCase() + action.slice(1)
      })
      if (ok) {
        try {
          const response = await api.patch(`/accounts/${account.id}/toggle-status`)
          alerts.success('Éxito', response.data.message)
          
          // Notificar cambio en el store
          companyStore.notifyAccountsChanged()
          
          loadAccounts()
        } catch (error) {
          console.error('Error toggling account status:', error)
          alerts.error('Error', `Error al ${action} cuenta`)
        }
      }
    }

    

    const getAccountTypeColor = (type) => {
      const colors = {
        activo: 'primary',
        pasivo: 'warning',
        patrimonio: 'info',
        ingresos: 'success',
        gastos: 'danger',
        costos: 'secondary'
      }
      return colors[type] || 'secondary'
    }

    const getAccountBalance = (account) => {
      // Si hay balances por rango, usar ese valor para respetar Fecha Inicio/Fin
      if (rangeBalances.value && rangeBalances.value[account.id] !== undefined) {
        return Number(rangeBalances.value[account.id])
      }
      const initialDebit = Number(account.initial_debit_balance || 0)
      const initialCredit = Number(account.initial_credit_balance || 0)
      const initialNet = initialDebit - initialCredit
      
      const movDebit = Number(account.current_debit_balance || 0)
      const movCredit = Number(account.current_credit_balance || 0)
      const movNet = movDebit - movCredit
      
      return initialNet + movNet
    }

    const balanceClass = (amount) => {
      if (amount === 0) return 'text-muted'
      return amount > 0 ? 'text-danger fw-bold' : 'text-success fw-bold'
    }

    const formatCurrency = (amount) => new Intl.NumberFormat('es-EC', { style: 'currency', currency: 'USD' }).format(amount)

    // Hierarchical methods
    const getRelationshipType = (account) => {
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

    // Modal methods
    const closeCreateAccountModal = () => {
      showCreateAccountModal.value = false
      editingAccount.value = null
    }

    const handleSaveAccount = async (accountData) => {
      try {
        if (editingAccount.value) {
          // Actualizar cuenta existente
          await api.put(`/accounts/${editingAccount.value.id}`, accountData, {
            params: { company_id: currentCompany.value.id }
          })
        } else {
          // Crear nueva cuenta
          await api.post('/accounts', accountData, {
            params: { company_id: currentCompany.value.id }
          })
        }
        
        // Notificar cambio en el store
        companyStore.notifyAccountsChanged()
        
        await loadAccounts()
        return true
      } catch (error) {
        console.error('Error saving account:', error)
        throw error
      }
    }

    // Watchers
    watch(() => companyStore.accountsChanged, () => {
      // Recargar cuentas cuando hay cambios desde otras vistas
      console.log('🔄 Cambios detectados en cuentas, recargando Plan de Cuentas...')
      loadAccounts()
    })

    // Lifecycle
    onMounted(() => {
      loadAccounts()
      // Limpiar breadcrumbs dinámicos al cargar la vista
      clearBreadcrumbs()
    })

    return {
      accounts,
      loading,
      currentPage,
      totalPages,
      visiblePages,
      filters,
      currentCompany,
      rangeBalances,
      showCreateAccountModal,
      editingAccount,
      
      showSearchHelp,
      loadAccounts,
      debouncedSearch,
      changePage,
      applyQuickSearch,
      clearFilters,
      editAccount,
      viewAccountMovements,
      toggleAccountStatus,
      
      getAccountTypeColor,
      getAccountBalance,
      balanceClass,
      formatCurrency,
      getRelationshipType,
      getRelationshipClass,
      getAccountRowClass,
      closeCreateAccountModal,
      handleSaveAccount
    }
  }
}
</script>

<style scoped>
.table th {
  border-top: none;
  font-weight: 600;
  color: #5a5c69;
  font-size: 0.8rem;
  padding: 0.5rem 0.3rem;
}

.table td {
  padding: 0.4rem 0.3rem;
  font-size: 0.8rem;
}

.btn-group .btn {
  margin-right: 2px;
}

.btn-group .btn:last-child {
  margin-right: 0;
}

code {
  background-color: #f8f9fa;
  padding: 0.1rem 0.3rem;
  border-radius: 0.2rem;
  font-size: 0.7rem;
}

.badge {
  font-size: 0.65rem;
  padding: 0.25rem 0.4rem;
}

.badge-sm {
  font-size: 0.6rem;
  padding: 0.2rem 0.3rem;
}

.btn-xs {
  padding: 0.2rem 0.4rem;
  font-size: 0.7rem;
}

.btn-sm {
  padding: 0.3rem 0.6rem;
  font-size: 0.75rem;
}

.form-control-sm, .form-select-sm {
  padding: 0.25rem 0.5rem;
  font-size: 0.8rem;
}

.form-label.small {
  font-size: 0.75rem;
  margin-bottom: 0.2rem;
}

.table-responsive {
  font-size: 0.85rem;
}

.card-body.p-2 {
  padding: 0.75rem !important;
}

.card-body.py-2 {
  padding: 0.75rem !important;
}

.pagination-sm .page-link {
  padding: 0.25rem 0.5rem;
  font-size: 0.8rem;
}
</style>

