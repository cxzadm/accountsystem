<template>
  <div class="login-container">
    <div class="row justify-content-center align-items-center min-vh-100">
      <div class="col-md-4 col-lg-3">
        <div class="card shadow-lg">
          <div class="card-body p-5">
            <!-- Logo -->
            <div class="text-center mb-4">
              <i class="fas fa-calculator fa-3x text-primary mb-3"></i>
              <h3 class="card-title">Sistema Contable  Accescont Ecuador</h3>
              <p class="text-muted">Inicia sesión para continuar</p>
            </div>

            <!-- Login Form -->
            <form @submit.prevent="handleLogin">
              <div class="mb-3">
                <label for="username" class="form-label">Usuario</label>
                <div class="input-group">
                  <span class="input-group-text">
                    <i class="fas fa-user"></i>
                  </span>
                  <input
                    type="text"
                    class="form-control"
                    id="username"
                    v-model="form.username"
                    :class="{ 'is-invalid': errors.username }"
                    placeholder="Ingresa tu usuario"
                    required
                  />
                  <div class="invalid-feedback" v-if="errors.username">
                    {{ errors.username }}
                  </div>
                </div>
              </div>

              <div class="mb-3">
                <label for="password" class="form-label">Contraseña</label>
                <div class="input-group">
                  <span class="input-group-text">
                    <i class="fas fa-lock"></i>
                  </span>
                  <input
                    :type="showPassword ? 'text' : 'password'"
                    class="form-control"
                    id="password"
                    v-model="form.password"
                    :class="{ 'is-invalid': errors.password }"
                    placeholder="Ingresa tu contraseña"
                    required
                  />
                  <button
                    class="btn btn-outline-secondary"
                    type="button"
                    @click="togglePassword"
                  >
                    <i :class="showPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
                  </button>
                  <div class="invalid-feedback" v-if="errors.password">
                    {{ errors.password }}
                  </div>
                </div>
              </div>

              <div class="mb-3 form-check">
                <input
                  type="checkbox"
                  class="form-check-input"
                  id="rememberMe"
                  v-model="form.rememberMe"
                />
                <label class="form-check-label" for="rememberMe">
                  Recordarme
                </label>
              </div>

              <div class="d-grid">
                <button
                  type="submit"
                  class="btn btn-primary btn-lg"
                  :disabled="loading"
                >
                  <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                  <i v-else class="fas fa-sign-in-alt me-2"></i>
                  {{ loading ? 'Iniciando sesión...' : 'Iniciar Sesión' }}
                </button>
              </div>
            </form>

            <!-- Error Message -->
            <div v-if="errorMessage" class="alert alert-danger mt-3" role="alert">
              <i class="fas fa-exclamation-triangle me-2"></i>
              {{ errorMessage }}
            </div>

            <!-- Demo Credentials -->
            <div class="mt-4">
              <small class="text-muted">
                <strong>Credenciales de prueba:</strong><br>
                Admin: admin / admin123<br>
                Contador: contador / contador123
              </small>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useToast } from 'vue-toastification'

export default {
  name: 'Login',
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()
    const toast = useToast()

    // Form data
    const form = reactive({
      username: '',
      password: '',
      rememberMe: false
    })

    // State
    const loading = ref(false)
    const showPassword = ref(false)
    const errorMessage = ref('')
    const errors = reactive({})

    // Methods
    const togglePassword = () => {
      showPassword.value = !showPassword.value
    }

    const validateForm = () => {
      errors.username = ''
      errors.password = ''

      if (!form.username.trim()) {
        errors.username = 'El usuario es requerido'
        return false
      }

      if (!form.password) {
        errors.password = 'La contraseña es requerida'
        return false
      }

      return true
    }

    const handleLogin = async () => {
      if (!validateForm()) {
        return
      }

      loading.value = true
      errorMessage.value = ''

      try {
        const result = await authStore.login({
          username: form.username.trim(),
          password: form.password
        })

        if (result.success) {
          toast.success('¡Bienvenido!')
          router.push('/')
        } else {
          errorMessage.value = result.message
        }
      } catch (error) {
        console.error('Login error:', error)
        errorMessage.value = 'Error al iniciar sesión. Inténtalo de nuevo.'
      } finally {
        loading.value = false
      }
    }

    return {
      form,
      loading,
      showPassword,
      errorMessage,
      errors,
      togglePassword,
      handleLogin
    }
  }
}
</script>

<style scoped>
.login-container {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
}

.card {
  border: none;
  border-radius: 15px;
}

.card-title {
  font-weight: 600;
  color: #333;
}

.input-group-text {
  background-color: #f8f9fa;
  border-color: #dee2e6;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 8px;
  font-weight: 500;
}

.btn-primary:hover {
  background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.2);
}

.form-control:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
}

.spinner-border-sm {
  width: 1rem;
  height: 1rem;
}
</style>










