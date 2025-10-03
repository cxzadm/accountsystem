// Configuración específica para Vite (sin módulos de Node.js)
// Esta versión es compatible con el entorno de Vite
// GENERADO AUTOMÁTICAMENTE - NO EDITAR MANUALMENTE

// Configuración hardcodeada para evitar problemas de compatibilidad
const BACKEND_CONFIG = {
  IP: '172.16.0.2',
  PORT: '8006',
  PROTOCOL: 'http',
  HOST: '0.0.0.0'
};

const FRONTEND_CONFIG = {
  PORT: 5176,
  HOST: '0.0.0.0',
  ALLOWED_HOSTS: ["accescontserver.sytes.net","localhost","127.0.0.1","172.16.0.2"]
};

const DATABASE_CONFIG = {
  PORT: 27017,
  HOST: 'localhost'
};

// Función para obtener la URL base del backend
const getBaseUrl = () => {
  return `${BACKEND_CONFIG.PROTOCOL}://${BACKEND_CONFIG.IP}:${BACKEND_CONFIG.PORT}`;
};

// Configuración completa
const config = {
  API_BASE_URL: getBaseUrl(),
  BACKEND_CONFIG,
  FRONTEND_CONFIG,
  DATABASE_CONFIG,
  ENVIRONMENT: 'development'
};

// Función para actualizar la configuración del backend
const updateBackendConfig = (newConfig) => {
  Object.assign(BACKEND_CONFIG, newConfig);
  config.API_BASE_URL = getBaseUrl();
};

// Función para actualizar solo la IP
const updateBackendIP = (newIP) => {
  BACKEND_CONFIG.IP = newIP;
  config.API_BASE_URL = getBaseUrl();
};

export { 
  BACKEND_CONFIG, 
  FRONTEND_CONFIG, 
  DATABASE_CONFIG, 
  getBaseUrl, 
  config, 
  updateBackendConfig, 
  updateBackendIP 
};
