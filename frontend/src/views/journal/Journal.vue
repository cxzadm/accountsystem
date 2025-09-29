<template>
  <div class="journal-page">
    <!-- Page Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h1 class="h3 mb-0">Diario Contable</h1>
        <p class="text-muted">Gestiona los asientos contables</p>
      </div>
      <div>
        <router-link to="/journal/new" class="btn btn-primary">
          <i class="fas fa-plus me-2"></i>
          Nuevo Asiento
        </router-link>
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
              @change="loadJournalEntries"
            />
          </div>
          <div class="col-md-3">
            <label class="form-label">Fecha Fin</label>
            <input
              type="date"
              class="form-control"
              v-model="filters.end_date"
              @change="loadJournalEntries"
            />
          </div>
          <div class="col-md-2">
            <label class="form-label">Estado</label>
            <select class="form-select" v-model="filters.status" @change="loadJournalEntries">
              <option value="draft">Borrador (Diario)</option>
              <option value="posted">Mayorizado (Mayor)</option>
              <option value="reversed">Reversado</option>
              <option value="reserved">Reservado</option>
              <option value="">Todos</option>
            </select>
          </div>
          <div class="col-md-2">
            <label class="form-label">Tipo</label>
            <select class="form-select" v-model="filters.entry_type" @change="loadJournalEntries">
              <option value="">Todos</option>
              <option value="manual">Manual</option>
              <option value="automatic">Automático</option>
              <option value="adjustment">Ajuste</option>
              <option value="closing">Cierre</option>
            </select>
          </div>
          <div class="col-md-2 d-flex align-items-end">
            <button class="btn btn-outline-secondary w-100" @click="clearFilters">
              <i class="fas fa-times me-1"></i>
              Limpiar
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Info Message for Posted Entries -->
    <div v-if="filters.status === 'posted'" class="alert alert-info mb-4">
      <i class="fas fa-info-circle me-2"></i>
      <strong>Asientos Mayorizados:</strong> Los asientos mayorizados se muestran aquí para referencia. 
      Para ver el detalle completo de los movimientos, ve al <router-link to="/ledger" class="alert-link">Mayor General</router-link>.
    </div>

    <!-- Journal Entries Table -->
    <div class="card">
      <div class="card-body">
        <div class="table-responsive">
          <table class="table table-hover">
            <thead>
              <tr v-if="filters.status !== 'reserved'">
                <th>Número</th>
                <th>Fecha</th>
                <th>Descripción</th>
                <th>Responsable</th>
                <th>Tipo</th>
                <th>Estado</th>
                <th>Débito</th>
                <th>Crédito</th>
                <th>Acciones</th>
              </tr>
              <tr v-else>
                <th>Número</th>
                <th>Código</th>
                <th>Secuencia</th>
                <th>Reservado por</th>
                <th>Fecha Reserva</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="loading">
                <td :colspan="filters.status !== 'reserved' ? 9 : 5" class="text-center py-4">
                  <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Cargando...</span>
                  </div>
                </td>
              </tr>
              <template v-else>
                <template v-if="filters.status !== 'reserved'">
                  <tr v-if="entries.length === 0">
                    <td colspan="9" class="text-center py-4 text-muted">
                      No se encontraron asientos
                    </td>
                  </tr>
                  <tr v-else v-for="entry in entries" :key="entry.id">
                    <td>
                      <code>{{ entry.entry_number }}</code>
                    </td>
                    <td>{{ formatDate(entry.date) }}</td>
                    <td>
                      <div>
                        <strong>{{ entry.description }}</strong>
                        <div class="text-muted small">
                          {{ entry.lines.length }} líneas
                        </div>
                      </div>
                    </td>
                    <td>
                      <span class="badge bg-info">
                        {{ entry.responsable || 'Sin responsable' }}
                      </span>
                    </td>
                    <td>
                      <span :class="`badge bg-${getEntryTypeColor(entry.entry_type)}`">
                        {{ entry.entry_type }}
                      </span>
                    </td>
                    <td>
                      <span :class="`badge bg-${getStatusColor(entry.status)}`">
                        {{ entry.status }}
                      </span>
                    </td>
                    <td class="text-end">
                      <strong class="text-danger">{{ formatCurrency(entry.total_debit) }}</strong>
                    </td>
                    <td class="text-end">
                      <strong class="text-success">{{ formatCurrency(entry.total_credit) }}</strong>
                    </td>
                    <td>
                      <div class="btn-group" role="group">
                        <button class="btn btn-sm btn-outline-primary" @click="viewEntry(entry)" title="Ver">
                          <i class="fas fa-eye"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-warning" @click="editEntry(entry)" title="Editar" :disabled="entry.status === 'posted'">
                          <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-success" @click="postEntry(entry)" title="Mayorizar (Pasar al Mayor)" :disabled="entry.status === 'posted'" v-if="entry.status === 'draft'">
                          <i class="fas fa-check"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-info" @click="viewInLedger(entry)" title="Ver en Mayor General" v-if="entry.status === 'posted'">
                          <i class="fas fa-external-link-alt"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-secondary" @click="unpostEntry(entry)" title="Desmayorizar (Volver a Borrador)" v-if="entry.status === 'posted'">
                          <i class="fas fa-arrow-left"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-primary" @click="copyEntry(entry)" title="Hacer Copia al Diario" v-if="entry.status === 'posted'">
                          <i class="fas fa-copy"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-warning" @click="reverseEntry(entry)" title="Revertir" :disabled="entry.status !== 'posted'" v-if="entry.status === 'posted'">
                          <i class="fas fa-undo"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-danger" @click="deleteEntry(entry)" title="Eliminar" :disabled="entry.status === 'posted'">
                          <i class="fas fa-trash"></i>
                        </button>
                      </div>
                    </td>
                  </tr>
                </template>
                <template v-else>
                  <tr v-if="reservations.length === 0">
                    <td colspan="5" class="text-center py-4 text-muted">No hay reservas</td>
                  </tr>
                  <tr v-else v-for="res in reservations" :key="res.id">
                    <td><code>{{ res.number }}</code></td>
                    <td>{{ res.document_code }}</td>
                    <td>{{ res.sequence }}</td>
                    <td>{{ res.reserved_by || '-' }}</td>
                    <td>
                      <div class="d-flex align-items-center justify-content-between">
                        <span>{{ formatDate(res.reserved_at) }}</span>
                        <button class="btn btn-sm btn-outline-primary" @click="editDraftFromReservation(res)">
                          Editar en borrador
                        </button>
                      </div>
                    </td>
                  </tr>
                </template>
              </template>
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

    <!-- Reusable Entry Detail Modal -->
    <EntryDetailModal modal-id="entryDetailModal" :entry="selectedEntry" @open-account-ledger="openAccountLedger" />
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'vue-toastification'
import { useCompanyStore } from '@/stores/company'
import api from '@/services/api'
import { printElement } from '@/services/print'
import EntryDetailModal from '@/components/EntryDetailModal.vue'
import { alerts } from '@/services/alerts'

export default {
  name: 'Journal',
  components: { EntryDetailModal },
  setup() {
    const router = useRouter()
    const toast = useToast()
    const companyStore = useCompanyStore()

    // State
    const entries = ref([])
    const reservations = ref([])
    const loading = ref(false)
    const currentPage = ref(1)
    const totalPages = ref(1)
    const pageSize = 10
    const selectedEntry = ref(null)

    const filters = reactive({
      start_date: '',
      end_date: '',
      status: 'draft', // Por defecto solo mostrar asientos en borrador
      entry_type: ''
    })

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

    // Methods
    const loadJournalEntries = async () => {
      if (!currentCompany.value) {
        toast.error('Selecciona una empresa primero')
        return
      }

      loading.value = true
      try {
        if (filters.status === 'reserved') {
          const resp = await api.get('/document-reservations', {
            params: { company_id: currentCompany.value.id, status: 'reserved' }
          })
          reservations.value = resp.data
          entries.value = []
          totalPages.value = 1
        } else {
          const params = {
            company_id: currentCompany.value.id,
            skip: (currentPage.value - 1) * pageSize,
            limit: pageSize,
            ...filters
          }
          const response = await api.get('/journal/', { params })
          entries.value = response.data
          reservations.value = []
          totalPages.value = Math.ceil(response.data.length / pageSize)
        }
      } catch (error) {
        console.error('Error loading journal entries:', error)
        toast.error('Error al cargar asientos')
      } finally {
        loading.value = false
      }
    }

    const changePage = (page) => {
      if (page >= 1 && page <= totalPages.value) {
        currentPage.value = page
        loadJournalEntries()
      }
    }

    const clearFilters = () => {
      filters.start_date = ''
      filters.end_date = ''
      filters.status = 'draft' // Mantener filtro por defecto
      filters.entry_type = ''
      currentPage.value = 1
      loadJournalEntries()
    }

    const viewEntry = (entry) => {
      selectedEntry.value = entry
      // Usar el componente modal reutilizable
      setTimeout(() => {
        const el = document.getElementById('entryDetailModal')
        if (!el) return
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
      }, 0)
    }

    const closeViewModal = () => {
      const modalElement = document.getElementById('entryDetailModal')
      if (!modalElement) return
      if (window.bootstrap && window.bootstrap.Modal) {
        const instance = window.bootstrap.Modal.getInstance(modalElement)
        if (instance) instance.hide()
      } else {
        modalElement.classList.remove('show')
        modalElement.style.display = 'none'
        modalElement.setAttribute('aria-hidden', 'true')
        document.body.classList.remove('modal-open')
        const backdrop = document.getElementById('entryDetailModal-backdrop')
        if (backdrop) backdrop.remove()
      }
    }

    const printCurrentEntry = () => {
      printElement('#viewEntryModal .modal-content', `Asiento ${selectedEntry.value?.entry_number}`)
    }

    const printEntry = () => {
      printElement('#entryDetailModal .modal-content', `Asiento ${selectedEntry.value?.entry_number}`)
    }

    const editEntry = (entry) => {
      router.push(`/journal/${entry.id}/edit`)
    }

    const editDraftFromReservation = async (res) => {
      // Crear un asiento en borrador con el número reservado y llevar al editor
      if (!currentCompany.value) {
        toast.error('Selecciona una empresa primero')
        return
      }
      try {
        // Obtener cuentas contables para usar como plantilla
        const accountsResponse = await api.get('/accounts/', { 
          params: { company_id: currentCompany.value.id, limit: 10 } 
        })
        const accounts = accountsResponse.data || []
        
        // Usar cuentas por defecto si están disponibles
        const defaultAccount1 = accounts.find(acc => acc.code === '1101') || accounts[0] || { code: '1101', name: 'Caja' }
        const defaultAccount2 = accounts.find(acc => acc.code === '2101') || accounts[1] || { code: '2101', name: 'Cuentas por Pagar' }
        
        const payload = {
          entry_number: res.number,
          date: new Date().toISOString(),
          description: `Asiento generado desde reserva ${res.number}`,
          entry_type: 'manual',
          document_type_id: res.document_type_id,
          document_type_code: res.document_code,
          lines: [
            { 
              account_code: defaultAccount1.code, 
              account_name: defaultAccount1.name, 
              description: 'Línea 1', 
              debit: 0, 
              credit: 0, 
              reference: '' 
            },
            { 
              account_code: defaultAccount2.code, 
              account_name: defaultAccount2.name, 
              description: 'Línea 2', 
              debit: 0, 
              credit: 0, 
              reference: '' 
            }
          ]
        }
        const response = await api.post('/journal/', payload, { params: { company_id: currentCompany.value.id } })
        toast.success('Borrador creado, redirigiendo...')
        router.push(`/journal/${response.data.id}/edit`)
      } catch (error) {
        console.error('Error creating draft from reservation:', error)
        const msg = error.response?.data?.detail || 'No se pudo crear el borrador'
        toast.error(msg)
      }
    }

    const approveEntry = async (entry) => {
      const ok = await alerts.confirm({
        title: `¿Aprobar asiento ${entry.entry_number}?`,
        text: 'Esta acción marcará el asiento como aprobado.',
        icon: 'question',
        confirmButtonText: 'Aprobar'
      })
      if (ok) {
        try {
          await api.post(`/journal/${entry.id}/approve/`, { approved: true })
          toast.success('Asiento aprobado exitosamente')
          loadJournalEntries()
        } catch (error) {
          console.error('Error approving entry:', error)
          toast.error('Error al aprobar asiento')
        }
      }
    }

    const postEntry = async (entry) => {
      const ok = await alerts.confirm({
        title: `¿Mayorizar asiento ${entry.entry_number}?`,
        text: 'Aplicará las transacciones al mayor de las cuentas.',
        icon: 'warning',
        confirmButtonText: 'Mayorizar'
      })
      if (ok) {
        try {
          await api.post(`/journal/${entry.id}/post/`)
          toast.success('Asiento mayorizado exitosamente')
          loadJournalEntries()
        } catch (error) {
          console.error('Error posting entry:', error)
          toast.error('Error al mayorizar asiento')
        }
      }
    }

    const reverseEntry = async (entry) => {
      const ok = await alerts.confirm({
        title: `¿Revertir asiento ${entry.entry_number}?`,
        text: 'Se creará un asiento de reversión.',
        icon: 'warning',
        confirmButtonText: 'Revertir'
      })
      if (ok) {
        try {
          await api.post(`/journal/${entry.id}/reverse/`)
          toast.success('Asiento revertido exitosamente')
          loadJournalEntries()
        } catch (error) {
          console.error('Error reversing entry:', error)
          toast.error('Error al revertir asiento')
        }
      }
    }

    const deleteEntry = async (entry) => {
      const ok = await alerts.confirm({
        title: `¿Eliminar asiento ${entry.entry_number}?`,
        text: 'Esta acción no se puede deshacer.',
        icon: 'warning',
        confirmButtonText: 'Eliminar'
      })
      if (ok) {
        try {
          await api.delete(`/journal/${entry.id}/`)
          toast.success('Asiento eliminado exitosamente')
          loadJournalEntries()
        } catch (error) {
          console.error('Error deleting entry:', error)
          toast.error('Error al eliminar asiento')
        }
      }
    }

    const viewInLedger = (entry) => {
      router.push('/ledger')
      toast.info('Redirigiendo al Mayor General para ver los movimientos detallados')
    }

    const openAccountLedger = (accountCode) => {
      // Cerrar el modal actual
      closeViewModal()
      
      // Navegar al mayor general con el filtro de cuenta
      router.push({
        path: '/ledger',
        query: { account: accountCode }
      })
      
      toast.info(`Redirigiendo al Mayor General para ver la cuenta ${accountCode}`)
    }

    const unpostEntry = async (entry) => {
      const ok = await alerts.confirm({
        title: `¿Desmayorizar asiento ${entry.entry_number}?`,
        text: 'El asiento volverá al estado de borrador.',
        icon: 'question',
        confirmButtonText: 'Desmayorizar'
      })
      if (ok) {
        try {
          await api.post(`/journal/${entry.id}/unpost/`)
          toast.success('Asiento desmayorizado exitosamente')
          loadJournalEntries()
        } catch (error) {
          console.error('Error unposting entry:', error)
          toast.error('Error al desmayorizar asiento')
        }
      }
    }

    const copyEntry = async (entry) => {
      const ok = await alerts.confirm({
        title: `¿Copiar asiento ${entry.entry_number}?`,
        text: 'Se creará un nuevo asiento en estado borrador.',
        icon: 'question',
        confirmButtonText: 'Copiar'
      })
      if (ok) {
        try {
          const response = await api.post(`/journal/${entry.id}/copy/`)
          toast.success(`Copia creada exitosamente: ${response.data.entry_number}`)
          loadJournalEntries()
        } catch (error) {
          console.error('Error copying entry:', error)
          toast.error('Error al crear copia del asiento')
        }
      }
    }

    const getStatusColor = (status) => {
      const colors = {
        draft: 'secondary',
        posted: 'success',
        reversed: 'warning'
      }
      return colors[status] || 'secondary'
    }

    const getEntryTypeColor = (type) => {
      const colors = {
        manual: 'primary',
        automatic: 'info',
        adjustment: 'warning',
        closing: 'danger'
      }
      return colors[type] || 'secondary'
    }

    const formatDate = (date) => {
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

    // Lifecycle
    onMounted(() => {
      loadJournalEntries()
    })

    return {
      entries,
      reservations,
      loading,
      currentPage,
      totalPages,
      visiblePages,
      filters,
      selectedEntry,
      loadJournalEntries,
      changePage,
      clearFilters,
      viewEntry,
      printEntry,
      closeViewModal,
      printCurrentEntry,
      editEntry,
      approveEntry,
      postEntry,
      reverseEntry,
      deleteEntry,
      viewInLedger,
      openAccountLedger,
      unpostEntry,
      copyEntry,
      editDraftFromReservation,
      getStatusColor,
      getEntryTypeColor,
      formatDate,
      formatCurrency
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

