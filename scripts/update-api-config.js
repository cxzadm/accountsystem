const fs = require('fs');
const path = require('path');

// Función para actualizar la configuración del api.js
function updateApiConfig() {
  const configPath = path.join(__dirname, '..', 'config.json');
  const apiPath = path.join(__dirname, '..', 'frontend', 'src', 'services', 'api.js');
  
  // Leer la configuración centralizada
  const configData = JSON.parse(fs.readFileSync(configPath, 'utf8'));
  const envConfig = configData.development;
  
  // Leer el archivo api.js actual
  let apiContent = fs.readFileSync(apiPath, 'utf8');
  
  // Actualizar la lógica de detección de puerto para que sea más flexible
  const newApiContent = `import axios from 'axios'
import { config } from '../../config-browser.js'

// Decide baseURL: use reverse-proxy path in production (served via Nginx),
// and direct backend URL during Vite dev server
const isViteDev = typeof window !== 'undefined' && (
  window.location.hostname === 'localhost' || 
  window.location.hostname === '127.0.0.1' ||
  window.location.port.startsWith('517')
)

const apiBaseURL = isViteDev ? \`\${config.API_BASE_URL}/api\` : '/api'

// Create axios instance
const api = axios.create({
  baseURL: apiBaseURL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Get token from localStorage directly
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = \`Bearer \${token}\`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response
  },
  async (error) => {
    // Solo cerrar sesión automáticamente en 401 (token inválido/expirado)
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('refreshToken')
      localStorage.removeItem('user')
      localStorage.removeItem('permissions')
      window.location.href = '/login'
    }
    // Para 403 (forbidden) solo propagamos el error para que la UI lo maneje
    return Promise.reject(error)
  }
)

export default api`;

  // Escribir el archivo actualizado
  fs.writeFileSync(apiPath, newApiContent);
  
  console.log('✅ api.js actualizado exitosamente');
  console.log(`📊 Configuración aplicada:`);
  console.log(`   - Backend: ${envConfig.backend.protocol}://${envConfig.backend.ip}:${envConfig.backend.port}`);
  console.log(`   - Frontend: puerto ${envConfig.frontend.port}`);
}

// Si se ejecuta directamente
if (require.main === module) {
  updateApiConfig();
}

module.exports = { updateApiConfig };


