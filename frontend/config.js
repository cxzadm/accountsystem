// Configuración del backend
const BACKEND_CONFIG = {
  // IP del servidor backend
  IP: '192.168.68.113',
  // Puerto del servidor backend
  PORT: '8000',
  // Protocolo (http/https)
  PROTOCOL: 'http'
}

// Get the current hostname and port
const getBaseUrl = () => {
  // Siempre usar la IP configurada
  return `${BACKEND_CONFIG.PROTOCOL}://${BACKEND_CONFIG.IP}:${BACKEND_CONFIG.PORT}`
}

export const config = {
  API_BASE_URL: getBaseUrl(),
  BACKEND_CONFIG
}

// Función para actualizar la configuración del backend
export const updateBackendConfig = (newConfig) => {
  Object.assign(BACKEND_CONFIG, newConfig)
  config.API_BASE_URL = getBaseUrl()
}

// Función para actualizar solo la IP
export const updateBackendIP = (newIP) => {
  BACKEND_CONFIG.IP = newIP
  config.API_BASE_URL = getBaseUrl()
} 