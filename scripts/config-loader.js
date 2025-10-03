import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Leer la configuración centralizada
const configPath = path.join(__dirname, '..', 'config.json');
const configData = JSON.parse(fs.readFileSync(configPath, 'utf8'));

// Determinar el entorno (development por defecto)
const environment = process.env.NODE_ENV || 'development';
const envConfig = configData[environment];

// Configuración del backend
export const BACKEND_CONFIG = {
  IP: envConfig.backend.ip,
  PORT: envConfig.backend.port.toString(),
  PROTOCOL: envConfig.backend.protocol,
  HOST: envConfig.backend.host
};

// Configuración del frontend
export const FRONTEND_CONFIG = {
  PORT: envConfig.frontend.port,
  HOST: envConfig.frontend.host,
  ALLOWED_HOSTS: envConfig.frontend.allowedHosts
};

// Configuración de la base de datos
export const DATABASE_CONFIG = {
  PORT: envConfig.database.port,
  HOST: envConfig.database.host
};

// Función para obtener la URL base del backend
export const getBaseUrl = () => {
  return `${BACKEND_CONFIG.PROTOCOL}://${BACKEND_CONFIG.IP}:${BACKEND_CONFIG.PORT}`;
};

// Configuración completa
export const config = {
  API_BASE_URL: getBaseUrl(),
  BACKEND_CONFIG,
  FRONTEND_CONFIG,
  DATABASE_CONFIG,
  ENVIRONMENT: environment
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
