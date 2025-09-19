<template>
  <div class="account-form-page">
    <!-- Page Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h1 class="h3 mb-0">
          {{ isEdit ? 'Editar Cuenta' : 'Nueva Cuenta' }}
        </h1>
        <p class="text-muted">
          {{ isEdit ? 'Modifica la información de la cuenta contable' : 'Crea una nueva cuenta en el plan contable' }}
        </p>
      </div>
      <div>
        <router-link to="/accounts" class="btn btn-outline-secondary">
          <i class="fas fa-arrow-left me-2"></i>
          Volver
        </router-link>
      </div>
    </div>

    <!-- Form -->
    <div class="row justify-content-center">
      <div class="col-md-8">
        <div class="card">
          <div class="card-body">
            <form @submit.prevent="handleSubmit">
              <div class="row">
                <div class="col-md-6">
                  <div class="mb-3">
                    <label for="code" class="form-label">Código de Cuenta *</label>
                    <input
                      type="text"
                      class="form-control"
                      id="code"
                      v-model="form.code"
                      :class="{ 'is-invalid': errors.code }"
                      :disabled="isEdit"
                      required
                    />
                    <div class="invalid-feedback" v-if="errors.code">
                      {{ errors.code }}
                    </div>
                    <div class="form-text">
                      Ejemplo: 1101, 2101, 3101, etc.
                    </div>
                  </div>
                </div>
                <div class="col-md-6">
                  <div class="mb-3">
                    <label for="level" class="form-label">Nivel</label>
                    <input
                      type="number"
                      class="form-control"
                      id="level"
                      v-model="form.level"
                      :class="{ 'is-invalid': errors.level }"
                      min="1"
                      max="5"
                    />
                    <div class="invalid-feedback" v-if="errors.level">
                      {{ errors.level }}
                    </div>
                  </div>
                </div>
              </div>

              <div class="mb-3">
                <label for="name" class="form-label">Nombre de la Cuenta *</label>
                <input
                  type="text"
                  class="form-control"
                  id="name"
                  v-model="form.name"
                  :class="{ 'is-invalid': errors.name }"
                  required
                />
                <div class="invalid-feedback" v-if="errors.name">
                  {{ errors.name }}
                </div>
              </div>

              <div class="mb-3">
                <label for="description" class="form-label">Descripción</label>
                <textarea
                  class="form-control"
                  id="description"
                  v-model="form.description"
                  :class="{ 'is-invalid': errors.description }"
                  rows="3"
                ></textarea>
                <div class="invalid-feedback" v-if="errors.description">
                  {{ errors.description }}
                </div>
              </div>

              <div class="row">
                <div class="col-md-6">
                  <div class="mb-3">
                    <label for="account_type" class="form-label">Tipo de Cuenta *</label>
                    <select
                      class="form-select"
                      id="account_type"
                      v-model="form.account_type"
                      :class="{ 'is-invalid': errors.account_type }"
                      required
                    >
                      <option value="">Seleccionar tipo</option>
                      <option value="activo">Activo</option>
                      <option value="pasivo">Pasivo</option>
                      <option value="patrimonio">Patrimonio</option>
                      <option value="ingresos">Ingresos</option>
                      <option value="gastos">Gastos</option>
                      <option value="costos">Costos</option>
                    </select>
                    <div class="invalid-feedback" v-if="errors.account_type">
                      {{ errors.account_type }}
                    </div>
                  </div>
                </div>
                <div class="col-md-6">
                  <div class="mb-3">
                    <label for="nature" class="form-label">Naturaleza *</label>
                    <select
                      class="form-select"
                      id="nature"
                      v-model="form.nature"
                      :class="{ 'is-invalid': errors.nature }"
                      required
                    >
                      <option value="">Seleccionar naturaleza</option>
                      <option value="deudora">Deudora</option>
                      <option value="acreedora">Acreedora</option>
                    </select>
                    <div class="invalid-feedback" v-if="errors.nature">
                      {{ errors.nature }}
                    </div>
                  </div>
                </div>
              </div>

              <div class="row">
                <div class="col-md-6">
                  <div class="mb-3">
                    <label for="parent_code" class="form-label">Código Padre</label>
                    <input
                      type="text"
                      class="form-control"
                      id="parent_code"
                      v-model="form.parent_code"
                      :class="{ 'is-invalid': errors.parent_code }"
                    />
                    <div class="invalid-feedback" v-if="errors.parent_code">
                      {{ errors.parent_code }}
                    </div>
                    <div class="form-text">
                      Código de la cuenta padre (opcional)
                    </div>
                  </div>
                </div>
                <div class="col-md-6">
                  <div class="mb-3">
                    <label for="is_editable" class="form-label">Editable</label>
                    <div class="form-check form-switch mt-2">
                      <input
                        class="form-check-input"
                        type="checkbox"
                        id="is_editable"
                        v-model="form.is_editable"
                      />
                      <label class="form-check-label" for="is_editable">
                        Permitir edición
                      </label>
                    </div>
                  </div>
                </div>
              </div>

              <div class="d-flex justify-content-end gap-2">
                <router-link to="/accounts" class="btn btn-secondary">
                  Cancelar
                </router-link>
                <button
                  type="submit"
                  class="btn btn-primary"
                  :disabled="loading"
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
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useToast } from 'vue-toastification'
import { useCompanyStore } from '@/stores/company'
import api from '@/services/api'

export default {
  name: 'AccountForm',
  setup() {
    const route = useRoute()
    const router = useRouter()
    const toast = useToast()
    const companyStore = useCompanyStore()

    // State
    const loading = ref(false)

    const form = reactive({
      code: '',
      name: '',
      description: '',
      account_type: '',
      nature: '',
      parent_code: '',
      level: 1,
      is_editable: true
    })

    const errors = reactive({})

    // Computed
    const isEdit = computed(() => !!route.params.id)
    const currentCompany = computed(() => companyStore.getCurrentCompany())

    // Methods
    const loadAccount = async () => {
      if (!isEdit.value) return

      loading.value = true
      try {
        const response = await api.get(`/accounts/${route.params.id}`)
        const account = response.data
        
        form.code = account.code
        form.name = account.name
        form.description = account.description
        form.account_type = account.account_type
        form.nature = account.nature
        form.parent_code = account.parent_code
        form.level = account.level
        form.is_editable = account.is_editable
      } catch (error) {
        console.error('Error loading account:', error)
        toast.error('Error al cargar cuenta')
        router.push('/accounts')
      } finally {
        loading.value = false
      }
    }

    const validateForm = () => {
      // Clear previous errors
      Object.keys(errors).forEach(key => delete errors[key])

      if (!form.code.trim()) {
        errors.code = 'El código es requerido'
      } else if (!/^\d{4}$/.test(form.code)) {
        errors.code = 'El código debe tener 4 dígitos'
      }

      if (!form.name.trim()) {
        errors.name = 'El nombre es requerido'
      }

      if (!form.account_type) {
        errors.account_type = 'El tipo de cuenta es requerido'
      }

      if (!form.nature) {
        errors.nature = 'La naturaleza es requerida'
      }

      if (form.level < 1 || form.level > 5) {
        errors.level = 'El nivel debe estar entre 1 y 5'
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
        const data = { ...form }
        
        if (isEdit.value) {
          await api.put(`/accounts/${route.params.id}`, data)
          toast.success('Cuenta actualizada exitosamente')
        } else {
          await api.post('/accounts', data, {
            params: { company_id: currentCompany.value.id }
          })
          toast.success('Cuenta creada exitosamente')
        }
        
        router.push('/accounts')
      } catch (error) {
        console.error('Error saving account:', error)
        toast.error(error.response?.data?.detail || 'Error al guardar cuenta')
      } finally {
        loading.value = false
      }
    }

    // Lifecycle
    onMounted(async () => {
      await loadAccount()
    })

    return {
      form,
      errors,
      loading,
      isEdit,
      handleSubmit
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

.form-check-input:checked {
  background-color: #4e73df;
  border-color: #4e73df;
}
</style>










