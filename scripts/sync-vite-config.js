const fs = require('fs');
const path = require('path');

// Función para sincronizar la configuración con vite-config-loader.js
function syncViteConfig() {
  const configPath = path.join(__dirname, '..', 'config.json');
  const viteConfigPath = path.join(__dirname, 'vite-config-loader.js');
  
  // Leer la configuración centralizada
  const configData = JSON.parse(fs.readFileSync(configPath, 'utf8'));
  const envConfig = configData.development; // Usar development para Vite
  
  // Generar el contenido del vite-config-loader.js
  const viteConfigContent = `// Configuración específica para Vite (sin módulos de Node.js)
// Esta versión es compatible con el entorno de Vite
// GENERADO AUTOMÁTICAMENTE - NO EDITAR MANUALMENTE

// Configuración hardcodeada para evitar problemas de compatibilidad
const BACKEND_CONFIG = {
  IP: '${envConfig.backend.ip}',
  PORT: '${envConfig.backend.port}',
  PROTOCOL: '${envConfig.backend.protocol}',
  HOST: '${envConfig.backend.host}'
};

const FRONTEND_CONFIG = {
  PORT: ${envConfig.frontend.port},
  HOST: '${envConfig.frontend.host}',
  ALLOWED_HOSTS: ${JSON.stringify(envConfig.frontend.allowedHosts)}
};

const DATABASE_CONFIG = {
  PORT: ${envConfig.database.port},
  HOST: '${envConfig.database.host}'
};

// Función para obtener la URL base del backend
const getBaseUrl = () => {
  return \`\${BACKEND_CONFIG.PROTOCOL}://\${BACKEND_CONFIG.IP}:\${BACKEND_CONFIG.PORT}\`;
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
`;

  // Escribir el archivo
  fs.writeFileSync(viteConfigPath, viteConfigContent);
  
  console.log('✅ vite-config-loader.js sincronizado exitosamente');
  console.log(`📊 Configuración aplicada:`);
  console.log(`   - Frontend: puerto ${envConfig.frontend.port}`);
  console.log(`   - Backend: puerto ${envConfig.backend.port}`);
}

// Si se ejecuta directamente
if (require.main === module) {
  syncViteConfig();
}

module.exports = { syncViteConfig };


