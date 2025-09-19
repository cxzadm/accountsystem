<template>
  <div class="ledger-page">
    <!-- Page Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h1 class="h3 mb-0">Mayor General</h1>
        <p class="text-muted">Consulta el estado de las cuentas contables</p>
        <small class="text-info" v-if="calculatingBalances">
          <i class="fas fa-sync-alt fa-spin me-1"></i>
          Calculando saldos padre automáticamente...
        </small>
      </div>
      <div class="d-flex gap-2">
        <button class="btn btn-outline-secondary" @click="toggleView">
          <i :class="showAccountSummary ? 'fas fa-list' : 'fas fa-chart-bar'" class="me-2"></i>
          {{ showAccountSummary ? 'Ver Asientos' : 'Ver Resumen' }}
        </button>
        <div v-if="showAccountSummary" class="btn-group">
          <button class="btn btn-outline-secondary" @click="expandAll"><i class="fas fa-angle-double-down me-1"></i> Expandir todo</button>
          <button class="btn btn-outline-secondary" @click="collapseAll"><i class="fas fa-angle-double-up me-1"></i> Contraer todo</button>
        </div>
        <div v-else class="btn-group">
          <button class="btn btn-outline-secondary" @click="expandAllEntries"><i class="fas fa-angle-double-down me-1"></i> Expandir todo</button>
          <button class="btn btn-outline-secondary" @click="collapseAllEntries"><i class="fas fa-angle-double-up me-1"></i> Contraer todo</button>
        </div>
        <button class="btn btn-warning me-2" @click="fixCompleteHierarchy" :disabled="fixingHierarchy">
          <i class="fas fa-sync-alt me-2"></i>
          <span v-if="fixingHierarchy">Corrigiendo...</span>
          <span v-else>Corregir Jerarquía Completa</span>
        </button>
        <div class="btn-group">
          <button class="btn btn-outline-primary dropdown-toggle" data-bs-toggle="dropdown" aria-expanded="false">
            <i class="fas fa-download me-2"></i> Exportar
          </button>
          <ul class="dropdown-menu dropdown-menu-end">
            <li><a class="dropdown-item" href="#" @click.prevent="exportLedger('xlsx')"><i class="fas fa-file-excel me-2 text-success"></i> Excel (XLSX)</a></li>
            <li><a class="dropdown-item" href="#" @click.prevent="exportLedger('csv')"><i class="fas fa-file-csv me-2 text-success"></i> CSV</a></li>
            <li><a class="dropdown-item" href="#" @click.prevent="exportLedger('pdf')"><i class="fas fa-file-pdf me-2 text-danger"></i> PDF</a></li>
          </ul>
        </div>
      </div>
    </div>

    <!-- Filters -->
    <div class="card mb-4">
      <div class="card-body">
        <div class="row">
          <div class="col-md-3">
            <label class="form-label">Fecha Inicio</label>
            <input
              type="date"
              class="form-control"
              v-model="filters.start_date"
              @change="loadLedger"
            />
          </div>
          <div class="col-md-3">
            <label class="form-label">Fecha Fin</label>
            <input
              type="date"
              class="form-control"
              v-model="filters.end_date"
              @change="loadLedger"
            />
          </div>
          <div class="col-md-3">
            <label class="form-label">Tipo de Cuenta</label>
            <select class="form-select" v-model="filters.account_type" @change="loadLedger">
              <option value="">Todos los tipos</option>
              <option value="activo">Activo</option>
              <option value="pasivo">Pasivo</option>
              <option value="patrimonio">Patrimonio</option>
              <option value="ingresos">Ingresos</option>
              <option value="gastos">Gastos</option>
              <option value="costos">Costos</option>
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

    <!-- Summary Cards -->
    <div class="row mb-4" v-if="summary">
      <div class="col-md-3">
        <div class="card bg-primary text-white">
          <div class="card-body">
            <div class="d-flex justify-content-between">
              <div>
                <h6 class="card-title">Total Débitos</h6>
                <h4>{{ formatCurrency(summary.total_debits) }}</h4>
              </div>
              <div class="align-self-center">
                <i class="fas fa-arrow-up fa-2x"></i>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card bg-success text-white">
          <div class="card-body">
            <div class="d-flex justify-content-between">
              <div>
                <h6 class="card-title">Total Créditos</h6>
                <h4>{{ formatCurrency(summary.total_credits) }}</h4>
              </div>
              <div class="align-self-center">
                <i class="fas fa-arrow-down fa-2x"></i>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card bg-info text-white">
          <div class="card-body">
            <div class="d-flex justify-content-between">
              <div>
                <h6 class="card-title">Saldo Neto</h6>
                <h4>{{ formatCurrency(summary.total_balance) }}</h4>
              </div>
              <div class="align-self-center">
                <i class="fas fa-balance-scale fa-2x"></i>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card" :class="summary.is_balanced ? 'bg-success' : 'bg-danger'">
          <div class="card-body text-white">
            <div class="d-flex justify-content-between">
              <div>
                <h6 class="card-title">Estado</h6>
                <h4>{{ summary.is_balanced ? 'Balanceado' : 'Desbalanceado' }}</h4>
              </div>
              <div class="align-self-center">
                <i :class="summary.is_balanced ? 'fas fa-check-circle' : 'fas fa-exclamation-triangle'" class="fa-2x"></i>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Ledger Table -->
    <div class="card">
      <div class="card-body">
        <div class="table-responsive">
          <!-- Vista de Resumen de Cuentas -->
          <table v-if="showAccountSummary" class="table table-hover">
            <thead>
              <tr>
                <th style="width: 40px;"></th>
                <th>Código</th>
                <th>Cuenta</th>
                <th>Tipo</th>
                <th>Padre/Hija</th>
                <th>Saldo Inicial (D - C)</th>
                <th>Total Débitos</th>
                <th>Total Créditos</th>
                <th>Saldo Actual (D - C)</th>
                <th>Movimientos</th>
                <th>Última Transacción</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="loading">
                <td colspan="12" class="text-center py-4">
                  <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Cargando...</span>
                  </div>
                </td>
              </tr>
              <tr v-else-if="ledger.length === 0">
                <td colspan="12" class="text-center py-4 text-muted">
                  No se encontraron cuentas
                </td>
              </tr>
              <template v-else v-for="account in filteredLedger" :key="account.account_id">
              <tr :class="getAccountRowClass(account)">
                <td>
                  <button
                    class="btn btn-sm btn-outline-secondary"
                    @click="toggleExpand(account)"
                    :title="isExpanded(account) ? 'Contraer' : 'Expandir'"
                  >
                    <i :class="isExpanded(account) ? 'fas fa-chevron-up' : 'fas fa-chevron-down'"></i>
                  </button>
                </td>
                <td>
                  <code :style="{ paddingLeft: (account.level - 1) * 20 + 'px' }">
                    {{ account.account_code }}
                  </code>
                </td>
                <td :style="{ paddingLeft: (account.level - 1) * 20 + 'px' }">
                  <div>
                    <strong>{{ account.account_name }}</strong>
                    <div class="text-muted small">
                      {{ account.nature }}
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
                <td class="text-center">
                  <span class="badge" :class="getRelationshipClass(account)">
                    {{ getRelationshipType(account) }}
                  </span>
                </td>
                <td class="text-end">
                  <span :class="netClass(initialNet(account))">{{ formatCurrency(initialNet(account)) }}</span>
                </td>
                <td class="text-end">
                  <strong class="text-danger">{{ formatCurrency(account.total_debits) }}</strong>
                </td>
                <td class="text-end">
                  <strong class="text-success">{{ formatCurrency(account.total_credits) }}</strong>
                </td>
                <td class="text-end">
                  <span :class="netClass(actualNet(account))">{{ formatCurrency(actualNet(account)) }}</span>
                </td>
                <td class="text-center">
                  <span class="badge bg-secondary">{{ account.entry_count }}</span>
                </td>
                <td>
                  <span v-if="account.last_transaction_date" class="small">
                    {{ formatDate(account.last_transaction_date) }}
                  </span>
                  <span v-else class="text-muted small">Sin movimientos</span>
                </td>
                <td>
                  <button
                    class="btn btn-sm btn-outline-primary"
                    @click="viewAccountLedger(account)"
                    title="Ver Mayor"
                  >
                    <i class="fas fa-eye"></i>
                  </button>
                </td>
              </tr>
              <!-- Expanded inline ledger details -->
              <tr v-if="isExpanded(account)">
                <td colspan="12">
                  <div class="p-2 border rounded bg-light">
                    <div class="d-flex justify-content-between align-items-center mb-2">
                      <div class="fw-semibold">Mayor de Cuenta: <code>{{ account.account_code }}</code> - {{ account.account_name }}</div>
                      <div v-if="expanded[account.account_id]?.loading" class="text-muted small">Cargando...</div>
                    </div>
                    <div class="table-responsive">
                      <table class="table table-sm table-striped table-bordered mb-0">
                        <thead>
                          <tr>
                            <th>Fecha</th>
                            <th>Descripción</th>
                            <th>Referencia</th>
                            <th class="text-end">Débito</th>
                            <th class="text-end">Crédito</th>
                            <th class="text-end">Saldo (D - C)</th>
                          </tr>
                        </thead>
                        <tbody>
                          <tr v-for="entry in (expanded[account.account_id]?.entries || [])" :key="entry.id">
                            <td>{{ formatDate(entry.date) }}</td>
                            <td>{{ entry.description }}</td>
                            <td>{{ entry.reference || '-' }}</td>
                            <td class="text-end">
                              <span v-if="entry.debit_amount > 0" class="text-danger fw-bold">{{ formatCurrency(entry.debit_amount) }}</span>
                              <span v-else class="text-muted">-</span>
                            </td>
                            <td class="text-end">
                              <span v-if="entry.credit_amount > 0" class="text-success fw-bold">{{ formatCurrency(entry.credit_amount) }}</span>
                              <span v-else class="text-muted">-</span>
                            </td>
                            <td class="text-end">
                              <span :class="[(entry.running_debit_balance - entry.running_credit_balance) >= 0 ? 'text-danger fw-bold' : 'text-success fw-bold']">
                                {{ formatCurrency((entry.running_debit_balance || 0) - (entry.running_credit_balance || 0)) }}
                              </span>
                            </td>
                          </tr>
                          <tr v-if="!expanded[account.account_id]?.entries || expanded[account.account_id]?.entries.length === 0">
                            <td colspan="6" class="text-center text-muted">Sin movimientos</td>
                          </tr>
                        </tbody>
                      </table>
                    </div>
                  </div>
                </td>
              </tr>
              </template>
            </tbody>
          </table>

          <!-- Vista de Asientos Contables -->
          <table v-else class="table table-hover">
            <thead>
              <tr>
                <th style="width: 40px;"></th>
                <th>Fecha</th>
                <th>Número</th>
                <th>Descripción</th>
                <th>Tipo</th>
                <th>Total Débito</th>
                <th>Total Crédito</th>
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
              <tr v-else-if="ledgerEntries.length === 0">
                <td colspan="9" class="text-center py-4 text-muted">
                  No se encontraron asientos mayorizados
                </td>
              </tr>
              <template v-else v-for="entry in filteredLedgerEntries" :key="entry.id">
              <tr>
                <td>
                  <button
                    class="btn btn-sm btn-outline-secondary"
                    @click="toggleExpandEntry(entry)"
                    :title="isEntryExpanded(entry) ? 'Contraer' : 'Expandir'"
                  >
                    <i :class="isEntryExpanded(entry) ? 'fas fa-chevron-up' : 'fas fa-chevron-down'"></i>
                  </button>
                </td>
                <td>{{ formatDate(entry.date) }}</td>
                <td>
                  <code>{{ entry.entry_number }}</code>
                </td>
                <td>
                  <div>
                    <strong>{{ entry.description }}</strong>
                    <div class="text-muted small">
                      {{ entry.entry_type }}
                    </div>
                  </div>
                </td>
                <td>
                  <span class="badge bg-info">{{ entry.entry_type }}</span>
                </td>
                <td class="text-end">
                  <strong class="text-danger">{{ formatCurrency(entry.total_debit) }}</strong>
                </td>
                <td class="text-end">
                  <strong class="text-success">{{ formatCurrency(entry.total_credit) }}</strong>
                </td>
                <td>
                  <span class="badge bg-success">Mayorizado</span>
                </td>
                <td>
                  <button
                    class="btn btn-sm btn-outline-primary"
                    @click="viewEntryDetails(entry)"
                    title="Ver Detalles"
                  >
                    <i class="fas fa-eye"></i>
                  </button>
                </td>
              </tr>
              <tr v-if="isEntryExpanded(entry)">
                <td colspan="9">
                  <div class="p-2 border rounded bg-light">
                    <div class="d-flex justify-content-between align-items-center mb-2">
                      <div class="fw-semibold">Detalle del Asiento: <code>{{ entry.entry_number }}</code></div>
                      <div v-if="entriesExpanded[entry.id]?.loading" class="text-muted small">Cargando...</div>
                    </div>
                    <div class="table-responsive">
                      <table class="table table-sm table-striped table-bordered mb-0">
                        <thead>
                          <tr>
                            <th>Código</th>
                            <th>Cuenta</th>
                            <th>Descripción</th>
                            <th class="text-end">Débito</th>
                            <th class="text-end">Crédito</th>
                          </tr>
                        </thead>
                        <tbody>
                          <tr v-for="line in (entriesExpanded[entry.id]?.lines || [])" :key="line.id || line.account_code + '-' + line.description">
                            <td><code>{{ line.account_code }}</code></td>
                            <td>{{ line.account_name || '-' }}</td>
                            <td>{{ line.description || '-' }}</td>
                            <td class="text-end">
                              <span v-if="Number(line.debit||0) > 0" class="text-danger fw-bold">{{ formatCurrency(Number(line.debit||0)) }}</span>
                              <span v-else class="text-muted">-</span>
                            </td>
                            <td class="text-end">
                              <span v-if="Number(line.credit||0) > 0" class="text-success fw-bold">{{ formatCurrency(Number(line.credit||0)) }}</span>
                              <span v-else class="text-muted">-</span>
                            </td>
                          </tr>
                          <tr v-if="!entriesExpanded[entry.id] || (entriesExpanded[entry.id]?.lines||[]).length === 0">
                            <td colspan="5" class="text-center text-muted">Sin detalle</td>
                          </tr>
                        </tbody>
                      </table>
                    </div>
                  </div>
                </td>
              </tr>
              </template>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Account Ledger Modal -->
    <div class="modal fade" id="accountLedgerModal" tabindex="-1" @click="closeModal">
      <div class="modal-dialog modal-xl" @click.stop>
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">
              <span v-if="showAccountSummary">Mayor de Cuenta: {{ selectedAccount?.account_code }} - {{ selectedAccount?.account_name }}</span>
              <span v-else>Detalle del Asiento: {{ selectedAccount?.entry_number }}</span>
            </h5>
            <div class="d-flex align-items-center gap-2">
              <button type="button" class="btn btn-sm btn-outline-secondary" @click="closeModal">
                <i class="fas fa-arrow-left me-1"></i> Regresar
              </button>
              <button type="button" class="btn btn-sm btn-outline-primary" @click="printSelected">
                <i class="fas fa-print me-1"></i> Imprimir
              </button>
              <button type="button" class="btn-close" @click="closeModal"></button>
            </div>
          </div>
          <div class="modal-body">
            <!-- Meta info bar for entry details to match Journal modal -->
            <div v-if="selectedAccount && !showAccountSummary" class="mb-3">
              <div class="row">
                <div class="col-md-3"><strong>Fecha:</strong> {{ formatDate(selectedAccount.date) }}</div>
                <div class="col-md-3"><strong>Tipo:</strong> {{ selectedAccount.entry_type }}</div>
                <div class="col-md-6"><strong>Descripción:</strong> {{ selectedAccount.account_name }}</div>
              </div>
            </div>
            <div v-if="selectedAccount" class="table-responsive">
              <table class="table table-sm table-striped table-bordered">
                <thead>
                  <tr>
                    <th>Fecha</th>
                    <th>Cuenta</th>
                    <th>Descripción</th>
                    <th>Referencia</th>
                    <th>Débito</th>
                    <th>Crédito</th>
                    <th v-if="showAccountSummary">Saldo (D - C)</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="entry in selectedAccount.entries" :key="entry.id">
                    <td>{{ formatDate(entry.date) }}</td>
                    <td>
                      <a v-if="entry.account_code" href="#" @click.prevent="openAccountLedgerByCode(entry.account_code)">
                        <code>{{ entry.account_code }}</code>
                      </a>
                      <span v-else class="text-muted">-</span>
                    </td>
                    <td>{{ entry.description }}</td>
                    <td>{{ entry.reference || '-' }}</td>
                    <td class="text-end">
                      <span v-if="entry.debit_amount > 0" class="text-danger fw-bold">
                        {{ formatCurrency(entry.debit_amount) }}
                      </span>
                      <span v-else class="text-muted">-</span>
                    </td>
                    <td class="text-end">
                      <span v-if="entry.credit_amount > 0" class="text-success fw-bold">
                        {{ formatCurrency(entry.credit_amount) }}
                      </span>
                      <span v-else class="text-muted">-</span>
                    </td>
                    <td v-if="showAccountSummary" class="text-end">
                      <span :class="[(entry.running_debit_balance - entry.running_credit_balance) >= 0 ? 'text-danger fw-bold' : 'text-success fw-bold']">
                        {{ formatCurrency((entry.running_debit_balance || 0) - (entry.running_credit_balance || 0)) }}
                      </span>
                    </td>
                  </tr>
                </tbody>
                <tfoot v-if="!showAccountSummary">
                  <tr class="table-dark">
                    <th colspan="4" class="text-end">TOTALES:</th>
                    <th class="text-end text-danger">
                      {{ formatCurrency(selectedAccount.entries.reduce((sum, entry) => sum + (entry.debit_amount || 0), 0)) }}
                    </th>
                    <th class="text-end text-success">
                      {{ formatCurrency(selectedAccount.entries.reduce((sum, entry) => sum + (entry.credit_amount || 0), 0)) }}
                    </th>
                  </tr>
                </tfoot>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
    <!-- Reusable Entry Detail Modal instance -->
    <EntryDetailModal
      modal-id="entryDetailModal"
      :entry="selectedEntryForModal"
      @open-account-ledger="openAccountLedgerByCode"
    />
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useToast } from 'vue-toastification'
import { useCompanyStore } from '@/stores/company'
import api from '@/services/api'
import { alerts } from '@/services/alerts'
import { printElement, printHtml } from '@/services/print'
import EntryDetailModal from '@/components/EntryDetailModal.vue'
import * as XLSX from 'xlsx'

export default {
  name: 'Ledger',
  components: { EntryDetailModal },
  setup() {
    const toast = useToast()
    const companyStore = useCompanyStore()

    // State
    const loading = ref(false)
    const calculatingBalances = ref(false)
    const fixingHierarchy = ref(false)
    const ledger = ref([])
    const ledgerEntries = ref([]) // Asientos contables mayorizados
    const summary = ref(null)
    const selectedAccount = ref(null)
    const showAccountSummary = ref(false) // Por defecto mostrar ASIENTOS

    const filters = reactive({
      start_date: '',
      end_date: '',
      account_type: ''
    })

    const selectedEntryForModal = ref(null)
    const expanded = ref({})
    const entriesExpanded = ref({})

    // Computed
    const currentCompany = computed(() => companyStore.getCurrentCompany())

    const filteredLedger = computed(() => {
      if (!filters.account_type) return ledger.value
      return ledger.value.filter(account => account.account_type === filters.account_type)
    })

    const filteredLedgerEntries = computed(() => {
      return ledgerEntries.value // Los asientos ya vienen filtrados por fecha del backend
    })

    // Methods
    const loadLedger = async () => {
      if (!currentCompany.value) {
        toast.error('Selecciona una empresa primero')
        return
      }

      console.log('Loading ledger for company:', currentCompany.value.id)
      loading.value = true
      try {
        // El cálculo automático ahora se ejecuta automáticamente en el backend
        // No es necesario ejecutarlo manualmente aquí
        calculatingBalances.value = true
        console.log('🔄 Cargando Mayor General (cálculo automático ejecutado en backend)...')

        const params = {
          company_id: currentCompany.value.id
        }

        if (filters.start_date) {
          params.start_date = filters.start_date
        }
        if (filters.end_date) {
          params.end_date = filters.end_date
        }

        console.log('Ledger params:', params)

        const [ledgerResponse, ledgerEntriesResponse, summaryResponse] = await Promise.all([
          api.get('/ledger/', { params }),
          api.get('/ledger/entries/', { params }),
          api.get('/ledger/summary/', { params })
        ])

        console.log('Ledger response:', ledgerResponse.data)
        console.log('Ledger entries response:', ledgerEntriesResponse.data)
        console.log('Summary response:', summaryResponse.data)

        ledger.value = ledgerResponse.data
        ledgerEntries.value = ledgerEntriesResponse.data
        summary.value = summaryResponse.data
        
        console.log('✅ Mayor general cargado con datos consistentes (cálculo automático ejecutado en backend)')
      } catch (error) {
        console.error('Error loading ledger:', error)
        console.error('Error details:', error.response?.data)
        toast.error(`Error al cargar mayor general: ${error.response?.data?.detail || error.message}`)
      } finally {
        loading.value = false
        calculatingBalances.value = false
      }
    }

    const fixCompleteHierarchy = async () => {
      console.log('🚀 INICIANDO corrección manual de jerarquía completa')
      console.log('🔍 Método fixCompleteHierarchy llamado correctamente')
      
      const ok = await alerts.confirm({
        title: '¿Corregir jerarquía completa?',
        text: 'Esta acción recalculará automáticamente los saldos de TODAS las cuentas padre en toda la jerarquía.',
        icon: 'question',
        confirmButtonText: 'Corregir'
      })
      
      console.log('📋 Confirmación del usuario:', ok)
      
      if (ok) {
        fixingHierarchy.value = true
        console.log('🔄 Ejecutando corrección de jerarquía...')
        try {
          console.log('📡 Enviando petición a:', '/accounts/fix-complete-hierarchy')
          console.log('🏢 Company ID:', currentCompany.value.id)
          
          const response = await api.post('/accounts/fix-complete-hierarchy', {}, {
            params: { company_id: currentCompany.value.id }
          })
          
          console.log('✅ Respuesta recibida:', response.data)
          
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
            }
          }
          
          // Recargar el ledger para mostrar los cambios
          await loadLedger()
          
        } catch (error) {
          console.error('❌ ERROR al corregir jerarquía:', error)
          console.error('📋 Detalles del error:', error.response?.data)
          console.error('📋 Status code:', error.response?.status)
          toast.error(`Error al corregir jerarquía: ${error.response?.data?.detail || error.message}`)
        } finally {
          fixingHierarchy.value = false
          console.log('🏁 FINALIZADO corrección de jerarquía')
        }
      }
    }

    const viewAccountLedger = async (account) => {
      try {
        console.log('Cargando mayor de cuenta específica (cálculo automático en backend)...')
        
        // Usar endpoint robusto /entries
        const params = { company_id: currentCompany.value.id }
        if (filters.start_date) params.start_date = filters.start_date
        if (filters.end_date) params.end_date = filters.end_date
        const { data } = await api.get(`/ledger/account/${account.account_id}/entries/`, { params })

        const mappedEntries = (data.entries || []).map(entry => ({
          ...entry,
          date: new Date(entry.date),
          debit_amount: entry.debit_amount || 0,
          credit_amount: entry.credit_amount || 0,
          running_debit_balance: entry.running_debit_balance || 0,
          running_credit_balance: entry.running_credit_balance || 0
        }))

        // Insertar fila de Saldo inicial para mostrar el saldo de apertura
        const openingDebit = data.initial_debit_balance || 0
        const openingCredit = data.initial_credit_balance || 0
        const openingDate = filters.start_date ? new Date(filters.start_date) : (mappedEntries[0]?.date || new Date())
        const openingRow = {
          id: 'opening-balance',
          account_id: data.account_id,
          account_code: data.account_code,
          account_name: data.account_name,
          company_id: params.company_id,
          entry_type: 'opening',
          journal_entry_id: null,
          date: openingDate,
          description: 'Saldo inicial',
          reference: '-',
          debit_amount: openingDebit,
          credit_amount: openingCredit,
          running_debit_balance: openingDebit,
          running_credit_balance: openingCredit,
          created_at: openingDate,
          created_by: ''
        }

        selectedAccount.value = {
          account_id: data.account_id,
          account_code: data.account_code,
          account_name: data.account_name,
          entries: [openingRow, ...mappedEntries]
        }
        showAccountSummary.value = true
      } catch (e) {
        console.error('Error loading account ledger:', e)
        toast.error('Error al cargar el mayor de la cuenta')
        return
      }

      // Usar el modal de Bootstrap de manera compatible
      const modalElement = document.getElementById('accountLedgerModal')
      if (modalElement) {
        if (window.bootstrap && window.bootstrap.Modal) {
          const modal = new window.bootstrap.Modal(modalElement)
          modal.show()
        } else {
          modalElement.classList.add('show')
          modalElement.style.display = 'block'
          modalElement.setAttribute('aria-hidden', 'false')
          document.body.classList.add('modal-open')
          const backdrop = document.createElement('div')
          backdrop.className = 'modal-backdrop fade show'
          backdrop.id = 'modal-backdrop'
          document.body.appendChild(backdrop)
        }
      }
    }

    const closeModal = () => {
      const modalElement = document.getElementById('accountLedgerModal')
      if (modalElement) {
        // Verificar si Bootstrap está disponible
        if (window.bootstrap && window.bootstrap.Modal) {
          const modal = window.bootstrap.Modal.getInstance(modalElement)
          if (modal) {
            modal.hide()
          }
        } else {
          // Fallback: cerrar el modal manualmente
          modalElement.classList.remove('show')
          modalElement.style.display = 'none'
          modalElement.setAttribute('aria-hidden', 'true')
          document.body.classList.remove('modal-open')
          
          // Remover backdrop
          const backdrop = document.getElementById('modal-backdrop')
          if (backdrop) {
            backdrop.remove()
          }
        }
      }
    }

    const buildExpandedEntries = () => {
      const details = []
      for (const acc of filteredLedger.value) {
        const state = expanded.value[acc.account_id]
        if (state?.open && Array.isArray(state.entries) && state.entries.length > 0) {
          for (const entry of state.entries) {
            details.push({
              account_code: acc.account_code,
              account_name: acc.account_name,
              date: entry.date,
              description: entry.description,
              reference: entry.reference,
              debit_amount: Number(entry.debit_amount || 0),
              credit_amount: Number(entry.credit_amount || 0),
              running_debit_balance: Number(entry.running_debit_balance || 0),
              running_credit_balance: Number(entry.running_credit_balance || 0)
            })
          }
        }
      }
      return details
    }

    const exportLedger = async (format) => {
      const isSummary = showAccountSummary.value
      try {
        if (format === 'csv') {
          const rows = []
          if (isSummary) {
            rows.push(['Código', 'Cuenta', 'Tipo', 'Saldo Inicial (D-C)', 'Total Débitos', 'Total Créditos', 'Saldo Actual (D-C)', 'Movimientos'])
            for (const acc of filteredLedger.value) {
              const ini = Number(acc.initial_debit_balance||0) - Number(acc.initial_credit_balance||0)
              const act = ini + (Number(acc.total_debits||0) - Number(acc.total_credits||0))
              rows.push([
                acc.account_code,
                acc.account_name,
                acc.account_type,
                ini.toString(),
                Number(acc.total_debits||0).toString(),
                Number(acc.total_credits||0).toString(),
                act.toString(),
                acc.entry_count?.toString() || '0'
              ])
              const state = expanded.value[acc.account_id]
              if (state?.open && state.entries?.length) {
                rows.push(['', 'DETALLE EXPANDIDO', '', '', '', '', '', ''])
                rows.push(['', 'Fecha', 'Descripción', 'Referencia', 'Débito', 'Crédito', 'Saldo (D-C)', ''])
                for (const e of state.entries) {
                  const saldo = (Number(e.running_debit_balance||0) - Number(e.running_credit_balance||0)).toString()
                  rows.push([
                    '',
                    new Date(e.date).toISOString().split('T')[0],
                    e.description || '-',
                    e.reference || '-',
                    Number(e.debit_amount||0).toString(),
                    Number(e.credit_amount||0).toString(),
                    saldo,
                    ''
                  ])
                }
              }
            }
          } else {
            rows.push(['Fecha', 'Número', 'Descripción', 'Tipo', 'Total Débito', 'Total Crédito', 'Estado'])
            for (const e of filteredLedgerEntries.value) {
              rows.push([
                new Date(e.date).toISOString().split('T')[0],
                e.entry_number,
                e.description,
                e.entry_type,
                Number(e.total_debit||0).toString(),
                Number(e.total_credit||0).toString(),
                e.status
              ])
            }
          }
          const csv = rows.map(r => r.map(v => `"${(v??'').toString().replace(/"/g,'""')}"`).join(',')).join('\n')
          const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
          const url = URL.createObjectURL(blob)
          const a = document.createElement('a')
          a.href = url
          a.download = isSummary ? 'mayor_resumen.csv' : 'mayor_asientos.csv'
          a.click()
          URL.revokeObjectURL(url)
          toast.success('Exportado a CSV')
        } else if (format === 'xlsx') {
          const wb = XLSX.utils.book_new()

          if (isSummary) {
            // Hoja Resumen
            const resumenRows = [['Código', 'Cuenta', 'Tipo', 'Saldo Inicial (D-C)', 'Total Débitos', 'Total Créditos', 'Saldo Actual (D-C)', 'Movimientos']]
            for (const acc of filteredLedger.value) {
              const ini = Number(acc.initial_debit_balance||0) - Number(acc.initial_credit_balance||0)
              const act = ini + (Number(acc.total_debits||0) - Number(acc.total_credits||0))
              resumenRows.push([
                acc.account_code,
                acc.account_name,
                acc.account_type,
                ini,
                Number(acc.total_debits||0),
                Number(acc.total_credits||0),
                act,
                Number(acc.entry_count||0)
              ])
            }
            const wsResumen = XLSX.utils.aoa_to_sheet(resumenRows)
            XLSX.utils.book_append_sheet(wb, wsResumen, 'Resumen')

            // Hoja Movimientos (solo cuentas expandidas)
            const detalles = buildExpandedEntries()
            if (detalles.length > 0) {
              const detalleRows = [['Código', 'Cuenta', 'Fecha', 'Descripción', 'Referencia', 'Débito', 'Crédito', 'Saldo (D-C)']]
              for (const d of detalles) {
                const saldo = Number((d.running_debit_balance || 0) - (d.running_credit_balance || 0))
                detalleRows.push([
                  d.account_code,
                  d.account_name,
                  new Date(d.date).toISOString().split('T')[0],
                  d.description || '-',
                  d.reference || '-',
                  Number(d.debit_amount||0),
                  Number(d.credit_amount||0),
                  saldo
                ])
              }
              const wsDet = XLSX.utils.aoa_to_sheet(detalleRows)
              XLSX.utils.book_append_sheet(wb, wsDet, 'Movimientos')
            }
          } else {
            // Vista Asientos
            const rows = [['Fecha', 'Número', 'Descripción', 'Tipo', 'Total Débito', 'Total Crédito', 'Estado']]
            for (const e of filteredLedgerEntries.value) {
              rows.push([
                new Date(e.date).toISOString().split('T')[0],
                e.entry_number,
                e.description,
                e.entry_type,
                Number(e.total_debit||0),
                Number(e.total_credit||0),
                e.status
              ])
            }
            const ws = XLSX.utils.aoa_to_sheet(rows)
            XLSX.utils.book_append_sheet(wb, ws, 'Asientos')

            // Hoja Detalles (solo asientos expandidos)
            const detalles = []
            for (const e of filteredLedgerEntries.value) {
              const state = entriesExpanded.value[e.id]
              if (state?.open && state.lines?.length) {
                for (const line of state.lines) {
                  detalles.push({
                    entry_number: e.entry_number,
                    entry_date: new Date(e.date).toISOString().split('T')[0],
                    account_code: line.account_code,
                    account_name: line.account_name,
                    description: line.description,
                    debit: Number(line.debit||0),
                    credit: Number(line.credit||0)
                  })
                }
              }
            }
            if (detalles.length > 0) {
              const detalleRows = [['Asiento', 'Fecha', 'Código', 'Cuenta', 'Descripción', 'Débito', 'Crédito']]
              for (const d of detalles) {
                detalleRows.push([
                  d.entry_number,
                  d.entry_date,
                  d.account_code,
                  d.account_name,
                  d.description,
                  d.debit,
                  d.credit
                ])
              }
              const wsDet = XLSX.utils.aoa_to_sheet(detalleRows)
              XLSX.utils.book_append_sheet(wb, wsDet, 'Detalles')
            }
          }

          const fileName = isSummary ? 'mayor.xlsx' : 'mayor_asientos.xlsx'
          XLSX.writeFile(wb, fileName)
          toast.success('Exportado a Excel (XLSX)')
        } else if (format === 'pdf') {
          // Construir HTML amigable para impresión/guardado a PDF
          const title = isSummary ? 'Mayor - Resumen' : 'Mayor - Asientos'
          let html = ''
          if (isSummary) {
            html += '<h3>Mayor General - Resumen</h3>'
            html += `<div><strong>Rango:</strong> ${filters.start_date || '-'} a ${filters.end_date || '-'}</div>`
            html += '<div class="table-responsive"><table class="table table-sm table-striped table-bordered"><thead><tr>'+
                    '<th>Código</th><th>Cuenta</th><th>Tipo</th><th>Saldo Inicial (D - C)</th><th>Total Débitos</th><th>Total Créditos</th><th>Saldo Actual (D - C)</th><th>Movimientos</th>'+
                    '</tr></thead><tbody>'
            for (const acc of filteredLedger.value) {
              const ini = Number(acc.initial_debit_balance||0) - Number(acc.initial_credit_balance||0)
              const act = ini + (Number(acc.total_debits||0) - Number(acc.total_credits||0))
              html += `<tr><td><code>${acc.account_code}</code></td><td>${acc.account_name}</td><td>${acc.account_type}</td>`+
                      `<td class="text-end">${ini.toLocaleString('es-EC')}</td>`+
                      `<td class="text-end">${Number(acc.total_debits||0).toLocaleString('es-EC')}</td>`+
                      `<td class="text-end">${Number(acc.total_credits||0).toLocaleString('es-EC')}</td>`+
                      `<td class="text-end">${act.toLocaleString('es-EC')}</td>`+
                      `<td class="text-center">${Number(acc.entry_count||0)}</td></tr>`
              const state = expanded.value[acc.account_id]
              if (state?.open && state.entries?.length) {
                html += '</tbody></table></div>'
                html += `<div class="mt-2 mb-3"><strong>Mayor de Cuenta:</strong> <code>${acc.account_code}</code> - ${acc.account_name}</div>`
                html += '<div class="table-responsive"><table class="table table-sm table-striped table-bordered"><thead><tr>'+
                        '<th>Fecha</th><th>Descripción</th><th>Referencia</th><th class="text-end">Débito</th><th class="text-end">Crédito</th><th class="text-end">Saldo (D - C)</th>'+
                        '</tr></thead><tbody>'
                for (const e of state.entries) {
                  const saldo = Number((Number(e.running_debit_balance||0) - Number(e.running_credit_balance||0)))
                  const fecha = new Date(e.date).toLocaleDateString('es-EC')
                  html += `<tr><td>${fecha}</td><td>${e.description || '-'}</td><td>${e.reference || '-'}</td>`+
                          `<td class="text-end">${Number(e.debit_amount||0).toLocaleString('es-EC')}</td>`+
                          `<td class="text-end">${Number(e.credit_amount||0).toLocaleString('es-EC')}</td>`+
                          `<td class="text-end">${saldo.toLocaleString('es-EC')}</td></tr>`
                }
                html += '</tbody></table></div>'
                html += '<hr />'
              }
            }
            // Reabrir tabla si no hubo detalles
            html += '<div class="table-responsive"></div>'
          } else {
            html += '<h3>Mayor General - Asientos</h3>'
            html += `<div><strong>Rango:</strong> ${filters.start_date || '-'} a ${filters.end_date || '-'}</div>`
            html += '<div class="table-responsive"><table class="table table-sm table-striped table-bordered"><thead><tr>'+
                    '<th>Fecha</th><th>Número</th><th>Descripción</th><th>Tipo</th><th class="text-end">Total Débito</th><th class="text-end">Total Crédito</th><th>Estado</th>'+
                    '</tr></thead><tbody>'
            for (const e of filteredLedgerEntries.value) {
              const fecha = new Date(e.date).toLocaleDateString('es-EC')
              html += `<tr><td>${fecha}</td><td><code>${e.entry_number}</code></td><td>${e.description}</td><td>${e.entry_type}</td>`+
                      `<td class="text-end">${Number(e.total_debit||0).toLocaleString('es-EC')}</td>`+
                      `<td class="text-end">${Number(e.total_credit||0).toLocaleString('es-EC')}</td>`+
                      `<td>${e.status}</td></tr>`
              
              // Mostrar detalle si está expandido
              const state = entriesExpanded.value[e.id]
              if (state?.open && state.lines?.length) {
                html += '</tbody></table></div>'
                html += `<div class="mt-2 mb-3"><strong>Detalle del Asiento:</strong> <code>${e.entry_number}</code> - ${e.description}</div>`
                html += '<div class="table-responsive"><table class="table table-sm table-striped table-bordered"><thead><tr>'+
                        '<th>Código</th><th>Cuenta</th><th>Descripción</th><th class="text-end">Débito</th><th class="text-end">Crédito</th>'+
                        '</tr></thead><tbody>'
                for (const line of state.lines) {
                  html += `<tr><td><code>${line.account_code || '-'}</code></td><td>${line.account_name || '-'}</td><td>${line.description || '-'}</td>`+
                          `<td class="text-end">${Number(line.debit||0).toLocaleString('es-EC')}</td>`+
                          `<td class="text-end">${Number(line.credit||0).toLocaleString('es-EC')}</td></tr>`
                }
                html += '</tbody></table></div>'
                html += '<hr />'
              }
            }
            html += '</tbody></table></div>'
          }
          printHtml(title, html)
        }
      } catch (e) {
        console.error('Error exporting ledger:', e)
        toast.error('No se pudo exportar')
      }
    }

    const expandAll = async () => {
      for (const acc of filteredLedger.value) {
        const state = expanded.value[acc.account_id] || { open: false, loading: false, entries: [] }
        state.open = true
        expanded.value[acc.account_id] = state
      }
      // Asegurar reactividad inmediata
      expanded.value = { ...expanded.value }
      // Cargar entradas en los expandidos sin datos
      for (const acc of filteredLedger.value) {
        const state = expanded.value[acc.account_id]
        if (state && state.open && state.entries.length === 0) {
          await fetchExpandedEntries(acc)
        }
      }
    }

    const collapseAll = () => {
      for (const id of Object.keys(expanded.value)) {
        expanded.value[id].open = false
      }
      expanded.value = { ...expanded.value }
    }

    // Asientos: expandir/contraer
    const isEntryExpanded = (entry) => {
      if (!entry || !entry.id) return false
      const state = entriesExpanded.value[entry.id]
      return Boolean(state && state.open)
    }

    const ensureEntryLinesLoaded = async (entry) => {
      const state = entriesExpanded.value[entry.id]
      if (!state) return
      if (Array.isArray(state.lines) && state.lines.length > 0) return
      try {
        state.loading = true
        // Intentar usar líneas existentes si vienen incluidas
        const lines = Array.isArray(entry.lines) ? entry.lines : []
        if (lines.length > 0) {
          state.lines = lines
        } else {
          // Fallback: intentar obtener por API si existe endpoint
          try {
            const params = { company_id: currentCompany.value?.id || '' }
            const { data } = await api.get(`/ledger/entries/${entry.id}/lines/`, { params })
            state.lines = Array.isArray(data?.lines) ? data.lines : []
          } catch (e) {
            console.warn('No se pudo obtener líneas por API, usando vacío')
            state.lines = []
          }
        }
      } finally {
        state.loading = false
        entriesExpanded.value = { ...entriesExpanded.value }
      }
    }

    const toggleExpandEntry = async (entry) => {
      if (!entry || !entry.id) return
      const state = entriesExpanded.value[entry.id] || { open: false, loading: false, lines: [] }
      state.open = !state.open
      entriesExpanded.value[entry.id] = state
      entriesExpanded.value = { ...entriesExpanded.value }
      if (state.open) {
        await ensureEntryLinesLoaded(entry)
      }
    }

    const expandAllEntries = async () => {
      for (const e of filteredLedgerEntries.value) {
        const state = entriesExpanded.value[e.id] || { open: false, loading: false, lines: [] }
        state.open = true
        entriesExpanded.value[e.id] = state
      }
      entriesExpanded.value = { ...entriesExpanded.value }
      for (const e of filteredLedgerEntries.value) {
        const state = entriesExpanded.value[e.id]
        if (state && state.open && (!state.lines || state.lines.length === 0)) {
          await ensureEntryLinesLoaded(e)
        }
      }
    }

    const collapseAllEntries = () => {
      for (const id of Object.keys(entriesExpanded.value)) {
        entriesExpanded.value[id].open = false
      }
      entriesExpanded.value = { ...entriesExpanded.value }
    }

    // Helpers de cálculo (D - C)
    const initialNet = (account) => {
      const d = Number(account.initial_debit_balance || 0)
      const c = Number(account.initial_credit_balance || 0)
      return d - c
    }

    const actualNet = (account) => {
      const initial = initialNet(account)
      const movD = Number(account.total_debits || 0)
      const movC = Number(account.total_credits || 0)
      return initial + (movD - movC)
    }

    const netClass = (amount) => {
      if (amount === 0) return 'text-muted'
      return amount > 0 ? 'text-danger fw-bold' : 'text-success fw-bold'
    }

    const clearFilters = () => {
      filters.start_date = ''
      filters.end_date = ''
      filters.account_type = ''
      loadLedger()
    }

    const toggleView = () => {
      showAccountSummary.value = !showAccountSummary.value
    }

    const isExpanded = (account) => {
      if (!account || !account.account_id) return false
      const state = expanded.value[account.account_id]
      return Boolean(state && state.open)
    }

    const fetchExpandedEntries = async (account) => {
      const state = expanded.value[account.account_id]
      if (!state) return
      try {
        state.loading = true
        const params = { company_id: currentCompany.value?.id || '' }
        if (filters.start_date) params.start_date = filters.start_date
        if (filters.end_date) params.end_date = filters.end_date
        const { data } = await api.get(`/ledger/account/${account.account_id}/entries/`, { params })
        const rawEntries = data.entries || []
        // Crear fila de saldo inicial
        const openingDebit = Number(data.initial_debit_balance || 0)
        const openingCredit = Number(data.initial_credit_balance || 0)
        const openingDate = filters.start_date ? new Date(filters.start_date) : (rawEntries[0]?.date ? new Date(rawEntries[0].date) : new Date())
        const openingRow = {
          id: 'opening-balance-inline-' + account.account_id,
          account_id: account.account_id,
          account_code: account.account_code,
          account_name: account.account_name,
          company_id: params.company_id,
          entry_type: 'opening',
          journal_entry_id: null,
          date: openingDate,
          description: 'Saldo inicial',
          reference: '-',
          debit_amount: 0,
          credit_amount: 0,
          running_debit_balance: openingDebit,
          running_credit_balance: openingCredit,
          created_at: openingDate,
          created_by: ''
        }
        state.entries = [openingRow, ...rawEntries]
      } catch (e) {
        console.error('Error loading inline account ledger:', e)
        state.entries = []
      } finally {
        state.loading = false
        expanded.value = { ...expanded.value }
      }
    }

    const toggleExpand = async (account) => {
      if (!account || !account.account_id) return
      const state = expanded.value[account.account_id] || { open: false, loading: false, entries: [] }
      state.open = !state.open
      expanded.value[account.account_id] = state
      expanded.value = { ...expanded.value }
      if (state.open && state.entries.length === 0) {
        await fetchExpandedEntries(account)
      }
    }

    // Re-aplicar filtros de fecha al contenido expandido
    watch(() => [filters.start_date, filters.end_date], async () => {
      const openAccounts = Object.keys(expanded.value).filter(id => expanded.value[id]?.open)
      if (openAccounts.length === 0) return
      // mapa rápido por id
      const byId = ledger.value.reduce((acc, a) => { acc[a.account_id] = a; return acc }, {})
      for (const id of openAccounts) {
        const acc = byId[id]
        if (acc) await fetchExpandedEntries(acc)
      }
    })

    const openAccountLedgerByCode = (accountCode) => {
      if (!accountCode) return
      // Cerrar modal de detalle de asiento si está abierto
      const entryModal = document.getElementById('entryDetailModal')
      if (entryModal) {
        if (window.bootstrap && window.bootstrap.Modal) {
          const instance = window.bootstrap.Modal.getInstance(entryModal)
          if (instance) instance.hide()
        } else {
          entryModal.classList.remove('show')
          entryModal.style.display = 'none'
          entryModal.setAttribute('aria-hidden', 'true')
          document.body.classList.remove('modal-open')
          const backdrop = document.getElementById('entryDetailModal-backdrop')
          if (backdrop) backdrop.remove()
        }
      }
      const account = ledger.value.find(a => a.account_code === accountCode)
      if (account) {
        viewAccountLedger(account)
      } else {
        toast.error(`Cuenta ${accountCode} no encontrada en el resumen cargado`)
      }
    }

    const printSelected = () => {
      printElement('#accountLedgerModal .modal-content', `Mayor de Cuenta ${selectedAccount.value?.account_code || ''}`)
    }

    const viewEntryDetails = (entry) => {
      // Abre el modal reutilizable con detalles del asiento
      // Creamos un objeto de entrada compatible con EntryDetailModal
      const normalized = {
        entry_number: entry.entry_number,
        entry_type: entry.entry_type,
        date: entry.date,
        description: entry.description,
        lines: entry.lines
      }
      selectedEntryForModal.value = normalized
      const el = document.getElementById('entryDetailModal')
      if (el) {
        if (window.bootstrap && window.bootstrap.Modal) {
          const modal = new window.bootstrap.Modal(el)
          modal.show()
        } else {
          el.classList.add('show')
          el.style.display = 'block'
          el.setAttribute('aria-hidden', 'false')
          document.body.classList.add('modal-open')
          const backdrop = document.createElement('div')
          backdrop.className = 'modal-backdrop fade show'
          backdrop.id = 'entryDetailModal-backdrop'
          document.body.appendChild(backdrop)
        }
      }
    }

    const getAccountTypeColor = (type) => {
      const colors = {
        activo: 'primary',
        pasivo: 'success',
        patrimonio: 'info',
        ingresos: 'warning',
        gastos: 'danger',
        costos: 'secondary'
      }
      return colors[type] || 'secondary'
    }

    const formatDate = (date) => {
      if (!date) return 'N/A'
      return new Intl.DateTimeFormat('es-EC', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      }).format(new Date(date))
    }

    const formatCurrency = (amount) => {
      return new Intl.NumberFormat('es-EC', {
        style: 'currency',
        currency: 'USD'
      }).format(amount)
    }

    // Hierarchical methods
    const getRelationshipType = (account) => {
      const hasChildren = ledger.value.some(acc => acc.parent_code === account.account_code)
      return hasChildren ? 'P' : 'H'
    }

    const getRelationshipClass = (account) => {
      const hasChildren = ledger.value.some(acc => acc.parent_code === account.account_code)
      return hasChildren ? 'bg-info' : 'bg-secondary'
    }

    const getAccountRowClass = (account) => {
      const hasChildren = ledger.value.some(acc => acc.parent_code === account.account_code)
      return hasChildren ? 'table-info' : ''
    }

    // Lifecycle
    onMounted(() => {
      loadLedger()
      
      // Si hay parámetros de query para abrir una cuenta específica
      const urlParams = new URLSearchParams(window.location.search)
      const accountParam = urlParams.get('account')
      if (accountParam) {
        // Buscar la cuenta en el ledger cargado por ID o código
        setTimeout(() => {
          const account = ledger.value.find(acc => 
            acc.account_id === accountParam || acc.account_code === accountParam
          )
          if (account) {
            viewAccountLedger(account)
          }
        }, 1000) // Esperar a que se cargue el ledger
      }
    })

    return {
      ledger,
      ledgerEntries,
      summary,
      selectedAccount,
      expanded,
      loading,
      calculatingBalances,
      fixingHierarchy,
      filters,
      filteredLedger,
      filteredLedgerEntries,
      showAccountSummary,
      loadLedger,
      fixCompleteHierarchy,
      viewAccountLedger,
      viewEntryDetails,
      closeModal,
      exportLedger,
      clearFilters,
      toggleView,
      isExpanded,
      toggleExpand,
      openAccountLedgerByCode,
      printSelected,
      selectedEntryForModal,
      initialNet,
      actualNet,
      netClass,
      getAccountTypeColor,
      formatDate,
      formatCurrency,
      getRelationshipType,
      getRelationshipClass,
      getAccountRowClass,
      expandAll,
      collapseAll,
      // Asientos
      entriesExpanded,
      isEntryExpanded,
      toggleExpandEntry,
      expandAllEntries,
      collapseAllEntries
    }
  }
}
</script>

<style scoped>
.card {
  transition: transform 0.2s ease;
}

.card:hover {
  transform: translateY(-2px);
}

.table th {
  font-weight: 600;
  background-color: #f8f9fc;
}

.badge {
  font-size: 0.75rem;
}

.modal-xl {
  max-width: 90%;
}
</style>

 


