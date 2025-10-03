const fs = require('fs');
const path = require('path');

// Función para sincronizar la configuración con config-browser.js
function syncBrowserConfig() {
  const configPath = path.join(__dirname, '..', 'config.json');
  const browserConfigPath = path.join(__dirname, '..', 'frontend', 'config-browser.js');
  
  // Leer la configuración centralizada
  const configData = JSON.parse(fs.readFileSync(configPath, 'utf8'));
  const envConfig = configData.development; // Usar development para el navegador
  
  // Generar el contenido del config-browser.js
  const browserConfigContent = `// Configuración del frontend compatible con navegador
// Esta versión no usa módulos de Node.js
// GENERADO AUTOMÁTICAMENTE - NO EDITAR MANUALMENTE

// Configuración hardcodeada para el navegador
const BACKEND_CONFIG = {
  IP: '${envConfig.backend.ip}',
  PORT: '${envConfig.backend.port}',
  PROTOCOL: '${envConfig.backend.protocol}'
};

// Función para obtener la URL base del backend
const getBaseUrl = () => {
  return \`\${BACKEND_CONFIG.PROTOCOL}://\${BACKEND_CONFIG.IP}:\${BACKEND_CONFIG.PORT}\`;
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
`;

  // Escribir el archivo
  fs.writeFileSync(browserConfigPath, browserConfigContent);
  
  console.log('✅ config-browser.js sincronizado exitosamente');
  console.log(`📊 Configuración aplicada:`);
  console.log(`   - Backend: ${envConfig.backend.protocol}://${envConfig.backend.ip}:${envConfig.backend.port}`);
}

// Si se ejecuta directamente
if (require.main === module) {
  syncBrowserConfig();
}

module.exports = { syncBrowserConfig };


