# 🔧 Estrategia de Configuración Centralizada

Esta guía explica cómo implementar un sistema de configuración centralizada que permite cambiar puertos y configuraciones desde un solo archivo, manteniendo sincronización automática entre frontend, backend y Docker.

## 📋 **Problema Resuelto**

**Antes:** Cambiar puertos requería editar múltiples archivos manualmente:
- `frontend/vite.config.js`
- `frontend/config.js`
- `backend/app/config.py`
- `backend/run.py`
- `docker-compose.yml`
- Y más...

**Después:** Un solo comando cambia todo automáticamente:
```bash
node scripts/change-ports.js 5174 8001
```

## 🏗️ **Arquitectura de la Solución**

```mermaid
graph TD
    A[config.json] --> B[Scripts de Sincronización]
    B --> C[Frontend Config]
    B --> D[Backend Config]
    B --> E[Docker Config]
    B --> F[API Config]
    
    C --> G[vite.config.js]
    C --> H[config-browser.js]
    D --> I[config.py]
    D --> J[run.py]
    E --> K[docker-compose.yml]
    F --> L[api.js]
```

## 📁 **Estructura de Archivos**

```
proyecto/
├── config.json                          # 🎯 Archivo principal de configuración
├── scripts/
│   ├── change-ports.js                  # 🔄 Script principal de cambio de puertos
│   ├── config-loader.js                # 📦 Cargador para Node.js
│   ├── config_loader.py                # 🐍 Cargador para Python
│   ├── vite-config-loader.js           # ⚡ Configuración para Vite
│   ├── sync-vite-config.js             # 🔄 Sincronizador de Vite
│   ├── sync-browser-config.js           # 🌐 Sincronizador del navegador
│   ├── update-api-config.js            # 🔌 Actualizador del API
│   └── generate-docker-compose.js      # 🐳 Generador de Docker
├── frontend/
│   ├── vite.config.js                  # ⚡ Configuración de Vite
│   ├── config-browser.js               # 🌐 Configuración del navegador
│   └── src/services/api.js             # 🔌 Configuración del API
└── backend/
    ├── app/config.py                   # 🐍 Configuración del backend
    └── run.py                          # 🚀 Ejecutor del backend
```

## 🎯 **1. Archivo Principal de Configuración**

### `config.json`
```json
{
  "development": {
    "frontend": {
      "port": 5173,
      "host": "0.0.0.0",
      "allowedHosts": ["localhost", "127.0.0.1", "192.168.68.113"]
    },
    "backend": {
      "port": 8000,
      "host": "0.0.0.0",
      "ip": "192.168.68.113",
      "protocol": "http"
    },
    "database": {
      "port": 27017,
      "host": "localhost"
    }
  },
  "production": {
    "frontend": {
      "port": 80,
      "host": "0.0.0.0",
      "allowedHosts": ["tu-dominio.com"]
    },
    "backend": {
      "port": 8000,
      "host": "0.0.0.0",
      "ip": "192.168.68.113",
      "protocol": "http"
    },
    "database": {
      "port": 27017,
      "host": "mongodb"
    }
  }
}
```

## 🔧 **2. Scripts de Sincronización**

### `scripts/config-loader.js` (Node.js)
```javascript
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

// Funciones de actualización
export const updateBackendConfig = (newConfig) => {
  Object.assign(BACKEND_CONFIG, newConfig);
  config.API_BASE_URL = getBaseUrl();
};

export const updateBackendIP = (newIP) => {
  BACKEND_CONFIG.IP = newIP;
  config.API_BASE_URL = getBaseUrl();
};
```

### `scripts/config_loader.py` (Python)
```python
import json
import os
from pathlib import Path

def load_config():
    """Cargar configuración centralizada desde config.json"""
    current_dir = Path(__file__).parent
    config_path = current_dir.parent / "config.json"
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    environment = os.getenv('ENVIRONMENT', 'development')
    env_config = config.get(environment, config['development'])
    
    return env_config

def get_backend_config():
    """Obtener configuración específica del backend"""
    config = load_config()
    return config['backend']

def get_database_config():
    """Obtener configuración específica de la base de datos"""
    config = load_config()
    return config['database']

def get_frontend_config():
    """Obtener configuración específica del frontend"""
    config = load_config()
    return config['frontend']

# Configuración por defecto
_config = load_config()
BACKEND_CONFIG = _config['backend']
DATABASE_CONFIG = _config['database']
FRONTEND_CONFIG = _config['frontend']
```

### `scripts/change-ports.js` (Script Principal)
```javascript
const fs = require('fs');
const path = require('path');

// Función para cambiar los puertos en la configuración
function changePorts(frontendPort, backendPort) {
  const configPath = path.join(__dirname, '..', 'config.json');
  
  // Leer configuración actual
  const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
  
  // Actualizar puertos en development
  if (frontendPort) {
    config.development.frontend.port = frontendPort;
    config.production.frontend.port = frontendPort;
  }
  
  if (backendPort) {
    config.development.backend.port = backendPort;
    config.production.backend.port = backendPort;
  }
  
  // Escribir configuración actualizada
  fs.writeFileSync(configPath, JSON.stringify(config, null, 2));
  
  console.log('✅ Configuración actualizada exitosamente');
  console.log(`📊 Nuevos puertos:`);
  console.log(`   - Frontend: ${config.development.frontend.port}`);
  console.log(`   - Backend: ${config.development.backend.port}`);
  
  return config;
}

// Función para mostrar la configuración actual
function showCurrentConfig() {
  const configPath = path.join(__dirname, '..', 'config.json');
  const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
  
  console.log('📊 Configuración actual:');
  console.log(`   - Frontend (development): puerto ${config.development.frontend.port}`);
  console.log(`   - Backend (development): puerto ${config.development.backend.port}`);
  console.log(`   - Frontend (production): puerto ${config.production.frontend.port}`);
  console.log(`   - Backend (production): puerto ${config.production.backend.port}`);
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

// Exportar funciones
module.exports = { 
  changePorts, 
  showCurrentConfig, 
  regenerateDockerCompose, 
  syncViteConfig, 
  syncBrowserConfig, 
  updateApiConfig 
};

// Si se ejecuta directamente desde línea de comandos
if (require.main === module) {
  const args = process.argv.slice(2);
  
  if (args.length === 0) {
    showCurrentConfig();
  } else if (args[0] === '--help' || args[0] === '-h') {
    console.log(`
🔧 Script de cambio de puertos - Sistema de Configuración Centralizada

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
```

## 🌐 **3. Configuración del Frontend**

### `frontend/vite.config.js`
```javascript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'
import { BACKEND_CONFIG, FRONTEND_CONFIG } from '../scripts/vite-config-loader.js'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    port: FRONTEND_CONFIG.PORT,
    host: FRONTEND_CONFIG.HOST,
    cors: true,
    strictPort: true,
    allowedHosts: FRONTEND_CONFIG.ALLOWED_HOSTS,
    hmr: {
      host: BACKEND_CONFIG.IP,
      protocol: 'ws',
      clientPort: FRONTEND_CONFIG.PORT
    }
  }
})
```

### `frontend/config-browser.js`
```javascript
// Configuración del frontend compatible con navegador
// Esta versión no usa módulos de Node.js
// GENERADO AUTOMÁTICAMENTE - NO EDITAR MANUALMENTE

// Configuración hardcodeada para el navegador
const BACKEND_CONFIG = {
  IP: '192.168.68.113',
  PORT: '8000',
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

// Funciones de actualización
export const updateBackendConfig = (newConfig) => {
  Object.assign(BACKEND_CONFIG, newConfig);
  config.API_BASE_URL = getBaseUrl();
};

export const updateBackendIP = (newIP) => {
  BACKEND_CONFIG.IP = newIP;
  config.API_BASE_URL = getBaseUrl();
};
```

### `frontend/src/services/api.js`
```javascript
import axios from 'axios'
import { config } from '../../config-browser.js'

// Decide baseURL: use reverse-proxy path in production (served via Nginx),
// and direct backend URL during Vite dev server
const isViteDev = typeof window !== 'undefined' && (
  window.location.hostname === 'localhost' || 
  window.location.hostname === '127.0.0.1' ||
  window.location.port.startsWith('517')
)

const apiBaseURL = isViteDev ? `${config.API_BASE_URL}/api` : '/api'

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
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
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
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('refreshToken')
      localStorage.removeItem('user')
      localStorage.removeItem('permissions')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default api
```

## 🐍 **4. Configuración del Backend**

### `backend/app/config.py`
```python
from pydantic_settings import BaseSettings
from typing import List, ClassVar
import os
import sys
from pathlib import Path

# Agregar el directorio scripts al path para importar config_loader
scripts_dir = Path(__file__).parent.parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

from config_loader import get_backend_config, get_database_config, get_frontend_config

# Obtener configuraciones fuera de la clase
database_config = get_database_config()
backend_config = get_backend_config()
frontend_config = get_frontend_config()

class Settings(BaseSettings):
    # Database - usar configuración centralizada
    mongodb_url: str = f"mongodb://{database_config['host']}:{database_config['port']}"
    database_name: str = "sistema_contable_ec"
    
    # Backend - usar configuración centralizada
    backend_port: int = backend_config['port']
    backend_host: str = backend_config['host']
    backend_ip: str = backend_config['ip']
    backend_protocol: str = backend_config['protocol']
    
    # Frontend - usar configuración centralizada
    frontend_port: int = frontend_config['port']
    
    # JWT
    secret_key: str = "tu-clave-secreta-super-segura-aqui"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    # CORS - usar configuración centralizada del frontend
    allowed_origins: List[str] = [
        f"http://localhost:{frontend_config['port']}",
        f"http://{backend_config['ip']}:{frontend_config['port']}",
        f"{backend_config['protocol']}://{backend_config['ip']}:{frontend_config['port']}"
    ]
    
    # App
    app_name: str = "Sistema Contable"
    version: str = "1.0.0"
    debug: bool = True
    
    # SRI Configuration
    sri_ruc: str = ""
    sri_ambiente: str = "pruebas"
    
    class Config:
        env_file = ".env"

settings = Settings()
```

### `backend/run.py`
```python
import uvicorn
from app.main import app
from app.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=settings.debug,
        workers=1
    )
```

## 🐳 **5. Configuración de Docker**

### `scripts/generate-docker-compose.js`
```javascript
const fs = require('fs');
const path = require('path');

// Leer la configuración centralizada
const configPath = path.join(__dirname, '..', 'config.json');
const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));

// Usar configuración de producción para Docker
const prodConfig = config.production;

// Generar docker-compose.yml
const dockerComposeContent = `version: '3.8'

services:
  mongodb:
    image: mongo:5.0
    container_name: sistema-contable-mongodb
    restart: unless-stopped
    ports:
      - "${prodConfig.database.port}:27017"
    environment:
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: password123
      MONGO_INITDB_DATABASE: sistema_contable_ec
    volumes:
      - mongodb_data:/data/db
      - ./backend/scripts/mongo-init.js:/docker-entrypoint-initdb.d/mongo-init.js:ro
    networks:
      - sistema-contable-network

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: sistema-contable-backend
    restart: unless-stopped
    ports:
      - "${prodConfig.backend.port}:${prodConfig.backend.port}"
    environment:
      - MONGODB_URL=mongodb://admin:password123@mongodb:27017/sistema_contable_ec?authSource=admin
      - SECRET_KEY=tu-clave-secreta-super-segura-para-produccion
      - DEBUG=false
      - ENVIRONMENT=production
    depends_on:
      - mongodb
    networks:
      - sistema-contable-network
    volumes:
      - ./backend:/app
    command: uvicorn app.main:app --host ${prodConfig.backend.host} --port ${prodConfig.backend.port}

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: sistema-contable-frontend
    restart: unless-stopped
    ports:
      - "${prodConfig.frontend.port}:80"
    depends_on:
      - backend
    networks:
      - sistema-contable-network

volumes:
  mongodb_data:

networks:
  sistema-contable-network:
    driver: bridge
`;

// Escribir el archivo docker-compose.yml
const dockerComposePath = path.join(__dirname, '..', 'docker-compose.yml');
fs.writeFileSync(dockerComposePath, dockerComposeContent);

console.log('✅ docker-compose.yml generado exitosamente con la configuración centralizada');
console.log(`📊 Configuración aplicada:`);
console.log(`   - Backend: puerto ${prodConfig.backend.port}`);
console.log(`   - Frontend: puerto ${prodConfig.frontend.port}`);
console.log(`   - Database: puerto ${prodConfig.database.port}`);
```

## 🔄 **6. Scripts de Sincronización**

### `scripts/sync-vite-config.js`
```javascript
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
```

### `scripts/sync-browser-config.js`
```javascript
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
```

### `scripts/update-api-config.js`
```javascript
const fs = require('fs');
const path = require('path');

// Función para actualizar la configuración del api.js
function updateApiConfig() {
  const configPath = path.join(__dirname, '..', 'config.json');
  const apiPath = path.join(__dirname, '..', 'frontend', 'src', 'services', 'api.js');
  
  // Leer la configuración centralizada
  const configData = JSON.parse(fs.readFileSync(configPath, 'utf8'));
  const envConfig = configData.development;
  
  // Generar el contenido del api.js
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
```

## 🚀 **7. Uso del Sistema**

### Comandos Principales
```bash
# Cambiar puertos (frontend y backend)
node scripts/change-ports.js 5174 8001

# Cambiar solo frontend
node scripts/change-ports.js 5174

# Cambiar solo backend
node scripts/change-ports.js -- 8001

# Ver configuración actual
node scripts/change-ports.js --show

# Regenerar docker-compose.yml
node scripts/change-ports.js --regenerate-docker
```

### Flujo de Trabajo
1. **Cambiar configuración**: `node scripts/change-ports.js 5174 8001`
2. **Reiniciar servicios**:
   ```bash
   # Frontend
   cd frontend && npm run dev
   
   # Backend
   cd backend && python run.py
   ```
3. **Verificar funcionamiento**: Los servicios se ejecutan en los nuevos puertos

## 🎯 **8. Beneficios de esta Estrategia**

### ✅ **Ventajas**
- **Un solo archivo** controla toda la configuración
- **Sincronización automática** entre todos los componentes
- **Compatibilidad** entre Node.js y navegador
- **Flexibilidad** para development y production
- **Escalabilidad** fácil para nuevos servicios
- **Mantenimiento** simplificado

### 🔧 **Casos de Uso**
- **Desarrollo local** con puertos personalizados
- **Entornos múltiples** (dev, staging, prod)
- **Microservicios** con configuración centralizada
- **Docker** con configuración dinámica
- **CI/CD** con configuración automática

## 📋 **9. Implementación en Nuevos Proyectos**

### Paso 1: Crear estructura base
```bash
mkdir mi-proyecto
cd mi-proyecto
mkdir scripts frontend backend
```

### Paso 2: Copiar archivos de configuración
- Copiar `config.json`
- Copiar todos los scripts de `scripts/`
- Adaptar las rutas según la estructura del proyecto

### Paso 3: Adaptar archivos del proyecto
- Actualizar `frontend/vite.config.js`
- Actualizar `frontend/src/services/api.js`
- Actualizar `backend/app/config.py`
- Actualizar `backend/run.py`

### Paso 4: Probar el sistema
```bash
node scripts/change-ports.js --show
node scripts/change-ports.js 3000 5000
```

## 🎉 **Conclusión**

Esta estrategia de configuración centralizada resuelve el problema de mantener múltiples archivos de configuración sincronizados, proporcionando:

- **Simplicidad**: Un comando cambia todo
- **Confiabilidad**: Sincronización automática
- **Flexibilidad**: Funciona con cualquier stack tecnológico
- **Escalabilidad**: Fácil de extender a nuevos servicios

**¡Implementa esta estrategia en tus proyectos y nunca más tendrás problemas de configuración desincronizada!** 🚀


