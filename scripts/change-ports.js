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

// Función para cambiar los puertos en la configuración
function changePorts(frontendPort, backendPort) {
  const configPath = path.join(__dirname, '..', 'config.json');
  
  // Leer configuración actual
  const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
  
  // Obtener la IP actual del equipo
  const currentIP = getLocalIP();
  
  // Actualizar puertos en development
  if (frontendPort) {
    config.development.frontend.port = frontendPort;
    config.production.frontend.port = frontendPort;
  }
  
  if (backendPort) {
    config.development.backend.port = backendPort;
    config.production.backend.port = backendPort;
  }
  
  // Actualizar IP del equipo en development y production
  config.development.backend.ip = currentIP;
  config.production.backend.ip = currentIP;
  
  // Actualizar allowedHosts para incluir la IP actual
  if (!config.development.frontend.allowedHosts.includes(currentIP)) {
    config.development.frontend.allowedHosts.push(currentIP);
  }
  
  // Escribir configuración actualizada
  fs.writeFileSync(configPath, JSON.stringify(config, null, 2));
  
  console.log('✅ Configuración actualizada exitosamente');
  console.log(`📊 Nuevos puertos:`);
  console.log(`   - Frontend: ${config.development.frontend.port}`);
  console.log(`   - Backend: ${config.development.backend.port}`);
  console.log(`🌐 IP del equipo: ${currentIP}`);
  
  return config;
}

// Función para mostrar la configuración actual
function showCurrentConfig() {
  const configPath = path.join(__dirname, '..', 'config.json');
  const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
  const currentIP = getLocalIP();
  
  console.log('📊 Configuración actual:');
  console.log(`   - Frontend (development): puerto ${config.development.frontend.port}`);
  console.log(`   - Backend (development): puerto ${config.development.backend.port}, IP: ${config.development.backend.ip}`);
  console.log(`   - Frontend (production): puerto ${config.production.frontend.port}`);
  console.log(`   - Backend (production): puerto ${config.production.backend.port}, IP: ${config.production.backend.ip}`);
  console.log(`🌐 IP actual del equipo: ${currentIP}`);
}

// Función para regenerar docker-compose.yml
function regenerateDockerCompose() {
  const { execSync } = require('child_process');
  try {
    execSync('node scripts/generate-docker-compose.js', { stdio: 'inherit' });
    console.log('✅ docker-compose.yml regenerado exitosamente');
  } catch (error) {
    console.error('❌ Error al regenerar docker-compose.yml:', error.message);
  }
}

// Función para sincronizar configuración de Vite
function syncViteConfig() {
  const { execSync } = require('child_process');
  try {
    execSync('node scripts/sync-vite-config.js', { stdio: 'inherit' });
    console.log('✅ Configuración de Vite sincronizada exitosamente');
  } catch (error) {
    console.error('❌ Error al sincronizar configuración de Vite:', error.message);
  }
}

// Función para sincronizar configuración del navegador
function syncBrowserConfig() {
  const { execSync } = require('child_process');
  try {
    execSync('node scripts/sync-browser-config.js', { stdio: 'inherit' });
    console.log('✅ Configuración del navegador sincronizada exitosamente');
  } catch (error) {
    console.error('❌ Error al sincronizar configuración del navegador:', error.message);
  }
}

// Función para actualizar configuración del API
function updateApiConfig() {
  const { execSync } = require('child_process');
  try {
    execSync('node scripts/update-api-config.js', { stdio: 'inherit' });
    console.log('✅ Configuración del API actualizada exitosamente');
  } catch (error) {
    console.error('❌ Error al actualizar configuración del API:', error.message);
  }
}

// Exportar funciones
module.exports = { changePorts, showCurrentConfig, regenerateDockerCompose, syncViteConfig, syncBrowserConfig, updateApiConfig };

// Si se ejecuta directamente desde línea de comandos
if (require.main === module) {
  const args = process.argv.slice(2);
  
  if (args.length === 0) {
    showCurrentConfig();
  } else if (args[0] === '--help' || args[0] === '-h') {
    console.log(`
🔧 Script de cambio de puertos - Sistema Contable

Uso:
  node scripts/change-ports.js [frontend_port] [backend_port]
  node scripts/change-ports.js --show
  node scripts/change-ports.js --regenerate-docker

Ejemplos:
  node scripts/change-ports.js 5174 8001    # Cambiar frontend a 5174 y backend a 8001
  node scripts/change-ports.js 5174         # Cambiar solo frontend a 5174
  node scripts/change-ports.js -- 8001      # Cambiar solo backend a 8001
  node scripts/change-ports.js --show       # Mostrar configuración actual
  node scripts/change-ports.js --regenerate-docker  # Regenerar docker-compose.yml

Nota: Los cambios se aplican tanto a development como a production.
    `);
  } else if (args[0] === '--show') {
    showCurrentConfig();
  } else if (args[0] === '--regenerate-docker') {
    regenerateDockerCompose();
  } else {
    const frontendPort = args[0] ? parseInt(args[0]) : null;
    const backendPort = args[1] ? parseInt(args[1]) : null;
    
    if (isNaN(frontendPort) && frontendPort !== null) {
      console.error('❌ Puerto del frontend debe ser un número válido');
      process.exit(1);
    }
    
    if (isNaN(backendPort) && backendPort !== null) {
      console.error('❌ Puerto del backend debe ser un número válido');
      process.exit(1);
    }
    
    changePorts(frontendPort, backendPort);
    syncViteConfig();
    syncBrowserConfig();
    updateApiConfig();
    regenerateDockerCompose();
  }
}
