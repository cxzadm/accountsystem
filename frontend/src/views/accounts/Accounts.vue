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
        <button class="btn btn-warning me-2" @click="fixCompleteHierarchy" :disabled="fixingHierarchy">
          <i class="fas fa-sync-alt me-2"></i>
          <span v-if="fixingHierarchy">Corrigiendo...</span>
          <span v-else>Corregir Jerarquía Completa</span>
        </button>
        <router-link to="/accounts/new" class="btn btn-outline-primary">
          <i class="fas fa-edit me-2"></i>
          Editar Avanzado
        </router-link>
      </div>
    </div>

    <!-- Filters -->
    <div class="card mb-4">
      <div class="card-body">
        <div class="row">
          <div class="col-md-3">
            <label class="form-label">Buscar</label>
            <input
              type="text"
              class="form-control"
              v-model="filters.search"
              placeholder="Código o nombre de cuenta..."
              @input="debouncedSearch"
            />
          </div>
          <div class="col-md-3">
            <label class="form-label">Fecha Inicio</label>
            <input type="date" class="form-control" v-model="filters.start_date" @change="loadAccounts" />
          </div>
          <div class="col-md-3">
            <label class="form-label">Fecha Fin</label>
            <input type="date" class="form-control" v-model="filters.end_date" @change="loadAccounts" />
          </div>
          <div class="col-md-3">
            <label class="form-label">Tipo de Cuenta</label>
            <select class="form-select" v-model="filters.account_type" @change="loadAccounts">
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
            <label class="form-label">Estado</label>
            <select class="form-select" v-model="filters.is_active" @change="loadAccounts">
              <option value="">Todos</option>
              <option value="true">Activo</option>
              <option value="false">Inactivo</option>
            </select>
          </div>
          <div class="col-md-3">
            <label class="form-label">Relación</label>
            <select class="form-select" v-model="filters.relationship" @change="loadAccounts">
              <option value="">Todas</option>
              <option value="parent">Solo Padres</option>
              <option value="child">Solo Hijas</option>
            </select>
          </div>
          <div class="col-md-3 d-flex align-items-end">
            <button class="btn btn-outline-secondary w-100" @click="clearFilters">
              <i class="fas fa-times me-1"></i>
              Limpiar
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Accounts Table -->
    <div class="card">
      <div class="card-body">
        <div class="table-responsive">
          <table class="table table-hover">
            <thead>
              <tr>
                <th>Código</th>
                <th>Nombre</th>
                <th>Tipo</th>
                <th>Naturaleza</th>
                <th>Padre/Hija</th>
                <th>Nivel</th>
                <th>Saldo (rango)</th>
                <th>Estado</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="loading">
                <td colspan="9" class="text-center py-4">
                  <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Cargando...</span>
                  </div>
                </td>
              </tr>
              <tr v-else-if="accounts.length === 0">
                <td colspan="9" class="text-center py-4 text-muted">
                  No se encontraron cuentas
                </td>
              </tr>
              <tr v-else v-for="account in accounts" :key="account.id" :class="getAccountRowClass(account)">
                <td>
                  <code :style="{ paddingLeft: (account.level - 1) * 20 + 'px' }">
                    {{ account.code }}
                  </code>
                </td>
                <td :style="{ paddingLeft: (account.level - 1) * 20 + 'px' }">
                  <div>
                    <strong>{{ account.name }}</strong>
                    <div v-if="account.description" class="text-muted small">
                      {{ account.description }}
                    </div>
                    <div v-if="account.parent_code" class="text-muted small">
                      <i class="fas fa-level-up-alt me-1"></i>
                      Padre: {{ account.parent_code }}
                    </div>
                  </div>
                </td>
                <td>
                  <span :class="`badge bg-${getAccountTypeColor(account.account_type)}`">
                    {{ account.account_type }}
                  </span>
                </td>
                <td>
                  <span :class="`badge ${account.nature === 'deudora' ? 'bg-primary' : 'bg-success'}`">
                    {{ account.nature }}
                  </span>
                </td>
                <td class="text-center">
                  <span class="badge" :class="getRelationshipClass(account)">
                    {{ getRelationshipType(account) }}
                  </span>
                </td>
                <td>
                  <span class="badge bg-secondary">{{ account.level }}</span>
                </td>
                <td class="text-end">
                  <span :class="balanceClass(getAccountBalance(account))">
                    {{ formatCurrency(getAccountBalance(account)) }}
                  </span>
                </td>
                <td>
                  <span :class="`badge bg-${account.is_active ? 'success' : 'secondary'}`">
                    {{ account.is_active ? 'Activo' : 'Inactivo' }}
                  </span>
                </td>
                <td>
                  <div class="btn-group" role="group">
                    <button
                      class="btn btn-sm btn-outline-info"
                      @click="viewAccountMovements(account)"
                      title="Ver Movimientos"
                    >
                      <i class="fas fa-history"></i>
                    </button>
                    <button
                      class="btn btn-sm btn-outline-primary"
                      @click="editAccount(account)"
                      title="Editar"
                      :disabled="!account.is_editable"
                    >
                      <i class="fas fa-edit"></i>
                    </button>
                    <button
                      :class="`btn btn-sm ${account.is_active ? 'btn-outline-warning' : 'btn-outline-success'}`"
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
        <nav v-if="totalPages > 1" class="mt-4">
          <ul class="pagination justify-content-center">
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

    <!-- Create Account Modal -->
    <div class="modal fade" :class="{ show: showCreateAccountModal }" :style="{ display: showCreateAccountModal ? 'block' : 'none' }" tabindex="-1">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Nueva Cuenta Contable</h5>
            <button type="button" class="btn-close" @click="closeCreateAccountModal"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="createAccount">
              <div class="row">
                <div class="col-md-6">
                  <div class="mb-3">
                    <label for="code" class="form-label">Código *</label>
                    <input
                      type="text"
                      class="form-control"
                      id="code"
                      v-model="newAccount.code"
                      required
                      placeholder="Ej: 1010101"
                    />
                    <div class="form-text">Código único de la cuenta</div>
                  </div>
                </div>
                <div class="col-md-6">
                  <div class="mb-3">
                    <label for="name" class="form-label">Nombre *</label>
                    <input
                      type="text"
                      class="form-control"
                      id="name"
                      v-model="newAccount.name"
                      required
                      placeholder="Ej: CAJA 1"
                    />
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

              <div class="row">
                <div class="col-md-6">
                  <div class="mb-3">
                    <label for="accountTypeSelect" class="form-label">Tipo de Cuenta *</label>
                    <select class="form-select" id="accountTypeSelect" v-model="newAccount.account_type" required>
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
                    <label for="nature" class="form-label">Naturaleza *</label>
                    <select class="form-select" id="nature" v-model="newAccount.nature" required>
                      <option value="">Seleccionar naturaleza</option>
                      <option value="deudora">Deudora</option>
                      <option value="acreedora">Acreedora</option>
                    </select>
                  </div>
                </div>
              </div>

              <div class="mb-3">
                <label for="description" class="form-label">Descripción</label>
                <textarea
                  class="form-control"
                  id="description"
                  v-model="newAccount.description"
                  rows="3"
                  placeholder="Descripción opcional de la cuenta"
                ></textarea>
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="closeCreateAccountModal">
              Cancelar
            </button>
            <button type="button" class="btn btn-primary" @click="createAccount" :disabled="creating">
              <span v-if="creating" class="spinner-border spinner-border-sm me-2"></span>
              {{ creating ? 'Creando...' : 'Crear Cuenta' }}
            </button>
          </div>
        </div>
      </div>
    </div>
    <div v-if="showCreateAccountModal" class="modal-backdrop fade show"></div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'vue-toastification'
import { alerts } from '@/services/alerts'
import { useCompanyStore } from '@/stores/company'
import api from '@/services/api'
import { debounce } from 'lodash-es'

export default {
  name: 'Accounts',
  setup() {
    const router = useRouter()
    const toast = useToast()
    const companyStore = useCompanyStore()

    // State
    const accounts = ref([])
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
    const creating = ref(false)
    const fixingHierarchy = ref(false)
    const newAccount = reactive({
      code: '',
      name: '',
      account_type: '',
      nature: '',
      parent_code: '',
      level: 1,
      account_relationship_type: 'H',
      description: ''
    })
    const suggestedCode = ref('')

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
        toast.error('Selecciona una empresa primero')
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
          params.search = filters.search.trim()
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
      } catch (error) {
        console.error('Error loading accounts:', error)
        toast.error('Error al cargar cuentas')
      } finally {
        loading.value = false
      }
    }

    const debouncedSearch = debounce(() => {
      currentPage.value = 1
      loadAccounts()
    }, 500)

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
      router.push(`/accounts/${account.id}/edit`)
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
      
      toast.info(`Redirigiendo al Mayor General para ver la cuenta ${account.code}`)
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
          toast.success(response.data.message)
          loadAccounts()
        } catch (error) {
          console.error('Error toggling account status:', error)
          toast.error(`Error al ${action} cuenta`)
        }
      }
    }

    const fixCompleteHierarchy = async () => {
      const ok = await alerts.confirm({
        title: '¿Corregir jerarquía completa?',
        text: 'Esta acción recalculará automáticamente los saldos de TODAS las cuentas padre en toda la jerarquía.',
        icon: 'question',
        confirmButtonText: 'Corregir'
      })
      
      if (ok) {
        fixingHierarchy.value = true
        try {
          const response = await api.post('/accounts/fix-complete-hierarchy', {}, {
            params: { company_id: currentCompany.value.id }
          })
          
          toast.success(response.data.message)
          
          // Mostrar detalles de las correcciones
          if (response.data.corrections && response.data.corrections.length > 0) {
            console.log('Correcciones realizadas:', response.data.corrections)
            
            // Mostrar un resumen de las correcciones más importantes
            const importantCorrections = response.data.corrections.filter(c => 
              c.old_balance !== c.new_balance
            )
            
            if (importantCorrections.length > 0) {
              toast.info(`Se corrigieron ${importantCorrections.length} cuentas padre con saldos incorrectos`)
              
              // Mostrar detalles en consola
              importantCorrections.forEach(correction => {
                console.log(`✅ ${correction.parent_code} (${correction.parent_name}): ${correction.old_balance} → ${correction.new_balance}`)
              })
            } else {
              toast.success('Todas las cuentas padre ya tenían saldos correctos')
            }
          }
          
          // Recargar las cuentas para mostrar los cambios
          await loadAccounts()
          
        } catch (error) {
          console.error('Error fixing complete hierarchy:', error)
          toast.error('Error al corregir jerarquía completa')
        } finally {
          fixingHierarchy.value = false
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
      resetNewAccount()
    }

    const resetNewAccount = () => {
      newAccount.code = ''
      newAccount.name = ''
      newAccount.account_type = ''
      newAccount.nature = ''
      newAccount.parent_code = ''
      newAccount.level = 1
      newAccount.account_relationship_type = 'H'
      newAccount.description = ''
      suggestedCode.value = ''
    }

    const updateAccountLevel = () => {
      if (!newAccount.parent_code) {
        newAccount.level = 1
        return
      }
      const parentAccount = accounts.value.find(acc => acc.code === newAccount.parent_code)
      if (parentAccount) {
        newAccount.level = (parentAccount.level || 1) + 1
      } else {
        newAccount.level = Math.ceil(newAccount.parent_code.length / 2) + 1
      }
    }

    const generateSuggestedCode = () => {
      if (!newAccount.parent_code) {
        const typeCodes = {
          activo: '1',
          pasivo: '2',
          patrimonio: '3',
          ingresos: '4',
          gastos: '5',
          costos: '6'
        }
        suggestedCode.value = typeCodes[newAccount.account_type] || '1'
        return
      }
      
      const parentAccount = accounts.value.find(acc => acc.code === newAccount.parent_code)
      if (!parentAccount) {
        suggestedCode.value = newAccount.parent_code + '01'
        return
      }
      
      const children = accounts.value.filter(acc => 
        acc.parent_code === newAccount.parent_code && 
        acc.code.startsWith(newAccount.parent_code) &&
        acc.code !== newAccount.parent_code
      )
      
      let nextNumber = 1
      if (children.length > 0) {
        const numbers = children.map(child => {
          const suffix = child.code.substring(newAccount.parent_code.length)
          return parseInt(suffix) || 0
        }).filter(num => !isNaN(num))
        
        if (numbers.length > 0) {
          nextNumber = Math.max(...numbers) + 1
        }
      }
      
      suggestedCode.value = newAccount.parent_code + nextNumber.toString().padStart(2, '0')
    }

    const createAccount = async () => {
      if (!newAccount.code || !newAccount.name || !newAccount.account_type || !newAccount.nature) {
        toast.error('Por favor complete todos los campos obligatorios')
        return
      }

      creating.value = true
      try {
        const accountData = {
          code: newAccount.code,
          name: newAccount.name,
          account_type: newAccount.account_type,
          nature: newAccount.nature,
          parent_code: newAccount.parent_code || null,
          level: newAccount.level,
          account_relationship_type: newAccount.account_relationship_type,
          description: newAccount.description || null
        }

        const response = await api.post('/accounts', accountData, {
          params: { company_id: currentCompany.value.id }
        })

        toast.success('Cuenta creada exitosamente')
        closeCreateAccountModal()
        loadAccounts()
      } catch (error) {
        console.error('Error creating account:', error)
        toast.error('Error al crear la cuenta')
      } finally {
        creating.value = false
      }
    }

    // Watchers
    watch(() => newAccount.parent_code, () => {
      updateAccountLevel()
      generateSuggestedCode()
    })

    watch(() => newAccount.account_relationship_type, () => {
      generateSuggestedCode()
    })

    watch(() => newAccount.account_type, () => {
      generateSuggestedCode()
    })

    // Lifecycle
    onMounted(() => {
      loadAccounts()
    })

    return {
      accounts,
      loading,
      currentPage,
      totalPages,
      visiblePages,
      filters,
      showCreateAccountModal,
      creating,
      fixingHierarchy,
      newAccount,
      suggestedCode,
      parentAccounts,
      loadAccounts,
      debouncedSearch,
      changePage,
      clearFilters,
      editAccount,
      viewAccountMovements,
      toggleAccountStatus,
      fixCompleteHierarchy,
      getAccountTypeColor,
      getAccountBalance,
      balanceClass,
      formatCurrency,
      getRelationshipType,
      getRelationshipClass,
      getAccountRowClass,
      closeCreateAccountModal,
      updateAccountLevel,
      generateSuggestedCode,
      createAccount
    }
  }
}
</script>

<style scoped>
.table th {
  border-top: none;
  font-weight: 600;
  color: #5a5c69;
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

