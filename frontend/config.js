// Importar configuración centralizada (versión compatible con navegador)
import { 
  BACKEND_CONFIG, 
  getBaseUrl, 
  updateBackendConfig, 
  updateBackendIP 
} from '../scripts/vite-config-loader.js'

export const config = {
  API_BASE_URL: getBaseUrl(),
  BACKEND_CONFIG
}

// Re-exportar funciones para mantener compatibilidad
export { updateBackendConfig, updateBackendIP } 