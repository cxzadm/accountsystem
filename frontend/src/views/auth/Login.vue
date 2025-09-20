<template>
  <div class="login-container">
    <!-- Background Pattern -->
    <div class="background-pattern"></div>
    
    <div class="row justify-content-center align-items-center min-vh-100">
      <div class="col-md-5 col-lg-4 col-xl-3">
        <div class="login-card">
          <!-- Header -->
          <div class="login-header">
            <div class="logo-container">
              <div class="logo-icon">
                <i class="fas fa-calculator"></i>
              </div>
              <div class="logo-text">
                <h2 class="brand-title">Accescont</h2>
                <p class="brand-subtitle">Sistema Contable Ecuador</p>
              </div>
            </div>
          </div>

          <!-- Login Form -->
          <div class="login-form">
            <form @submit.prevent="handleLogin">
              <div class="form-group">
                <label for="username" class="form-label">
                  <i class="fas fa-user me-2"></i>
                  Usuario
                </label>
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

              <div class="form-group">
                <label for="password" class="form-label">
                  <i class="fas fa-lock me-2"></i>
                  Contraseña
                </label>
                <div class="password-input">
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
                    class="password-toggle"
                    type="button"
                    @click="togglePassword"
                    :title="showPassword ? 'Ocultar contraseña' : 'Mostrar contraseña'"
                  >
                    <i :class="showPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
                  </button>
                </div>
                <div class="invalid-feedback" v-if="errors.password">
                  {{ errors.password }}
                </div>
              </div>

              <div class="form-options">
                <div class="form-check">
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
              </div>

              <button
                type="submit"
                class="login-btn"
                :disabled="loading"
              >
                <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                <i v-else class="fas fa-sign-in-alt me-2"></i>
                {{ loading ? 'Iniciando sesión...' : 'Iniciar Sesión' }}
              </button>
            </form>

            <!-- Error Message -->
            <div v-if="errorMessage" class="error-message">
              <i class="fas fa-exclamation-triangle me-2"></i>
              {{ errorMessage }}
            </div>
          </div>

          <!-- Footer -->
          <div class="login-footer">
            <p class="footer-text">
              © 2025 Accescont Ecuador. Todos los derechos reservados.
            </p>
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
/* Variables de color */
:root {
  --primary-color: #165c6a;
  --primary-light: #1e7a8a;
  --primary-dark: #0f4a54;
  --secondary-color: #f8f9fa;
  --accent-color: #28a745;
  --text-dark: #2c3e50;
  --text-light: #6c757d;
  --border-color: #e9ecef;
  --shadow-light: rgba(22, 92, 106, 0.1);
  --shadow-medium: rgba(22, 92, 106, 0.2);
  --shadow-dark: rgba(22, 92, 106, 0.3);
}

/* Contenedor principal */
.login-container {
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-light) 50%, var(--primary-dark) 100%);
  min-height: 100vh;
  position: relative;
  overflow: hidden;
}

/* Patrón de fondo */
.background-pattern {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: 
    radial-gradient(circle at 20% 80%, rgba(255, 255, 255, 0.1) 0%, transparent 50%),
    radial-gradient(circle at 80% 20%, rgba(255, 255, 255, 0.1) 0%, transparent 50%),
    radial-gradient(circle at 40% 40%, rgba(255, 255, 255, 0.05) 0%, transparent 50%);
  animation: float 20s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0px) rotate(0deg); }
  50% { transform: translateY(-20px) rotate(1deg); }
}

/* Tarjeta de login */
.login-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  box-shadow: 
    0 20px 40px var(--shadow-medium),
    0 8px 16px var(--shadow-light),
    inset 0 1px 0 rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.2);
  overflow: hidden;
  position: relative;
  z-index: 10;
}

/* Header del login */
.login-header {
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-light) 100%);
  padding: 2.5rem 2rem 2rem;
  text-align: center;
  position: relative;
}

.login-header::before {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent 0%, rgba(255, 255, 255, 0.3) 50%, transparent 100%);
}

.logo-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.logo-icon {
  width: 80px;
  height: 80px;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(10px);
  border: 2px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
}

.logo-icon i {
  font-size: 2.5rem;
  color: white;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.brand-title {
  color: white;
  font-size: 2rem;
  font-weight: 700;
  margin: 0;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  letter-spacing: -0.5px;
}

.brand-subtitle {
  color: rgba(255, 255, 255, 0.9);
  font-size: 1rem;
  margin: 0;
  font-weight: 400;
  letter-spacing: 0.5px;
}

/* Formulario de login */
.login-form {
  padding: 2.5rem 2rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-label {
  color: var(--text-dark);
  font-weight: 600;
  font-size: 0.9rem;
  margin-bottom: 0.75rem;
  display: flex;
  align-items: center;
}

.form-label i {
  color: var(--primary-color);
  font-size: 0.85rem;
}

.form-control {
  border: 2px solid var(--border-color);
  border-radius: 12px;
  padding: 0.875rem 1rem;
  font-size: 1rem;
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
}

.form-control:focus {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 0.2rem var(--shadow-light);
  background: white;
  transform: translateY(-1px);
}

.form-control::placeholder {
  color: var(--text-light);
  font-weight: 400;
}

/* Input de contraseña */
.password-input {
  position: relative;
}

.password-toggle {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: var(--text-light);
  font-size: 1rem;
  padding: 0.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
  border-radius: 6px;
}

.password-toggle:hover {
  color: var(--primary-color);
  background: rgba(22, 92, 106, 0.1);
}

/* Opciones del formulario */
.form-options {
  margin-bottom: 2rem;
}

.form-check {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.form-check-input {
  width: 18px;
  height: 18px;
  border: 2px solid var(--border-color);
  border-radius: 4px;
  background: white;
  cursor: pointer;
  transition: all 0.3s ease;
}

.form-check-input:checked {
  background-color: var(--primary-color);
  border-color: var(--primary-color);
}

.form-check-input:focus {
  box-shadow: 0 0 0 0.2rem var(--shadow-light);
}

.form-check-label {
  color: var(--text-dark);
  font-weight: 500;
  cursor: pointer;
  user-select: none;
}

/* Botón de login */
.login-btn {
  width: 100%;
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-light) 100%);
  border: none;
  border-radius: 12px;
  padding: 1rem 2rem;
  font-size: 1.1rem;
  font-weight: 600;
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  box-shadow: 0 4px 12px var(--shadow-medium);
}

.login-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s;
}

.login-btn:hover::before {
  left: 100%;
}

.login-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px var(--shadow-dark);
}

.login-btn:active {
  transform: translateY(0);
}

.login-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
}

/* Mensaje de error */
.error-message {
  background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
  color: white;
  padding: 1rem 1.25rem;
  border-radius: 12px;
  font-size: 0.9rem;
  font-weight: 500;
  margin-top: 1.5rem;
  display: flex;
  align-items: center;
  box-shadow: 0 4px 12px rgba(220, 53, 69, 0.3);
  animation: shake 0.5s ease-in-out;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-5px); }
  75% { transform: translateX(5px); }
}

/* Footer */
.login-footer {
  background: var(--secondary-color);
  padding: 1.5rem 2rem;
  text-align: center;
  border-top: 1px solid var(--border-color);
}

.footer-text {
  color: var(--text-light);
  font-size: 0.85rem;
  margin: 0;
  font-weight: 400;
}

/* Spinner */
.spinner-border-sm {
  width: 1rem;
  height: 1rem;
  border-width: 2px;
}

/* Responsive */
@media (max-width: 768px) {
  .login-card {
    margin: 1rem;
    border-radius: 20px;
  }
  
  .login-header {
    padding: 2rem 1.5rem 1.5rem;
  }
  
  .login-form {
    padding: 2rem 1.5rem;
  }
  
  .logo-icon {
    width: 70px;
    height: 70px;
  }
  
  .logo-icon i {
    font-size: 2rem;
  }
  
  .brand-title {
    font-size: 1.75rem;
  }
}

/* Animaciones de entrada */
.login-card {
  animation: slideUp 0.6s ease-out;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>











