<template>
  <div class="user-form-page">
    <!-- Page Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h1 class="h3 mb-0">
          {{ isEdit ? 'Editar Usuario' : 'Nuevo Usuario' }}
        </h1>
        <p class="text-muted">
          {{ isEdit ? 'Modifica la información del usuario' : 'Crea un nuevo usuario en el sistema' }}
        </p>
      </div>
      <div>
        <router-link to="/users" class="btn btn-outline-secondary">
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
                    <label for="username" class="form-label">Usuario *</label>
                    <input
                      type="text"
                      class="form-control"
                      id="username"
                      v-model="form.username"
                      :class="{ 'is-invalid': errors.username }"
                      :disabled="isEdit"
                      required
                    />
                    <div class="invalid-feedback" v-if="errors.username">
                      {{ errors.username }}
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
                <div class="col-md-6">
                  <div class="mb-3">
                    <label for="first_name" class="form-label">Nombre *</label>
                    <input
                      type="text"
                      class="form-control"
                      id="first_name"
                      v-model="form.first_name"
                      :class="{ 'is-invalid': errors.first_name }"
                      required
                    />
                    <div class="invalid-feedback" v-if="errors.first_name">
                      {{ errors.first_name }}
                    </div>
                  </div>
                </div>
                <div class="col-md-6">
                  <div class="mb-3">
                    <label for="last_name" class="form-label">Apellido *</label>
                    <input
                      type="text"
                      class="form-control"
                      id="last_name"
                      v-model="form.last_name"
                      :class="{ 'is-invalid': errors.last_name }"
                      required
                    />
                    <div class="invalid-feedback" v-if="errors.last_name">
                      {{ errors.last_name }}
                    </div>
                  </div>
                </div>
              </div>

              <div class="row">
                <div class="col-md-6">
                  <div class="mb-3">
                    <label for="role" class="form-label">Rol *</label>
                    <select
                      class="form-select"
                      id="role"
                      v-model="form.role"
                      :class="{ 'is-invalid': errors.role }"
                      required
                    >
                      <option value="">Seleccionar rol</option>
                      <option value="admin">Administrador</option>
                      <option value="contador">Contador</option>
                      <option value="auditor">Auditor</option>
                      <option value="interno">Interno</option>
                    </select>
                    <div class="invalid-feedback" v-if="errors.role">
                      {{ errors.role }}
                    </div>
                  </div>
                </div>
                <div class="col-md-6">
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

              <div v-if="!isEdit" class="mb-3">
                <label for="password" class="form-label">Contraseña *</label>
                <input
                  type="password"
                  class="form-control"
                  id="password"
                  v-model="form.password"
                  :class="{ 'is-invalid': errors.password }"
                  required
                />
                <div class="invalid-feedback" v-if="errors.password">
                  {{ errors.password }}
                </div>
              </div>

              <div class="mb-3">
                <label class="form-label">Empresas</label>
                <div class="row">
                  <div
                    v-for="company in availableCompanies"
                    :key="company.id"
                    class="col-md-6 mb-2"
                  >
                    <div class="form-check">
                      <input
                        class="form-check-input"
                        type="checkbox"
                        :id="`company-${company.id}`"
                        :value="company.id"
                        v-model="form.companies"
                      />
                      <label class="form-check-label" :for="`company-${company.id}`">
                        {{ company.name }}
                      </label>
                    </div>
                  </div>
                </div>
              </div>

              <div class="d-flex justify-content-end gap-2">
                <router-link to="/users" class="btn btn-secondary">
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
  name: 'UserForm',
  setup() {
    const route = useRoute()
    const router = useRouter()
    const toast = useToast()

    // State
    const loading = ref(false)
    const availableCompanies = ref([])

    const form = reactive({
      username: '',
      email: '',
      first_name: '',
      last_name: '',
      role: '',
      status: 'active',
      password: '',
      companies: []
    })

    const errors = reactive({})

    // Computed
    const isEdit = computed(() => !!route.params.id)

    // Methods
    const loadCompanies = async () => {
      try {
        const response = await api.get('/companies')
        availableCompanies.value = response.data
      } catch (error) {
        console.error('Error loading companies:', error)
        toast.error('Error al cargar empresas')
      }
    }

    const loadUser = async () => {
      if (!isEdit.value) return

      loading.value = true
      try {
        const response = await api.get(`/users/${route.params.id}`)
        const user = response.data
        
        form.username = user.username
        form.email = user.email
        form.first_name = user.first_name
        form.last_name = user.last_name
        form.role = user.role
        form.status = user.status
        form.companies = user.companies || []
      } catch (error) {
        console.error('Error loading user:', error)
        toast.error('Error al cargar usuario')
        router.push('/users')
      } finally {
        loading.value = false
      }
    }

    const validateForm = () => {
      // Clear previous errors
      Object.keys(errors).forEach(key => delete errors[key])

      if (!form.username.trim()) {
        errors.username = 'El usuario es requerido'
      }

      if (!form.email.trim()) {
        errors.email = 'El email es requerido'
      } else if (!/\S+@\S+\.\S+/.test(form.email)) {
        errors.email = 'El email no es válido'
      }

      if (!form.first_name.trim()) {
        errors.first_name = 'El nombre es requerido'
      }

      if (!form.last_name.trim()) {
        errors.last_name = 'El apellido es requerido'
      }

      if (!form.role) {
        errors.role = 'El rol es requerido'
      }

      if (!isEdit.value && !form.password) {
        errors.password = 'La contraseña es requerida'
      }

      return Object.keys(errors).length === 0
    }

    const handleSubmit = async () => {
      if (!validateForm()) {
        return
      }

      loading.value = true
      try {
        const data = { ...form }
        
        if (isEdit.value) {
          // Remove password from update if empty
          if (!data.password) {
            delete data.password
          }
          await api.put(`/users/${route.params.id}`, data)
          toast.success('Usuario actualizado exitosamente')
        } else {
          await api.post('/users', data)
          toast.success('Usuario creado exitosamente')
        }
        
        router.push('/users')
      } catch (error) {
        console.error('Error saving user:', error)
        toast.error(error.response?.data?.detail || 'Error al guardar usuario')
      } finally {
        loading.value = false
      }
    }

    // Lifecycle
    onMounted(async () => {
      await loadCompanies()
      await loadUser()
    })

    return {
      form,
      errors,
      loading,
      isEdit,
      availableCompanies,
      handleSubmit
    }
  }
}
</script>

<style scoped>
.form-check-input:checked {
  background-color: #4e73df;
  border-color: #4e73df;
}

.btn {
  min-width: 120px;
}

.spinner-border-sm {
  width: 1rem;
  height: 1rem;
}
</style>










