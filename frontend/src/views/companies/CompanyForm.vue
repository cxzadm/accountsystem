<template>
  <div class="company-form-page">
    <!-- Page Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h1 class="h3 mb-0">
          {{ isEdit ? 'Editar Empresa' : 'Nueva Empresa' }}
        </h1>
        <p class="text-muted">
          {{ isEdit ? 'Modifica la información de la empresa' : 'Registra una nueva empresa en el sistema' }}
        </p>
      </div>
      <div>
        <router-link to="/companies" class="btn btn-outline-secondary">
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
                    <label for="name" class="form-label">Nombre de la Empresa *</label>
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
                </div>
                <div class="col-md-6">
                  <div class="mb-3">
                    <label for="ruc" class="form-label">RUC *</label>
                    <input
                      type="text"
                      class="form-control"
                      id="ruc"
                      v-model="form.ruc"
                      :class="{ 'is-invalid': errors.ruc }"
                      required
                    />
                    <div class="invalid-feedback" v-if="errors.ruc">
                      {{ errors.ruc }}
                    </div>
                  </div>
                </div>
              </div>

              <div class="mb-3">
                <label for="legal_name" class="form-label">Razón Social *</label>
                <input
                  type="text"
                  class="form-control"
                  id="legal_name"
                  v-model="form.legal_name"
                  :class="{ 'is-invalid': errors.legal_name }"
                  required
                />
                <div class="invalid-feedback" v-if="errors.legal_name">
                  {{ errors.legal_name }}
                </div>
              </div>

              <div class="mb-3">
                <label for="address" class="form-label">Dirección *</label>
                <textarea
                  class="form-control"
                  id="address"
                  v-model="form.address"
                  :class="{ 'is-invalid': errors.address }"
                  rows="3"
                  required
                ></textarea>
                <div class="invalid-feedback" v-if="errors.address">
                  {{ errors.address }}
                </div>
              </div>

              <div class="row">
                <div class="col-md-6">
                  <div class="mb-3">
                    <label for="phone" class="form-label">Teléfono *</label>
                    <input
                      type="tel"
                      class="form-control"
                      id="phone"
                      v-model="form.phone"
                      :class="{ 'is-invalid': errors.phone }"
                      required
                    />
                    <div class="invalid-feedback" v-if="errors.phone">
                      {{ errors.phone }}
                    </div>
                  </div>
                </div>
                <div class="col-md-6">
                  <div class="mb-3">
                    <label for="email" class="form-label">Email *</label>
                    <input
                      type="email"
                      class="form-control"
                      id="email"
                      v-model="form.email"
                      :class="{ 'is-invalid': errors.email }"
                      required
                    />
                    <div class="invalid-feedback" v-if="errors.email">
                      {{ errors.email }}
                    </div>
                  </div>
                </div>
              </div>

              <div class="row">
                <div class="col-md-4">
                  <div class="mb-3">
                    <label for="fiscal_year_start" class="form-label">Inicio Año Fiscal</label>
                    <select
                      class="form-select"
                      id="fiscal_year_start"
                      v-model="form.fiscal_year_start"
                      :class="{ 'is-invalid': errors.fiscal_year_start }"
                    >
                      <option value="1">Enero</option>
                      <option value="2">Febrero</option>
                      <option value="3">Marzo</option>
                      <option value="4">Abril</option>
                      <option value="5">Mayo</option>
                      <option value="6">Junio</option>
                      <option value="7">Julio</option>
                      <option value="8">Agosto</option>
                      <option value="9">Septiembre</option>
                      <option value="10">Octubre</option>
                      <option value="11">Noviembre</option>
                      <option value="12">Diciembre</option>
                    </select>
                    <div class="invalid-feedback" v-if="errors.fiscal_year_start">
                      {{ errors.fiscal_year_start }}
                    </div>
                  </div>
                </div>
                <div class="col-md-4">
                  <div class="mb-3">
                    <label for="currency" class="form-label">Moneda</label>
                    <select
                      class="form-select"
                      id="currency"
                      v-model="form.currency"
                      :class="{ 'is-invalid': errors.currency }"
                    >
                      <option value="USD">USD - Dólar Americano</option>
                      <option value="EUR">EUR - Euro</option>
                    </select>
                    <div class="invalid-feedback" v-if="errors.currency">
                      {{ errors.currency }}
                    </div>
                  </div>
                </div>
                <div class="col-md-4">
                  <div class="mb-3">
                    <label for="status" class="form-label">Estado</label>
                    <select
                      class="form-select"
                      id="status"
                      v-model="form.status"
                      :class="{ 'is-invalid': errors.status }"
                    >
                      <option value="active">Activo</option>
                      <option value="inactive">Inactivo</option>
                      <option value="suspended">Suspendido</option>
                    </select>
                    <div class="invalid-feedback" v-if="errors.status">
                      {{ errors.status }}
                    </div>
                  </div>
                </div>
              </div>

              <div class="d-flex justify-content-end gap-2">
                <router-link to="/companies" class="btn btn-secondary">
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
import api from '@/services/api'

export default {
  name: 'CompanyForm',
  setup() {
    const route = useRoute()
    const router = useRouter()
    const toast = useToast()

    // State
    const loading = ref(false)

    const form = reactive({
      name: '',
      ruc: '',
      legal_name: '',
      address: '',
      phone: '',
      email: '',
      fiscal_year_start: 1,
      currency: 'USD',
      status: 'active'
    })

    const errors = reactive({})

    // Computed
    const isEdit = computed(() => !!route.params.id)

    // Methods
    const loadCompany = async () => {
      if (!isEdit.value) return

      loading.value = true
      try {
        const response = await api.get(`/companies/${route.params.id}`)
        const company = response.data
        
        form.name = company.name
        form.ruc = company.ruc
        form.legal_name = company.legal_name
        form.address = company.address
        form.phone = company.phone
        form.email = company.email
        form.fiscal_year_start = company.fiscal_year_start
        form.currency = company.currency
        form.status = company.status
      } catch (error) {
        console.error('Error loading company:', error)
        toast.error('Error al cargar empresa')
        router.push('/companies')
      } finally {
        loading.value = false
      }
    }

    const validateForm = () => {
      // Clear previous errors
      Object.keys(errors).forEach(key => delete errors[key])

      if (!form.name.trim()) {
        errors.name = 'El nombre es requerido'
      }

      if (!form.ruc.trim()) {
        errors.ruc = 'El RUC es requerido'
      } else if (!/^\d{13}$/.test(form.ruc.replace(/-/g, ''))) {
        errors.ruc = 'El RUC debe tener 13 dígitos'
      }

      if (!form.legal_name.trim()) {
        errors.legal_name = 'La razón social es requerida'
      }

      if (!form.address.trim()) {
        errors.address = 'La dirección es requerida'
      }

      if (!form.phone.trim()) {
        errors.phone = 'El teléfono es requerido'
      }

      if (!form.email.trim()) {
        errors.email = 'El email es requerido'
      } else if (!/\S+@\S+\.\S+/.test(form.email)) {
        errors.email = 'El email no es válido'
      }

      return Object.keys(errors).length === 0
    }

    const handleSubmit = async () => {
      if (!validateForm()) {
        return
      }

      loading.value = true
      try {
        if (isEdit.value) {
          await api.put(`/companies/${route.params.id}`, form)
          toast.success('Empresa actualizada exitosamente')
        } else {
          await api.post('/companies', form)
          toast.success('Empresa creada exitosamente')
        }
        
        router.push('/companies')
      } catch (error) {
        console.error('Error saving company:', error)
        toast.error(error.response?.data?.detail || 'Error al guardar empresa')
      } finally {
        loading.value = false
      }
    }

    // Lifecycle
    onMounted(async () => {
      await loadCompany()
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
</style>






