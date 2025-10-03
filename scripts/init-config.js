const fs = require('fs');
const path = require('path');
const os = require('os');

// Función para obtener la IP del equipo
function getLocalIP() {
  const interfaces = os.networkInterfaces();
  for (const name of Object.keys(interfaces)) {
    for (const iface of interfaces[name]) {
      // Saltar interfaces internas y no IPv4
      if (iface.family === 'IPv4' && !iface.internal) {
        return iface.address;
      }
    }
  }
  return 'localhost'; // Fallback si no se encuentra IP
}

// Función para inicializar la configuración con la IP actual
function initConfig() {
  const configPath = path.join(__dirname, '..', 'config.json');
  
  // Leer configuración actual
  const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
  
  // Obtener la IP actual del equipo
  const currentIP = getLocalIP();
  
  // Actualizar IP del equipo en development y production
  config.development.backend.ip = currentIP;
  config.production.backend.ip = currentIP;
  
  // Actualizar allowedHosts para incluir la IP actual
  if (!config.development.frontend.allowedHosts.includes(currentIP)) {
    config.development.frontend.allowedHosts.push(currentIP);
  }
  
  // Escribir configuración actualizada
  fs.writeFileSync(configPath, JSON.stringify(config, null, 2));
  
  console.log('✅ Configuración inicializada con IP del equipo actual');
  console.log(`🌐 IP detectada: ${currentIP}`);
  console.log(`📊 Configuración actualizada:`);
  console.log(`   - Frontend: puerto ${config.development.frontend.port}`);
  console.log(`   - Backend: puerto ${config.development.backend.port}, IP: ${currentIP}`);
  
  return config;
}

// Si se ejecuta directamente
if (require.main === module) {
  initConfig();
}

module.exports = { initConfig, getLocalIP };
