<template>
  <div class="document-reservations-page">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h1 class="h3 mb-0">Reservas de Números de Documentos</h1>
        <p class="text-muted">Administra y corrige reservas realizadas</p>
      </div>
      <div>
        <router-link to="/companies" class="btn btn-outline-secondary">
          <i class="fas fa-arrow-left me-2"></i>
          Volver
        </router-link>
      </div>
    </div>

    <div class="card mb-3">
      <div class="card-body">
        <div class="row g-3">
          <div class="col-md-3">
            <label class="form-label">Estado</label>
            <select class="form-select" v-model="filters.status" @change="load">
              <option value="reserved">Reservado</option>
            </select>
          </div>
          <div class="col-md-3 d-flex align-items-end">
            <button class="btn btn-outline-secondary" @click="clearFilters">
              Limpiar
            </button>
          </div>
        </div>
      </div>
    </div>

    <div class="card">
      <div class="card-body">
        <div class="table-responsive">
          <table class="table table-hover">
            <thead>
              <tr>
                <th>Número</th>
                <th>Código</th>
                <th>Secuencia</th>
                <th>Estado</th>
                <th>Asiento</th>
                <th>Reservado por</th>
                <th>Fecha Reserva</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="loading">
                <td colspan="8" class="text-center py-4">
                  <div class="spinner-border text-primary"></div>
                </td>
              </tr>
              <tr v-else-if="items.length === 0">
                <td colspan="8" class="text-center py-4 text-muted">
                  No hay reservas
                </td>
              </tr>
              <tr v-else v-for="res in items" :key="res.id">
                <td><code>{{ res.number }}</code></td>
                <td>{{ res.document_code }}</td>
                <td>{{ res.sequence }}</td>
                <td><span class="badge bg-secondary">Reservado</span></td>
                <td>
                  <span v-if="res.journal_entry_id">{{ res.journal_entry_id }}</span>
                  <span v-else class="text-muted">-</span>
                </td>
                <td>{{ res.reserved_by || '-' }}</td>
                <td>{{ formatDate(res.reserved_at) }}</td>
                <td class="text-end">
                  <button class="btn btn-sm btn-outline-primary" @click="update(res)">
                    Guardar
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { useToast } from 'vue-toastification'
import { useCompanyStore } from '@/stores/company'
import api from '@/services/api'

export default {
  name: 'DocumentReservations',
  setup() {
    const toast = useToast()
    const companyStore = useCompanyStore()

    const items = ref([])
    const loading = ref(false)
    const filters = reactive({ status: 'reserved' })

    const currentCompany = computed(() => companyStore.getCurrentCompany())

    const load = async () => {
      if (!currentCompany.value) { toast.error('Selecciona una empresa'); return }
      loading.value = true
      try {
        const { data } = await api.get('/document-reservations', {
          params: { company_id: currentCompany.value.id, status: filters.status || undefined }
        })
        items.value = data
      } catch (e) {
        console.error(e)
        toast.error('Error al cargar reservas')
      } finally {
        loading.value = false
      }
    }

    const update = async (res) => {
      try {
        await api.put(`/document-reservations/${res.id}`, { status: res.status })
        toast.success('Reserva actualizada')
      } catch (e) {
        console.error(e)
        toast.error('Error al actualizar')
      }
    }

    const clearFilters = () => {
      filters.status = ''
      load()
    }

    const formatDate = (date) => {
      return new Intl.DateTimeFormat('es-EC', { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }).format(new Date(date))
    }

    onMounted(load)

    return { items, loading, filters, load, update, clearFilters, formatDate }
  }
}
</script>

<style scoped>
.table th {
  border-top: none;
  font-weight: 600;
}
</style>
