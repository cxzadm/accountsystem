<template>
  <div class="container-fluid">
    <div class="row">
      <div class="col-12">
        <div class="d-flex justify-content-between align-items-center mb-4">
          <h2><i class="fas fa-user me-2"></i>Mi Perfil</h2>
        </div>
      </div>
    </div>

    <div class="row">
      <div class="col-md-8">
        <div class="card">
          <div class="card-header">
            <h5 class="card-title mb-0">Información Personal</h5>
          </div>
          <div class="card-body">
            <form @submit.prevent="updateProfile">
              <div class="row">
                <div class="col-md-6">
                  <div class="mb-3">
                    <label for="firstName" class="form-label">Nombre</label>
                    <input
                      type="text"
                      class="form-control"
                      id="firstName"
                      v-model="profile.first_name"
                      required
                    />
                  </div>
                </div>
                <div class="col-md-6">
                  <div class="mb-3">
                    <label for="lastName" class="form-label">Apellido</label>
                    <input
                      type="text"
                      class="form-control"
                      id="lastName"
                      v-model="profile.last_name"
                      required
                    />
                  </div>
                </div>
              </div>

              <div class="row">
                <div class="col-md-6">
                  <div class="mb-3">
                    <label for="email" class="form-label">Email</label>
                    <input
                      type="email"
                      class="form-control"
                      id="email"
                      v-model="profile.email"
                      required
                    />
                  </div>
                </div>
                <div class="col-md-6">
                  <div class="mb-3">
                    <label for="phone" class="form-label">Teléfono</label>
                    <input
                      type="tel"
                      class="form-control"
                      id="phone"
                      v-model="profile.phone"
                    />
                  </div>
                </div>
              </div>

              <div class="mb-3">
                <label for="role" class="form-label">Rol</label>
                <input
                  type="text"
                  class="form-control"
                  id="role"
                  :value="getRoleName(profile.role)"
                  disabled
                />
              </div>

              <div class="d-flex gap-2">
                <button type="submit" class="btn btn-primary" :disabled="loading">
                  <i class="fas fa-save me-1"></i>
                  {{ loading ? 'Guardando...' : 'Guardar Cambios' }}
                </button>
                <button type="button" class="btn btn-outline-secondary" @click="resetForm">
                  <i class="fas fa-undo me-1"></i>
                  Cancelar
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>

      <div class="col-md-4">
        <div class="card">
          <div class="card-header">
            <h5 class="card-title mb-0">Cambiar Contraseña</h5>
          </div>
          <div class="card-body">
            <form @submit.prevent="changePassword">
              <div class="mb-3">
                <label for="currentPassword" class="form-label">Contraseña Actual</label>
                <input
                  type="password"
                  class="form-control"
                  id="currentPassword"
                  v-model="passwordForm.current_password"
                  required
                />
              </div>

              <div class="mb-3">
                <label for="newPassword" class="form-label">Nueva Contraseña</label>
                <input
                  type="password"
                  class="form-control"
                  id="newPassword"
                  v-model="passwordForm.new_password"
                  required
                  minlength="6"
                />
              </div>

              <div class="mb-3">
                <label for="confirmPassword" class="form-label">Confirmar Nueva Contraseña</label>
                <input
                  type="password"
                  class="form-control"
                  id="confirmPassword"
                  v-model="passwordForm.confirm_password"
                  required
                />
              </div>

              <button type="submit" class="btn btn-warning w-100" :disabled="passwordLoading">
                <i class="fas fa-key me-1"></i>
                {{ passwordLoading ? 'Cambiando...' : 'Cambiar Contraseña' }}
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useToast } from 'vue-toastification'

export default {
  name: 'Profile',
  setup() {
    const authStore = useAuthStore()
    const toast = useToast()
    
    const loading = ref(false)
    const passwordLoading = ref(false)
    
    const profile = ref({
      first_name: '',
      last_name: '',
      email: '',
      phone: '',
      role: ''
    })
    
    const passwordForm = ref({
      current_password: '',
      new_password: '',
      confirm_password: ''
    })

    const getRoleName = (role) => {
      const roles = {
        'admin': 'Administrador',
        'accountant': 'Contador',
        'user': 'Usuario'
      }
      return roles[role] || role
    }

    const loadProfile = () => {
      if (authStore.user) {
        profile.value = { ...authStore.user }
      }
    }

    const updateProfile = async () => {
      loading.value = true
      try {
        await authStore.updateProfile(profile.value)
        toast.success('Perfil actualizado correctamente')
      } catch (error) {
        toast.error('Error al actualizar el perfil')
        console.error('Error updating profile:', error)
      } finally {
        loading.value = false
      }
    }

    const changePassword = async () => {
      if (passwordForm.value.new_password !== passwordForm.value.confirm_password) {
        toast.error('Las contraseñas no coinciden')
        return
      }

      passwordLoading.value = true
      try {
        await authStore.changePassword(passwordForm.value)
        toast.success('Contraseña cambiada correctamente')
        passwordForm.value = {
          current_password: '',
          new_password: '',
          confirm_password: ''
        }
      } catch (error) {
        toast.error('Error al cambiar la contraseña')
        console.error('Error changing password:', error)
      } finally {
        passwordLoading.value = false
      }
    }

    const resetForm = () => {
      loadProfile()
    }

    onMounted(() => {
      loadProfile()
    })

    return {
      profile,
      passwordForm,
      loading,
      passwordLoading,
      getRoleName,
      updateProfile,
      changePassword,
      resetForm
    }
  }
}
</script>










