// Configuración del frontend compatible con navegador
// Esta versión no usa módulos de Node.js
// GENERADO AUTOMÁTICAMENTE - NO EDITAR MANUALMENTE

// Configuración hardcodeada para el navegador
const BACKEND_CONFIG = {
  IP: '172.16.0.2',
  PORT: '8008',
  PROTOCOL: 'http'
};

// Función para obtener la URL base del backend
const getBaseUrl = () => {
  return `${BACKEND_CONFIG.PROTOCOL}://${BACKEND_CONFIG.IP}:${BACKEND_CONFIG.PORT}`;
};

// Configuración completa
export const config = {
  API_BASE_URL: getBaseUrl(),
  BACKEND_CONFIG
};

// Función para actualizar la configuración del backend
export const updateBackendConfig = (newConfig) => {
  Object.assign(BACKEND_CONFIG, newConfig);
  config.API_BASE_URL = getBaseUrl();
};

// Función para actualizar solo la IP
export const updateBackendIP = (newIP) => {
  BACKEND_CONFIG.IP = newIP;
  config.API_BASE_URL = getBaseUrl();
};
