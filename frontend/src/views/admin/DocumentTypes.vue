<template>
  <div class="document-types-page">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h1 class="h3 mb-0">Tipos de Documentos Contables</h1>
        <p class="text-muted">Administra la numeración y parámetros</p>
      </div>
      <div>
        <button class="btn btn-outline-warning me-2" @click="resetAllNumbers" :disabled="loading">
          <i class="fas fa-undo me-2"></i>
          Reiniciar Números
        </button>
        <button class="btn btn-primary" @click="openForm()">
          <i class="fas fa-plus me-2"></i>
          Nuevo Tipo
        </button>
      </div>
    </div>

    <div class="card">
      <div class="card-body">
        <div class="table-responsive">
          <table class="table table-hover">
            <thead>
              <tr>
                <th>Código</th>
                <th>Nombre</th>
                <th>Último Número</th>
                <th>Est.-Pto</th>
                <th>Tipo Comp.</th>
                <th>Electrónico</th>
                <th>Activo</th>
                <th></th>
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
              <tr v-else-if="items.length === 0">
                <td colspan="8" class="text-center py-4 text-muted">No hay tipos de documentos</td>
              </tr>
              <tr v-else v-for="doc in items" :key="doc.id">
                <td><code>{{ doc.code }}</code></td>
                <td>{{ doc.name }}</td>
                <td><code>{{ doc.control_number || formatNext(doc) }}</code></td>
                <td>{{ doc.establishment_point || '-' }}</td>
                <td>{{ doc.receipt_type || '-' }}</td>
                <td>
                  <span :class="`badge bg-${doc.is_electronic ? 'success' : 'secondary'}`">
                    {{ doc.is_electronic ? 'Sí' : 'No' }}
                  </span>
                </td>
                <td>
                  <span :class="`badge bg-${doc.is_active ? 'success' : 'secondary'}`">
                    {{ doc.is_active ? 'Activo' : 'Inactivo' }}
                  </span>
                </td>
                <td class="text-end">
                  <div class="btn-group">
                    <button class="btn btn-sm btn-outline-secondary" @click="reserveNext(doc)" title="Reservar siguiente número">
                      <i class="fas fa-hashtag"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-warning" @click="openForm(doc)" title="Editar">
                      <i class="fas fa-edit"></i>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Modal Form -->
    <div class="modal fade" id="docTypeModal" tabindex="-1" aria-hidden="true">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ editItem ? 'Editar Tipo' : 'Nuevo Tipo' }}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="save">
              <div class="row g-3">
                <div class="col-md-3">
                  <label class="form-label">Código *</label>
                  <input class="form-control" v-model="form.code" :disabled="!!editItem" required />
                </div>
                <div class="col-md-9">
                  <label class="form-label">Nombre *</label>
                  <input class="form-control" v-model="form.name" required />
                </div>
                <div class="col-md-4">
                  <label class="form-label">Establecimiento - Punto</label>
                  <input class="form-control" v-model="form.establishment_point" placeholder="001-001" />
                </div>
                <div class="col-md-4">
                  <label class="form-label">Tipo de Comprobante</label>
                  <input class="form-control" v-model="form.receipt_type" placeholder="7" />
                </div>
                <div class="col-md-4">
                  <label class="form-label">Padding</label>
                  <input type="number" min="1" class="form-control" v-model.number="form.padding" />
                </div>
                <div class="col-md-3">
                  <label class="form-label">Mov. Bancos</label>
                  <select class="form-select" v-model="form.bank_movement">
                    <option value="">-</option>
                    <option value="D">D (Débito)</option>
                    <option value="C">C (Crédito)</option>
                  </select>
                </div>
                <div class="col-md-3">
                  <label class="form-label">Mov. Clientes</label>
                  <select class="form-select" v-model="form.customer_movement">
                    <option value="">-</option>
                    <option value="D">D (Débito)</option>
                    <option value="C">C (Crédito)</option>
                  </select>
                </div>
                <div class="col-md-3">
                  <label class="form-label">Mov. Proveedores</label>
                  <select class="form-select" v-model="form.supplier_movement">
                    <option value="">-</option>
                    <option value="D">D (Débito)</option>
                    <option value="C">C (Crédito)</option>
                  </select>
                </div>
                <div class="col-md-3">
                  <label class="form-label">Mov. Productos</label>
                  <select class="form-select" v-model="form.product_movement">
                    <option value="">-</option>
                    <option value="I">I (Ingreso)</option>
                    <option value="E">E (Egreso)</option>
                  </select>
                </div>
                <div class="col-md-3">
                  <label class="form-label">Documento Electrónico</label>
                  <select class="form-select" v-model.boolean="form.is_electronic">
                    <option :value="false">No</option>
                    <option :value="true">Sí</option>
                  </select>
                </div>
                <div class="col-md-3">
                  <label class="form-label">Responsable (Código)</label>
                  <input class="form-control" v-model="form.responsible_code" placeholder="BFC" />
                </div>
                <div class="col-md-6">
                  <label class="form-label">Responsable (Nombre)</label>
                  <input class="form-control" v-model="form.responsible_name" placeholder="BRYAM CABRERA" />
                </div>
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cerrar</button>
            <button type="button" class="btn btn-primary" :disabled="saving" @click="save()">
              <span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>
              {{ saving ? 'Guardando...' : 'Guardar' }}
            </button>
          </div>
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
  name: 'DocumentTypes',
  setup() {
    const toast = useToast()
    const companyStore = useCompanyStore()

    const items = ref([])
    const loading = ref(false)
    const saving = ref(false)
    const editItem = ref(null)
    const form = reactive({
      code: '',
      name: '',
      establishment_point: '',
      receipt_type: '',
      bank_movement: '',
      customer_movement: '',
      supplier_movement: '',
      product_movement: '',
      is_electronic: false,
      responsible_code: '',
      responsible_name: '',
      padding: 5
    })

    const currentCompany = computed(() => companyStore.getCurrentCompany())

    const load = async () => {
      if (!currentCompany.value) {
        toast.error('Selecciona una empresa primero')
        return
      }
      loading.value = true
      try {
        const { data } = await api.get('/document-types/', { params: { company_id: currentCompany.value.id } })
        items.value = data
      } catch (e) {
        console.error(e)
        toast.error('Error al cargar tipos de documentos')
      } finally {
        loading.value = false
      }
    }

    const openForm = (doc = null) => {
      editItem.value = doc
      if (doc) {
        Object.assign(form, {
          code: doc.code,
          name: doc.name,
          establishment_point: doc.establishment_point || '',
          receipt_type: doc.receipt_type || '',
          bank_movement: doc.bank_movement || '',
          customer_movement: doc.customer_movement || '',
          supplier_movement: doc.supplier_movement || '',
          product_movement: doc.product_movement || '',
          is_electronic: !!doc.is_electronic,
          responsible_code: doc.responsible_code || '',
          responsible_name: doc.responsible_name || '',
          padding: doc.padding || 5
        })
      } else {
        Object.assign(form, {
          code: '', name: '', establishment_point: '', receipt_type: '', bank_movement: '', customer_movement: '', supplier_movement: '', product_movement: '', is_electronic: false, responsible_code: '', responsible_name: '', padding: 5
        })
      }

      setTimeout(() => {
        const el = document.getElementById('docTypeModal')
        if (!el) return
        if (window.bootstrap && window.bootstrap.Modal) {
          const modal = new window.bootstrap.Modal(el)
          modal.show()
        } else {
          el.classList.add('show'); el.style.display = 'block'; el.removeAttribute('aria-hidden');
        }
      }, 0)
    }

    const closeForm = () => {
      const el = document.getElementById('docTypeModal')
      if (!el) return
      if (window.bootstrap && window.bootstrap.Modal) {
        const instance = window.bootstrap.Modal.getInstance(el)
        if (instance) instance.hide()
      } else {
        el.classList.remove('show'); el.style.display = 'none'; el.setAttribute('aria-hidden', 'true')
      }
    }

    const save = async () => {
      if (!currentCompany.value) {
        toast.error('Selecciona una empresa primero')
        return
      }
      if (!form.code.trim() || !form.name.trim()) {
        toast.error('Código y nombre son requeridos')
        return
      }
      saving.value = true
      try {
        if (editItem.value) {
          const { data } = await api.put(`/document-types/${editItem.value.id}`, form)
          const idx = items.value.findIndex(i => i.id === editItem.value.id)
          if (idx !== -1) items.value[idx] = data
          toast.success('Tipo actualizado')
        } else {
          const { data } = await api.post('/document-types/', form, { params: { company_id: currentCompany.value.id } })
          items.value.push(data)
          toast.success('Tipo creado')
        }
        closeForm()
      } catch (e) {
        console.error(e)
        toast.error(e.response?.data?.detail || 'Error al guardar')
      } finally {
        saving.value = false
      }
    }

    const reserveNext = async (doc) => {
      try {
        const { data } = await api.post(`/document-types/${doc.id}/next-number`)
        toast.success(`Reservado: ${data.number}`)
        // refrescar control_number/sequence localmente
        const idx = items.value.findIndex(i => i.id === doc.id)
        if (idx !== -1) items.value[idx].control_number = data.number
      } catch (e) {
        console.error(e)
        toast.error('Error al reservar número')
      }
    }

    const formatNext = (doc) => {
      const seq = doc.next_sequence || 1
      const pad = parseInt(doc.padding || 5)
      return `${doc.code}-${String(seq).padStart(pad, '0')}`
    }

    const resetAllNumbers = async () => {
      if (!currentCompany.value) {
        toast.error('Selecciona una empresa primero')
        return
      }
      
      if (!confirm('¿Estás seguro de reiniciar TODOS los números de documentos? Esta acción no se puede deshacer.')) {
        return
      }

      if (!confirm('CONFIRMACIÓN FINAL: Esto reiniciará la numeración de todos los tipos de documentos. ¿Continuar?')) {
        return
      }

      loading.value = true
      try {
        await api.post('/document-types/reset-numbers/', {}, {
          params: { company_id: currentCompany.value.id }
        })
        toast.success('Números reiniciados exitosamente')
        await load()
      } catch (e) {
        console.error(e)
        toast.error('Error al reiniciar números')
      } finally {
        loading.value = false
      }
    }

    onMounted(load)

    return { items, loading, saving, editItem, form, openForm, save, reserveNext, formatNext, resetAllNumbers }
  }
}
</script>

<style scoped>
.table th {
  border-top: none;
  font-weight: 600;
}
</style>



